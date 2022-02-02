"""
Query USGS/ODE API for image data products
"""
from npt import log


def ode(dataset: str, bbox: dict, match: str = 'intersect'):
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

    prods = ODE(dataset).query(bbox=bbox, match=match).parse().to_dataframe()

    return prods



# def run(bounding_box, dataset_id, output_geojson=None, contains=False, how='intersect'):
#     """
#     Write GeoJSON with products intersecting 'bounding_box'
#
#     Inputs:
#     * bounding_box:
#         Dictionary with 'minlat','maxlat','westlon','eastlon' keys;
#         Longitues range is [0:360] (180 center).
#     * dataset_id:
#         Datasets identifiers. Options are 'mro/ctx/edr', 'mro/hirise/rdrv11'.
#     * output_geojson:
#         Filename for the GeoJSON containing found products as Features.
#     """
#     output_filename = output_geojson
#     if contains:
#         how = 'contains'
#     contains = True if 'contain' in how else False
#     if not bounding_box:
#         return None
#     products = query_footprints(bbox=bounding_box, dataset=dataset_id, contains=contains)
#     if not products:
#         return None
#     if output_filename:
#         gdf = write_geojson(products, filename=output_filename)
#         return gdf
#     return products
