from .formatters import geojson_2_geodataframe, products_2_geojson, json_2_geojson

import json

from . import log

def read(filename):
    """
    Return 'features' from GeoJSON
    """
    with open(filename, 'r') as fp:
        js = json.load(fp)
        features = js['features']
    return features
