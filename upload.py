from zegami_kanjidic import api
import os
import io
import re

TSV_NAME = 'osidata-new.tsv'
XSLT_NAME = 'osizeg-upload.xslt'
IMAGE_FOLDERS = ["logos"]
API_URL = 'https://app.zegami.com/api/'
PROJECT = 'project-code-here'
TOKEN = 'your-token-here'



zegs = True

COLLECTION_TITLE = 'OSI collection'
COLLECTION_DESCRIPTION = 'collection-description'
if not zegs and len(IMAGE_FOLDERS) > 1:
    raise(Exception("Only one image folder allowed for non-zeg collections"))


def update_paths(project, imageset_ids, file):

    def foldername_replace(matchobj):
        return os.path.join(API_URL,
                            "v0/project/{}/imagesets/{}/images/name:{}/data"
                            ).format(
                            project,
                            imageset_ids[matchobj.group(1).decode("utf-8")],
                            matchobj.group(2).decode("utf-8")
                            ).encode()

    pat = (r"(" + r'|'.join(IMAGE_FOLDERS) + r")/(.*?).png").encode()
    updatedfile = re.sub(pat, foldername_replace, file.read())

    with open("test.xslt", 'wb') as testfile:
        testfile.write(updatedfile)

    return updatedfile


def main():
    client = api.Client(API_URL, PROJECT, TOKEN)

    collection = client.create_collection(COLLECTION_TITLE,
                                          COLLECTION_DESCRIPTION, zegs)
    with open(TSV_NAME, 'rb') as f:
        client.upload_data(collection['dataset_id'], TSV_NAME, f)
    imageset_ids = dict()
    for foldername in IMAGE_FOLDERS:
        if zegs:
            imageset = client.create_imageset(foldername)
            imageset_ids[foldername] = imageset_id = imageset['id']
        else:
            imageset_id = collection['imageset_id']
        for filename in os.listdir(foldername):
            with open(os.path.join(foldername, filename), 'rb') as f:
                client.upload_png(imageset_id, filename.replace('.png', ''), f)

    if zegs:
        # perform this substitution on the .tsv above if the
        # image filenames are specified in there instead
        with open(XSLT_NAME, 'rb') as f:
            bio = io.BytesIO(update_paths(client.project, imageset_ids, f))

        client.upload_zegx(collection['id'], bio)
    else:
        join_ds = client.create_join("Join for " + collection["name"],
                                     collection['imageset_id'],
                                     collection['dataset_id'],
                                     id_field='Company')
        collection['join_dataset_id'] = join_ds['id']
        client.update_collection(collection['id'], collection)


if __name__ == "__main__":
    main()
