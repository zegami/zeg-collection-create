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
    '.jpg': JPEG_TYPE,
    '.jpeg': JPEG_TYPE,
    '.png': PNG_TYPE,
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
                      collection_name,
                      collection_description,
                      data_file,
                      image_folders,
                      xslt_file):
    """Create a new collection."""
    collection = client.create_collection(
        collection_name,
        collection_description,
        True)
    reporter("Created collection", level=0)

    with open(data_file, 'rb') as f:
        client.upload_data(collection['dataset_id'], data_file, f)
        reporter(
            "Data file {filename} uploaded",
            level=0,
            filename=data_file
        )
    imageset_ids = dict()
    # create an imageset for each folder
    for directory in image_folders:
        directory_name = get_path_directory_name(directory)
        imageset = api_upload_folder(
            reporter,
            client,
            directory,
            directory_name
        )
        imageset_ids[directory_name] = imageset['id']

    # perform this substitution on the .tsv above if the
    # image filenames are specified in there instead
    with open(xslt_file, 'rb') as f:
        bio = io.BytesIO(
            update_paths(
                client.project,
                imageset_ids,
                f,
                client.api_url,
                image_folders,
            )
        )
        client.upload_zegx(collection['id'], bio)
        reporter("Created zegx template", level=0)


def api_upload_folder(reporter, client, image_folder, imageset_name):
    """Upload all images within a folder to an imageset."""
    imageset = client.create_imageset(imageset_name)
    reporter("Created imageset {name}", level=0, name=imageset_name)
    for filename in os.listdir(image_folder):
        file_path = os.path.join(image_folder, filename)
        # the components being the file name and the extension
        filename_components = os.path.splitext(
            os.path.basename(file_path)
        )
        if len(filename_components) > 1 and \
                filename_components[1] in FILE_TYPES.keys():
            with open(file_path, 'rb') as f:
                try:
                    client.upload_image(
                        imageset['id'],
                        filename_components[0],
                        f,
                        FILE_TYPES[filename_components[1]]
                    )
                    reporter(
                        "Imageset: {id}, uploaded {filename}",
                        level=0,
                        id=imageset['id'],
                        filename=filename_components[0]
                    )
                except requests.exceptions.RequestException as e:
                    reporter(
                        "Imageset: {id}, upload failed for {filename}\n{error}",
                        level=0,
                        id=imageset['id'],
                        filename=filename_components[0],
                        error=e,
                    )
    return imageset


def update_paths(project, imageset_ids, file, api_url, image_folders):
    """Update the paths for all images in the XSLT.

    The URL needs to instead point to the imageset.
    """
    def foldername_replace(matchobj):
        return os.path.join(api_url,
                            "v0/project/{}/imagesets/{}/images/name:{}/data"
                            ).format(
                            project,
                            imageset_ids[matchobj.group(1).decode("utf-8")],
                            matchobj.group(2).decode("utf-8")
                            ).encode()

    directory_names = [get_path_directory_name(folder) for folder in image_folders]
    pat = (r"(" + r'|'.join(directory_names) + r")/(.*?).png").encode()
    updatedfile = re.sub(pat, foldername_replace, file.read())

    with open("test.xslt", 'wb') as testfile:
        testfile.write(updatedfile)

    return updatedfile

def get_path_directory_name(path):
    """Get the directory name for a path."""
    return os.path.split(path)[-1]
