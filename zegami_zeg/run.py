# Copyright 2017 Zegami Ltd

"""Core logic for generating a Zeg collection."""

from __future__ import absolute_import

import errno
import io
import os
import re
import requests


PNG_TYPE = "image/png"
JPEG_TYPE = "image/jpeg"
FILE_TYPES = {
    'jpg': JPEG_TYPE,
    'jpeg': JPEG_TYPE,
    'png': PNG_TYPE,
}


def _ensure_dir(dirname):
    try:
        os.mkdir(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


class Reporter(object):
    """Simplistic output to a stream with verbosity support."""

    def __init__(self, stream, verbosity):
        """Init."""
        self._stream = stream
        self.level = verbosity

    def __call__(self, format_string, level=1, **kwargs):
        """Call."""
        if self.level >= level:
            self._stream.write(format_string.format(**kwargs) + "\n")
            self._stream.flush()

    def show_nth(self, n, step=(1 << 10)):
        """``True`` if item in sequence should be reported based on level."""
        if not self.level:
            return False
        factor = step >> (self.level << 1)
        if not factor:
            return True
        return not n % factor


def create_collection(reporter,
                      client,
                      auth_client,
                      collection_name,
                      collection_description,
                      data_file,
                      image_folders,
                      xslt_file,
                      columns_file,
                      zegs,
                      dynamic_custom_options=None,
                      image_column='id',
                      path_replace=None):
    """Create a new collection."""
    collection = client.create_collection(
        collection_name,
        collection_description,
        zegs)

    reporter("Created collection " + collection['dataset_id'], level=0)

    with open(data_file, 'rb') as f:
        client.upload_data(collection['dataset_id'], data_file, f)
        reporter(
            "Data file {filename} uploaded",
            level=0,
            filename=data_file
        )
    imageset_ids = dict()
    if zegs:
    # create an imageset for each folder
        for directory in image_folders:
            directory_name = get_path_directory_name(directory)
            imageset_ids[directory_name] = api_upload_folder(
                    reporter,
                    client,
                    auth_client,
                    directory,
                    directory_name,
                    zegs
            )
        # perform this substitution on the .tsv above if the
        # image filenames are specified in there instead
        with open(xslt_file, 'rb') as f:
            text = f.read()
            if path_replace is not None:
                text = update_paths(
                    client.project,
                    imageset_ids,
                    text,
                    client.api_url,
                    image_folders,
                )

            bio = io.BytesIO(text)
            with open('test.xslt', 'wb') as wf:
                wf.write(text)
            if dynamic_custom_options: collection['dynamic_custom_options'] = dynamic_custom_options 
            collection['related_imageset_ids'] = [value for key, value in imageset_ids.items()]
            client.update_collection(collection['id'], collection)
            client.upload_zegx(collection['id'], bio)
            reporter("Created zegx template", level=0)
    else:
        source={"deepzoom": {"midlevel": 10, "optimize": 'true', "overlap": 1, "quality": 95}}
        info = {"source": source}
        client.update_imageset(collection['dz_imageset_id'], info=info)

        imageset_ids[get_path_directory_name(image_folders[0])] = api_upload_folder(
                reporter,
                client,
                auth_client,
                image_folders[0],
                get_path_directory_name(image_folders[0]),
                zegs,
                existing_imageset_id=collection['imageset_id']
        )
        join_ds = client.create_join("Join for " + collection['name'],
                                     imageset_ids[get_path_directory_name(image_folders[0])],
                                     collection['dataset_id'],
                                     join_column=image_column)
        collection['join_dataset_id'] = join_ds['id']
        reporter("Joined images and data", level=0)
        client.update_collection(collection['id'], collection)


    # upload a json with the column schema
    if columns_file is not None:
        with open(columns_file, 'rb') as f:
            client.set_columns(f.read(), collection['dataset_id'])


def api_upload_folder(reporter, client, auth_client, image_folder, imageset_name, zegs, existing_imageset_id=None):
    if existing_imageset_id:
        imageset_id = existing_imageset_id
    else:
        reporter("Creating imageset", level=0)
        imageset = client.create_imageset(imageset_name)
        imageset_id = imageset['id']
        reporter("Created imageset {name}", level=0, name=imageset_name)

    """Upload all images within a folder to an imageset."""
    for filename in os.listdir(image_folder):
        file_path = os.path.join(image_folder, filename)
        # the components being the file name and the extension
        filename_components = os.path.basename(file_path).rsplit('.', 1)
        if len(filename_components) > 1 and \
                filename_components[1].lower() in FILE_TYPES.keys():
            with open(file_path, 'rb') as f:
                i = 3
                while i > 0:
                    try:
                        client.upload_image(
                            imageset_id,
                            filename_components[0],
                            f,
                            FILE_TYPES[filename_components[1].lower()]
                        )
                        reporter(
                            "Imageset: {id}, uploaded {filename}",
                            level=0,
                            id=imageset_id,
                            filename=filename_components[0]
                        )
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 401:
                            reporter("Requesting new token...", level=0)
                            client.update_token(auth_client.get_user_token())
                        i -= 1
                        reporter(str(e))
                        continue
                    except requests.exceptions.RequestException as e:
                        reporter(
                            "Imageset: {id}, upload failed for {filename}\n{error}",
                            level=0,
                            id=imageset_id,
                            filename=filename_components[0],
                            error=e,
                        )
                    break


    return imageset_id


def update_paths(project, imageset_ids, text, api_url, image_folders):
    """Update the paths for all images in the XSLT.

    The URL needs to instead point to the imageset.
    """
    def foldername_replace(matchobj):
        return (api_url + "v0/project/{}/imagesets/{}/images/name:{}/data\""
                            ).format(
                            project,
                            imageset_ids[matchobj.group(1).decode("utf-8")],
                            matchobj.group(2).decode("utf-8")
                            ).encode()

    directory_names = [get_path_directory_name(folder) for folder in image_folders]
    pat = (r"({})/(.*?)(\.)?({})?\"").format(
                  r'|'.join(directory_names),
                  r'|'.join(FILE_TYPES.keys())
            ).encode()
    updatedfile = re.sub(pat, foldername_replace, text)

    with open("test.xslt", 'wb') as testfile:
        testfile.write(updatedfile)

    return updatedfile

def get_path_directory_name(path):
    """Get the directory name for a path."""
    return os.path.split(path)[-1]
