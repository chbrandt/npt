import os

from . import log

from gpt.utils.download import download_file

def _run_geo_feature(geojson_feature, base_path, progressbar=False):
    """
    Download data products (Image, Label) inside 'base_path'

    Inputs:
    * product_feature:
        Feature from GeoJSON from Search/Listing stage
        Field 'image_url' is expected, field 'image_path' will be added
        Field 'label_url' is optional, if present will be download also
    * base_path:
        Base filesystem path (directory) where product will be downloaded
    * progressbar (False):
        If a (tqdm) progress-bar should show download progress
    """
    product_feature = geojson_feature

    assert base_path, "Expected a valid path, got '{}' instead".format(base_path)

    properties = product_feature['properties']
    properties = run_props(properties, base_path, progressbar)
    product_feature['properties'] = properties

    return product_feature

run = _run_geo_feature


def run_props(properties, base_path, progressbar=False):
    properties = properties.copy()

    image_url = properties['image_url']
    image_path = _download(image_url, basepath=base_path, progressbar=progressbar)
    if image_path:
        properties['image_path'] = image_path

    if ('label_url' in properties
        and properties['label_url'] != properties['image_url']):
        label_url = properties['label_url']
        label_path = _download(label_url, basepath=base_path, progressbar=progressbar)
        if label_path:
            properties['label_path'] = label_path

    return properties


def _download(url, basepath, progressbar=False):
    _file = url.split('/')[-1]
    file_path = os.path.join(basepath, _file)
    try:
        _out = download_file(url, filename=file_path, progress_on=progressbar)
    except Exception as err:
        log.error(err)
        return None
    return file_path
