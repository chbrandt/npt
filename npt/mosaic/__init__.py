import os
import rasterio
from pathlib import Path
from . import log

def run(geojson_file, basepath, output, tmpdir):
    """
    Make mosaic from files in 'input_geojson' file. Write GeoJSON with mosaic feature.
    """
    import geopandas
    from datetime import datetime

    gdf = geopandas.read_file(geojson_file)
    log.info("{:d} features read".format(len(gdf)))

    filenames = list(gdf['tiff_path'])

    geometry = [gdf.geometry.unary_union]
    c_lon,c_lat = geometry[0].centroid.coords.xy
    c_lon = '{:03d}'.format(int(c_lon[0]))
    c_lat = '{:03d}'.format(int(c_lat[0]))
    # print("GEOMETRY CENTROID:", c_lon, c_lat)

    properties = {}
    for p in gdf.columns:
        if len(gdf[p].unique()) == 1:
            val = list(gdf[p].unique())
        else:
            val = None
        if val:
            properties[p] = val
    properties['mosaic_sources'] = [','.join(list(gdf['id']))]

    ngdf = geopandas.GeoDataFrame(properties, geometry=geometry)
    _rec = ngdf.iloc[0]

    dtime = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    mosaic_filename = (
      "mosaic_"
      f"{_rec['inst'].lower()}_"
      f"{dtime}"_
      f"lon{c_lon}_lat{c_lat}.tif"
    )

    mosaic_path = mosaic(filenames, output_path=basepath,
                                mosaic_filename=mosaic_filename)

    ngdf['tiff_path'] = [mosaic_path]

    if output:
        # json_2_geojson(products, filename=output)
        ngdf.to_file(output, driver='GeoJSON')
    else:
        import json
        # click.echo(json.dumps(products, indent=2))
        return ngdf.to_json(indent=2)


def mosaic(filenames, output_path, mosaic_filename=None, make_dirs=True):
    if not os.path.isdir(output_path):
        if make_dirs:
            os.makedirs(output_path, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(output_path))
            return None

    if not mosaic_filename:
        mosaic_filename = "mosaic.tif"
    output = Path(output_path) / mosaic_filename
    # output = raster.mosaic(filenames, output.as_posix())
    output = warp(filenames, output.as_posix())
    return output

# """
# Mosaic related Functions
#
# The basic idea of this mosaic'ing module is to offer a function to handle the
# list of images to mosaic from a geojson file (which is the media used by MEEO).
# """
# from npt.utils import geojson
#
# def run(geojson_filename):
#     """
#     Create mosaic from given images. Return geojson for resulting mosaic.
#
#     Input:
#         * geojson_filename : string
#
#     Output:
#         GeoJSON (object)
#     """
#     gjs = geojson.read(geojson_filename)
#
#     features = geojson.copy_features(gjs)
#     new_features = _run_features(features)
#     assert len(new_features) == 1, """
#         Resulting number features from a mosaic is expected to be '1',
#         instead got {len(new_features)}
#         """
#
#     geojson_out = None
#     return geojson_out
#
# from_geojson = run
#
#
# def _run_features(features: list) -> list:
#     """
#     Input:
#         * features : list
#             List of geojson features
#     """
#     # because mosaic processing is processed in batch (all source "together"),
#     # and also because the input geojson/features-list can contain image/data
#     # from different datasets (i.e, product_types), we first want to go
#     # through each and all of them and organize after the datasets, in lists also.
#     def _groupby_dataset(features: list) -> dict:
#         """
#         Return dictionary if list of features after each dataset/product_type
#         """
#         data_sets = {}
#         for feature in features:
#             properties = feature['properties']
#             target = properties['targetName']
#             mission = properties['mission']
#             instrument = properties['instrumentId']
#             product_type = properties['observationMode']
#             datasetId = f"{target}/{mission}/{instrument}/{product_type}".lower()
#             data_sets[datasetId] = data_sets.get(datasetId, []) + [feature]
#         return data_sets
#
#     data_sets = _groupby_dataset(features)
#     log.debug(f"Datasets/product-types involved in this mosaic: {data_sets.keys()}")
#
#     for d_id, features in data_sets.items():
#         if d_id == 'mars/mro/ctx/edr':
#             mosaic_ctx(features)
#     # properties = _run_props(properties, output_path, projection, tmpdir, datasetId)
#     # feature['properties'] = properties
#     # pass
#     assert None
#
#
# def mosaic_ctx(features: list, engine='isis'):
#     """
#     Input:
#         - features : list of geo-features
#         Each feature contain in properties 'image_path' (isis) or 'tiff_path' (gdal)
#         - engine : string
#         Options are ['isis','gdal']
#     """
#     if engine == 'isis':
#         from npt.isis.mosaic import mosaic
#         path_field = 'image_path'
#         ext = 'cub'
#     else:
#         assert engine == 'gdal'
#         from npt.gdal.mosaic import mosaic
#         path_field = 'tiff_path'
#         ext = 'tif'
#
#     # _pf = 'properties'
#     # input_filenames = [ f[_p][path_field] for f in features ]
#     # output_filename = '.'.join('mosaic',ext)
#
#     import geopandas
#     gdf = geopandas.GeoDataFrame.from_features(features)
#     input_filenames = list(gdf[path_field])
#
#     output_filename = mosaic(input_filenames, output_filename)
#     if not output_filename:
#         return None# import os
def from_features(features, files_field='tiff_path',
                    output_path=None, tmpdir=None, make_dirs=True):
    # # Create a temp dir for the processing
    # if tmpdir and not os.path.isdir(tmpdir):
    #     if make_dirs:
    #         os.makedirs(tmpdir, exist_ok=True)
    #     else:
    #         print("Path '{}' does not exist.".format(tmpdir))
    #         return None
    #
    # if tmpdir:
    #     assert os.path.isdir(tmpdir), """Given tmpdir '{}' does not exist""".format(tmpdir)
    #     tempfile.tempdir = tmpdir

    if output_path and not os.path.isdir(output_path):
        if make_dirs:
            os.makedirs(output_path, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(output_path))
            return None

    assert os.path.isdir(output_path), """Given output_path '{}' does not exist""".format(output_path)

    # try:
    #     tmpdir = tempfile.mkdtemp(prefix='neanias_')
    # except:
    #     log.error("Temporary directory ('{}') could not be created.".format(tmpdir))
    #     raise err
    # else:
    #     log.info("Temp dir: '{}'".format(tmpdir))

    filenames = [f['properties'][files_field] for f in features]
    assert filenames
    output = Path(output_path) / f'mosaic_{len(filenames)}.tif'
    # mosaic = merge(filenames, output=output)
    mosaic = warp(filenames, output=output.as_posix())
    return mosaic


def merge(filenames, output):
    """
    Return filename of merged 'filenames' GeoTIFFs

    Input:
        filenames : list
            List of filenames to merge
        output : string
            Mosaic filename
    """
    from rasterio import merge

    with rasterio.open(filenames[0]) as src:
        meta = src.meta.copy()

    # The merge function returns a single array and the affine transform info
    arr, out_trans = merge.merge(filenames)

    meta.update({
        "driver": "GTiff",
        "height": arr.shape[1],
        "width": arr.shape[2],
        "transform": out_trans
    })

    # Write the mosaic raster to disk
    with rasterio.open(output, "w", **meta) as dest:
        dest.write(arr)

    return output


def warp(filenames, output):
    """
    Return filename of merged 'filenames' GeoTIFFs

    Input:
        filenames : list
            List of filenames to merge
        output : string
            Mosaic filename
    """
    from osgeo import gdal

    # The merge function returns a single array and the affine transform info
    gdal.Warp(output, filenames, format="GTiff",
              options=["COMPRESS=LZW", "TILED=YES"])

    return output
