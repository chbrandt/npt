from .formatters import geojson_2_geodataframe, products_2_geojson, json_2_geojson
from npt.utils import filenames

import json

from . import log

def read(filename):
    """
    Return 'features' from GeoJSON
    """
    with open(filename, 'r') as fp:
        js = json.load(fp)
    #     features = js['features']
    # return features
    return js


def write(gjson_object, geojson_filename):
    """
    Write GeoJSON object to file
    """
    with open(geojson_filename, 'w') as fp:
        json.dump(gjson_object, fp)
    return geojson_filename


def write_feature_json(feature:dict, reference_path_field:str='image_path') -> bool:
    """
    Write feature/metadata next to feature['image_path']
    """
    import json
    try:
        reference_path = feature['properties'][reference_path_field]
        json_filename = filenames.change_extension(reference_path, 'json')
        with open(json_filename, 'w') as fp:
            json.dump(feature, fp)
        return json_filename
    except Exception as err:
        raise err
        return None
