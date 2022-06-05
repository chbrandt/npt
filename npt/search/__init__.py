"""
Query USGS/ODE API for image data products
"""
from npt import log


def ode(dataset: str, bbox: dict=None, product_id: str = None, match: str = 'intersect', bbox_ref:str='C0'):
    """
    Return GeoDataFrame with found data products as features

    Input:
    - dataset: name of the dataset (see `npt.datasets`)
    - bbox: (opt., see product_id) bounding-box to query overlapping products.
            Dictionary keys: minlat, maxlat, westlon, eastlon;
            Latitude/longitude values range: (-90:90, -180:180)
            If not defined, 'product-id' is expected.
    - product_id : (optional, see bbox) product-id in 'dataset'
            If not defined, 'bbox' is expected.
    - match: how to consider overlapping matching footprints.
             Options are: 'intersect', 'contain'
    - bbox_ref: if 'C0' (default), 'bbox' longitudes are centered at 0 (-180:180),
                if 'C180', 'bbox' longitudes are centered at 180 (0:360).
    """
    from npt.search._ode import ODE

    assert bbox or product_id, "Please, define either 'bbox' or 'product_id'"

    if bbox:
        prods = ODE(dataset).query_bbox(bbox=bbox, match=match, bbox_ref=bbox_ref).parse()
    if product_id:
        if bbox:
            # Not implemented yet: could filter for product-id(s) expression (exact or regex)
            pass
        prods = ODE(dataset).query_pid(product_id=product_id).parse()


    if not prods:
        return None

    return prods.to_dataframe()
