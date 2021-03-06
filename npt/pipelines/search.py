# import os
# import shapely
# import geopandas as gpd

from . import log

from npt import search


def run(bounding_box, dataset_id, output_geojson=None, contains=False):
    """
    Write GeoJSON with products intersecting 'bounding_box'

    Inputs:
    * bounding_box:
        Dictionary with 'minlat','maxlat','westlon','eastlon' keys;
        Longitues range is [0:360] (180 center).
    * dataset_id:
        Datasets identifiers. Options are 'mars/mro/ctx/edr', 'mars/mro/hirise/rdrv11'.
    * output_geojson:
        Filename for the GeoJSON containing found products as Features.
    """
    output_filename = output_geojson
    if not bounding_box:
        return None

    how = 'contain' if contains else 'intersect'
    # ode_result = search.ode.bbox(bounding_box, dataset_id, how)
    # products = search.ode.parse_products(ode_result, search.ode.DESCRIPTORS[dataset_id])
    results = search.product_type(dataset_id, bbox=bounding_box, how=how)
    # results = results.filter(descriptors=DESCRIPTORS_CUSTOM)

    if not products:
        return None

    geojson = results.to_geojson()

    if output_filename:
        # return write_geojson(products, filename=output_filename)
        with open(output_filename, 'w') as fp:
            fp.dump(geojson, fp)

    return geojson


# def write_geojson(products, filename):
#     """
#     Write products to a GeoJSON 'filename'. Return GeoPandas dataframe.
#
#     > Note: This function modifies field 'geometry' from 'products'
#
#     products: list of product records (from search_footprints)
#     filename: GeoJSON filename for the output
#     """
#     assert isinstance(products, list), f"Expected 'products' to be a list. Instead: {products}"
#     assert filename and filename.strip() != '', "Give me a valid filename"
#
#     for prod in products:
#         try:
#             prod['geometry'] = shapely.wkt.loads(prod['geometry'])
#         except TypeError as err:
#             log.info("Error in: ", prod)
#             raise err
#
#     gdf = gpd.GeoDataFrame(products)
#
#     gdf.to_file(filename, driver='GeoJSON')
#     log.info("File '{}' written.".format(filename))
#     return gdf
