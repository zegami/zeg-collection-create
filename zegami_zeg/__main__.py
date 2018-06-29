# Copyright 2017 Zegami Ltd

__doc__ = """Command line script to create a Zeg based collection."""

import argparse
import getpass
import sys
import yaml

from . import (
    api,
    auth,
    run,
)


def parse_args(argv):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(argv[0], description=__doc__)
    parser.add_argument(
        "--collection",
        help="Collection details in YAML format",
    )
    parser.add_argument(
        "--project",
        help="Project id to make collection in",
    )
    parser.add_argument(
        "--api-url",
        default="https://app.zegami.com/api/",
        help="Zegami api endpoint",
    )
    parser.add_argument(
        "--oauth-url",
        default="https://app.zegami.com/oauth/token/",
        help="Zegami authentication endpoint",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="show progress",
    )
    args = parser.parse_args(argv[1:])

    return args


def main(argv):
    """Application entry point."""
    args = parse_args(argv)
    reporter = run.Reporter(sys.stderr, args.verbose)

    # authenticate user
    # get details
    username = raw_input('Email: ')
    password = getpass.getpass('Password: ')
    auth_client = auth.AuthClient(args.oauth_url)
    auth_client.set_name_pass(username, password)
    token = auth_client.get_user_token()

    if token is None:
        sys.stderr.write("Failed to sign in!")
        return 1

    reporter("User successfully signed in.", level=0)

    # parse yaml collection configuration
    with open(args.collection, 'r') as stream:
        try:
            yargs = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    if args.api_url is None:
        client = None
    else:
        client = api.Client(args.api_url, args.project, token)
    try:
        run.create_collection(
            reporter,
            client,
            auth_client,
            yargs['collection_name'],
            yargs['collection_description']
                if 'collection_description' in yargs else None,
            yargs['data_file'],
            yargs['image_folders']
                if type(yargs['image_folders']) is list else [],
            yargs['xslt_file'] if yargs['zegs'] else None,
            yargs['columns_file']
                if 'columns_file' in yargs else None,
            yargs['zegs'],
            dynamic_custom_options=yargs['dynamic_custom_options']
                if 'dynamic_custom_options' in yargs else None,
            image_column=yargs['image_column']
                if 'image_column' in yargs else None,
            path_replace=yargs['path_replace']
                if 'path_replace' in yargs else None
        )
    except (EnvironmentError, ValueError) as e:
        sys.stderr.write("error: {}\n".format(e))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
