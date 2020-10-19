
"""
Search interface:
- for (products)
- at (ODE)
- by (location)
"""

# @staticmethod
# def query2geojson(bounding_box, dataset_id, geojson_filename):
#     """
#     Write GeoJSON with products intersecting 'bounding_box'
#
#     Inputs:
#     * bounding_box:
#         Dictionary with 'minlat','maxlat','westlon','eastlon' keys;
#         Longitues range is [0:360] (180 center).
#     * dataset_id:
#         Datasets identifiers. Options are 'mro/ctx/edr', 'mro/hirise/rdrv11'.
#     * geojson_filename:
#         Filename for the GeoJSON containing found products as Features.
#     """
#     output_filename = geojson_filename
#     products = Search.query_footprints(bbox=bounding_box,
#                                        dataset=dataset_id)
#     gdf = Search.write_geojson(products, filename=output_filename)
#     return gdf
#
# __call__ = query2geojson

def bbox(bbox, dataset=None,
         provider=None, contains=False,
         target='mars', host=None, instr=None, ptype=None):
    """
    Return list of found products (in dictionaries)

    dataset be like: 'mars/mro/hirise/rdrv11'
    bbox: {'minlat': -0.5, 'maxlat': 0.5, 'westlon': 359.5, 'eastlon': 0.5}
    """
    from npt.pds.ode import ODE

    if provider.lower() != 'ode':
        msg = "'{facility}' not implemented. Check 'npt.interfaces'."
        raise NotImplementedError(msg.format(facility=facility))

    if dataset:
        target,host,instr,ptype = dataset.split('/')

    ode = ODE(target,host,instr,ptype)

    # Interface design
    # ode.search._by(bbox)._parse(schema)
    # ode.search._by(bbox)._for(products)
    # ---

    req = ode.query_bbox(bbox, contains=contains)

    # products = ode.requested_products(req)
    products = ode.read_products(req)

    if products:
        schema = {'meta':None, 'files':None, 'footprints':None}
        products = ode.parse_products(products, schema)
    return products


def write_geojson(products, filename):
    """
    Write products to a GeoJSON 'filename'. Return GeoPandas dataframe.

    > Note: This function modifies field 'geometry' from 'products'

    products: list of product records (from search_footprints)
    filename: GeoJSON filename for the output
    """
    from .utils.io import json_2_geojson
    try:
        json_2_geojson(products, filename)
        return True
    except:
        return False
