import os
from copy import deepcopy
from copy import copy as shallowcopy

from npt import log

from npt.utils.download import download_file


def from_geodataframe(gdf, basepath:str,
                 image_url_field:str='image_url',
                 label_url_field:str='label_url',
                 image_path_field:str='image_path',
                 label_path_field:str='label_path',
                 progressbar:bool=False):
    """
    Download all entries from GeoDataFrame indicated by URLs in the resp. paths
    """
    import json
    gjson_obj = json.loads(gdf.to_json())

    new_gjson = from_geojson(gjson_obj, basepath,
                            image_url_field,
                            label_url_field,
                            image_path_field,
                            label_path_field,
                            progressbar)

    if not new_gjson:
        return None

    new_gdf = gdf.__class__.from_features(new_gjson['features'])
    return new_gdf

from_dataframe = from_geodataframe


def from_geojson(geojson:dict, basepath:str,
                 image_url_field:str='image_url',
                 label_url_field:str='label_url',
                 image_path_field:str='image_path',
                 label_path_field:str='label_path',
                 progressbar:bool=False) -> dict:
    """
    Download all entries (features) in GeoJSON, URLs in the resp. paths given
    """
    features = geojson['features']
    new_features = []
    for feature in features:
        new_feature = from_feature(feature, basepath,
                                    image_url_field,
                                    label_url_field,
                                    image_path_field,
                                    label_path_field,
                                    progressbar)
        assert id(new_feature) != id(feature)
        new_features.append(new_feature)

    new_geojson = shallowcopy(geojson)
    assert id(new_geojson) != id(geojson)
    new_geojson['features'] = new_features

    return new_geojson


#TODO: Add argument "data product type" to define what to download.
def from_feature(feature:dict, basepath:str=None,
                 image_url_field:str='image_url',
                 label_url_field:str='label_url',
                 image_path_field:str='image_path',
                 label_path_field:str='label_path',
                 progressbar:bool=False):
    """
    Download data products (Image, Label) inside 'basepath'
    """
    from ._pds import split_label_from_image
    from ._pds import write_feature_json

    basepath = basepath or '.'

    properties = deepcopy(feature['properties'])
    geometry = deepcopy(feature['geometry'])

    image_url = properties.pop(image_url_field)

    image_path = _download(image_url, basepath=basepath, progressbar=progressbar)
    properties[image_path_field] = image_path

    label_url = None
    if label_url_field in properties:
        label_url = properties.pop(label_url_field)

    if (label_url is not None and label_url != image_url):
        label_path = _download(label_url, basepath=basepath, progressbar=progressbar)
    else:
        label_path = split_label_from_image(image_path)

    properties[label_path_field] = label_path

    # Update metadata set basaed on image Label.
    # FIXME: these MEEO metadata mappings are a bit chaotic
    metaDict = _createLblDict(label_path)
    metaDict.update(_map_meta_meeo(properties))
    properties.update(metaDict)

    new_feature = shallowcopy(feature)
    new_feature['properties'] = properties
    new_feature['geometry'] = geometry

    # Write the image/product respective feature/metadata next to it
    feature_filename = write_feature_json(new_feature)
    log.info("Feature/metadata file '{}' written.".format(feature_filename))

    return new_feature


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


def _createLblDict( filename ):
    """
    filename is a 'LBL' (PDS LBL) filename
    """
    text = open(filename, 'r').read()
    lines = text.splitlines()
    img_header = {}
    for line in lines:
        value = line
        fields = [v.strip() for v in value.split("=")]
        key_value = fields[0]
        fill_value = fields[-1].replace('"',"").rstrip()
        if 'DATA_SET_ID' == key_value:
            # l_datasetId = fill_value.replace("-","_").replace(".","_").split("_")
            # img_header['datasetId'] = "_".join(l_datasetId[0:3:2])
            # img_header['observationMode'] = l_datasetId[4]
            pass

        # elif 'PRODUCT_ID' == key_value:
        #     img_header['idFromProvider'] = fill_value

        elif 'INSTRUMENT_HOST_NAME' == key_value:
            img_header['instrumentHostName'] = fill_value
            # img_header['spacecraftId'] = "".join([s[0].upper() for s in fill_value.split()])

        elif 'INSTRUMENT_NAME' == key_value:
            img_header['instrumentName'] = fill_value

        # elif 'INSTRUMENT_ID' == key_value:
        #     img_header['instrumentId'] = fill_value

        # elif 'TARGET_NAME' == key_value:
        #     img_header['targetName'] = fill_value

        elif 'MISSION_PHASE_NAME' == key_value:
            img_header['missionPhaseName'] = fill_value

        # elif 'PRODUCT_CREATION_TIME' == key_value:
        #     img_header['productCreationTime'] = fill_value

        # elif 'START_TIME' == key_value:
        #     img_header['startTime'] = fill_value.replace(" ", "")

        # elif 'STOP_TIME' == key_value:
        #     img_header['stopTime'] = fill_value.replace(" ", "")


    # img_header['solarDistance'] = ""
    # img_header['solarLongitude'] = ""

    _keys = list(img_header.keys())
    _keys.sort()
    return {k:img_header[k] for k in _keys}

def _map_meta_meeo(props):
    meta = {}
    meta['idFromProvider'] = props['id']
    meta['observationMode'] = props['type']
    meta['instrumentId'] = props['inst']
    meta['spacecraftId'] = props['mission']
    meta['datasetId'] = f"{props['mission']}_{props['inst']}"
    meta['targetName'] = props['Target_name']
    meta['productCreationTime'] = props['Product_creation_time']
    meta['startTime'] = props['UTC_start_time']
    meta['stopTime'] = props['UTC_stop_time']
    return meta
