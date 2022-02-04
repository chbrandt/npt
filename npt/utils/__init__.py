import json

from npt import log

from . import tmpdir


def read_geojson(filename):
    """
    Return JSON object from GeoJSON
    """
    with open(filename, 'r') as fp:
        js = json.load(fp)
    return js
