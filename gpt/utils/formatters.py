import geopandas as gpd
import shapely

from .bbox import string_2_dict as bbox_string_2_dict

from . import log

def geojson_2_geodataframe(records):
    assert isinstance(records, list), "Expected a list [{}], instead got {}".format(type(records))
    for rec in records:
        geom = rec['geometry']
        if isinstance(geom, str):
            try:
                # rec['geometry'] = shapely.wkt.loads(rec['geometry'])
                geom = shapely.wkt.loads(geom)
            except Exception as err:
                log.error(err)
                raise err
        else:
            try:
                geom = shapely.geometry.asShape(geom)
            except Exception as err:
                log.error(err)
                raise err
        rec['geometry'] = geom
    gdf = gpd.GeoDataFrame(records)
    return gdf


def products_2_geojson(products, filename):
    """
    Write products to a GeoJSON 'filename'. Return GeoPandas dataframe.

    > Note: This function modifies field 'geometry' from 'products'

    products: list of product records (from search_footprints)
    filename: GeoJSON filename for the output
    """

    assert isinstance(products, list), "Expected 'products' to be a list"
    assert filename and filename.strip() != '', "Give me a valid filename"

    gdf = geojson_2_geodataframe(products)

    gdf.to_file(filename, driver='GeoJSON')
    print("File '{}' written.".format(filename))
    return

json_2_geojson = products_2_geojson
