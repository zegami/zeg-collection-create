# Copyright 2017 Zegami Ltd

"""API client for talking to Zegami cloud version."""

from __future__ import absolute_import

from . import (
    http,
)


# Some mimetypes for file upload
TSV_TYPE = "text/tab-separated-values"
XSLT_TYPE = "application/xml"


class Client(object):
    """HTTP client for interacting with the Zegami api."""

    def __init__(self, api_url, project, token):
        """Initialise client."""
        self.api_url = api_url
        self.project = project
        self.token = token
        auth = http.TokenEndpointAuth(api_url, token)
        self.session = http.make_session(auth)

    def update_token(self, token):
        self.token = token
        auth = http.TokenEndpointAuth(self.api_url, self.token)
        self.session = http.make_session(auth)

    def create_collection(self, name, description=None, dynamic=False):
        """Create a new collection."""
        url = "{}v0/project/{}/collections/".format(self.api_url, self.project)
        info = {"name": name, "dynamic": dynamic}
        if description is not None:
            info["description"] = description
        else:
            info["description"] = ""
        response_json = http.post_json(self.session, url, info)
        return response_json['collection']

    def update_collection(self, coll_id, info):
        """Update an existing collection."""
        url = "{}v0/project/{}/collections/{}".format(
            self.api_url, self.project, coll_id)
        response_json = http.put_json(self.session, url, info)
        return response_json['collection']

    def create_imageset(self, name, source=None):
        """Create a new Imageset."""
        url = "{}v0/project/{}/imagesets/".format(self.api_url, self.project)
        info = {"name": name}
        if source is not None:
            info["source"] = source
        response_json = http.post_json(self.session, url, info)
        return response_json['imageset']

    def create_join(self, name, imageset_id, dataset_id, join_column="id"):
        """Join an existing imageset to a dataset."""
        url = "{}v0/project/{}/datasets/".format(
            self.api_url, self.project)
        info = {
            "name": name,
            "source": {
                "imageset_id": imageset_id,
                "dataset_id": dataset_id,
                "imageset_name_join_to_dataset": {
                    "dataset_column": join_column},
            }
        }
        response_json = http.post_json(self.session, url, info)
        return response_json["dataset"]

    def upload_data(self, dataset_id, name, file):
        """Upload a data file."""
        url = "{}v0/project/{}/datasets/{}/file".format(
            self.api_url, self.project, dataset_id)
        response_json = http.post_file(self.session, url, name, file, TSV_TYPE)
        return response_json

    def upload_image(self, imageset_id, name, file, mime_type):
        """Upload an image."""
        url = "{}v0/project/{}/imagesets/{}/images".format(
            self.api_url, self.project, imageset_id)
        response_json = http.post_file(
            self.session,
            url,
            name,
            file,
            mime_type)
        return response_json

    def update_imageset(self, imageset_id,  info):
        url = "{}v0/project/{}/imagesets/{}".format(
                self.api_url, self.project, imageset_id)
        response_json = http.get_json(self.session, url)['imageset']
        response_json.update(info)
        final_json = http.put_json(self.session, url, response_json)
        return final_json

    def upload_zegx(self, collection_id, file):
        """Upload an XSLT."""
        url = "{}v0/project/{}/collections/{}/zegx".format(
            self.api_url, self.project, collection_id)
        response_json = http.put_file(self.session, url, file, XSLT_TYPE)
        return response_json

    def set_columns(self, dataset_id, columns):
        url = "{}v0/project/{}/datasets/{}/columns".format(
            self.api_url, self.project, dataset_id)
        response_json = http.put_json(self.session, url, columns)
        return response_json
