# Create Zeg collection
API client for creating Zegami collections based on Zegs (dynamic databound tiles).

## Creating a collection
To create a collection a configuration YAML file needs to be specified as well as the Zegami project identifier.

The project identifier can be found by signing into Zegami and copying it from the URL, which is in the format `https://app.zegami.com/p/<project id>/c/...`

```
python upload.py --collection <path to a collection yaml file> --project <a zegami project id>
```

## Collection configuration YAML
A YAML settings file is used to configure the collection detalis like the name and Zeg location.

```
# The name of the collection
collection_name: Collection Name
# The collection description, not required
collection_description: Description
# A list of folders containing images (if any)
image_folders:
  - images
# Path to the data file for the collection. Can be .csv, .tsv or .xlsx
data_file: path to .tsv file
# Path to the XSLT to generate an SVG image once data bound to a row
xslt_file: path to the .xslt file
```