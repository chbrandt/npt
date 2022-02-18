"""
Query USGS/ODE API for image data products
"""
from npt import log


def ode(dataset: str, bbox: dict, match: str = 'intersect', bbox_ref:str='C0'):
    """
    Return GeoDataFrame with found data products as features

    Input:
    - dataset: name of the dataset (see `npt.datasets`)
    - bbox: bounding-box to query overlapping products.
            Dictionary keys: minlat, maxlat, westlon, eastlon;
            Latitude/longitude values range: (-90:90, -180:180)
    - match: how to consider overlapping matching footprints.
             Options are: 'intersect', 'contain'
    - filter: Not implemented yet.
    """
    from npt.search._ode import ODE

    prods = ODE(dataset).query(bbox=bbox, match=match, bbox_ref=bbox_ref).parse()

    if not prods:
        return None

    return prods.to_dataframe()
