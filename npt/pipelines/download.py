import os
import subprocess

from . import log

from npt.utils.download import download_file

#TODO: Add argument "data product type" to define what to download.
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

    if 'label_path' in properties:
        assert 'label_url' in properties
        metaDict = createLblDict(properties['label_path'])
    else:
        metaDict = createImgDict(properties['image_path'])

    properties.update(metaDict)
    return properties


def _download(url, basepath, progressbar=False):
    _file = url.split('/')[-1]
    file_path = os.path.join(basepath, _file)
    #TODO: check if file_path is here already, if so, skip downloading
    try:
        _out = download_file(url, filename=file_path, progress_on=progressbar)
    except Exception as err:
        log.error(err)
        return None
    return file_path


def createLblDict( filename ):
    """
    filename is a 'LBL' (PDS LBL) filename
    """
    text = open(filename, 'r').read()
    return _parseLbl(text)


def createImgDict( filename ):
    """
    filename is a 'IMG' (PDS Image) filename
    """
    cmd = "awk '{print $0; if($0 ~ /^END/){if($1 !~ /END_/){exit}}}' %s" % filename
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            universal_newlines=True, shell=True)
    values_txt, err = p.communicate()
    return _parseLbl(values_txt)


def _parseLbl(values_txt):
    lines = values_txt.splitlines()
    img_header = {}
    for line in lines:
        value = line
        fields = [v.strip() for v in value.split("=")]
        key_value = fields[0]
        fill_value = fields[-1].replace('"',"").rstrip()
        if 'DATA_SET_ID' == key_value:
            l_datasetId = fill_value.replace("-","_").replace(".","_").split("_")
            img_header['datasetId'] = "_".join(l_datasetId[0:3:2])
            img_header['observationMode'] = l_datasetId[4]

        elif 'PRODUCT_ID' == key_value:
            img_header['idFromProvider'] = fill_value

        elif 'INSTRUMENT_HOST_NAME' == key_value:
            img_header['instrumentHostName'] = fill_value
            img_header['spacecraftId'] = "".join([s[0].upper() for s in fill_value.split()])

        elif 'INSTRUMENT_NAME' == key_value:
            img_header['instrumentName'] = fill_value

        elif 'INSTRUMENT_ID' == key_value:
            img_header['instrumentId'] = fill_value

        elif 'TARGET_NAME' == key_value:
            img_header['targetName'] = fill_value

        elif 'MISSION_PHASE_NAME' == key_value:
            img_header['missionPhaseName'] = fill_value

        elif 'PRODUCT_CREATION_TIME' == key_value:
            img_header['productCreationTime'] = fill_value

        elif 'START_TIME' == key_value:
            img_header['startTime'] = fill_value.replace(" ", "")

        elif 'STOP_TIME' == key_value:
            img_header['stopTime'] = fill_value.replace(" ", "")


    img_header['solarDistance'] = ""
    img_header['solarLongitude'] = ""

    _keys = list(img_header.keys())
    _keys.sort()
    return {k:img_header[k] for k in _keys}
