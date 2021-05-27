import geopandas as gpd
import shapely

from .bbox import string_2_dict as bbox_string_2_dict

from . import log

# === Inspect functions
# ref: https://fabianlee.org/2019/09/22/python-using-a-custom-decorator-to-inspect-function-arguments/
#
import functools
import inspect

def logintrospect(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inspect_decorator(func, args, kwargs)
        result = func(*args, **kwargs)
        print("-return " + str(result))
        return result
    return wrapper


def inspect_decorator(func,args,kwargs):
  funcname = func.__name__
  print("function {}()".format(funcname))

  # get description of function params expected
  argspec = inspect.getargspec(func)

  # go through each position based argument
  counter = 0
  if argspec.args and type(argspec.args is list):
    for arg in args:
      # when you run past the formal positional arguments
      try:
        print("*" + str(argspec.args[counter]) + " = " + str(arg))
        counter+=1
      except IndexError as e:
        # then fallback to using the positional varargs name
        if argspec.varargs:
          varargsname = argspec.varargs
          print("*" + varargsname + " = " + str(arg))
        pass

  # finally show the named varargs
  if argspec.keywords:
    kwargsname = argspec.keywords
    for k,v in kwargs.items():
      print("**" + kwargsname + " " + k + " = " + str(v))

# ==========

@logintrospect
def geojson_2_geodataframe(records):
    assert isinstance(records, list), "Expected a list [{}], instead got {}".format(type(records))
    gpdrecs = []
    for rec in records:
        geom = rec['geometry']
        if isinstance(geom, str):
            try:
                # rec['geometry'] = shapely.wkt.loads(rec['geometry'])
                geom = shapely.wkt.loads(geom)
            except Exception as err:
                log.error(err)
                raise err
        elif geom is None:
            pass
        else:
            try:
                geom = shapely.geometry.asShape(geom)
            except Exception as err:
                log.error(err)
                raise err
        gpdrec = rec['properties']
        gpdrec['geometry'] = geom
        gpdrecs.append(gpdrec)
    gdf = gpd.GeoDataFrame(gpdrecs)
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
