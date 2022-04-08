import os
import rasterio
from pathlib import Path
from . import log

def mosaic(geojson_file, basepath, output, tmpdir):
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
        # Add to mosaic properties/feature the values that are equal across source data
        if len(gdf[p].unique()) == 1:
            val = list(gdf[p].unique())
            properties[p] = val
        else:
            val = None

    properties['id_sources'] = [','.join(list(gdf['id']))]

    ngdf = geopandas.GeoDataFrame(properties, geometry=geometry)
    _rec = ngdf.iloc[0]

    dtime = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    mosaic_filename = (
      "mosaic_"
      f"{_rec['inst'].lower()}_"
      f"{dtime}"_
      f"lon{c_lon}_lat{c_lat}.tif"
    )

    mosaic_path = _mosaic(filenames, basepath=basepath,
                         mosaic_filename=mosaic_filename)

    ngdf['tiff_path'] = [mosaic_path]

    return ngdf


def _mosaic(filenames, basepath, mosaic_filename=None, make_dirs=True):
    if not os.path.isdir(basepath):
        if make_dirs:
            os.makedirs(basepath, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(basepath))
            return None

    if not mosaic_filename:
        mosaic_filename = "mosaic.tif"
    output = Path(basepath) / mosaic_filename
    output = warp(filenames, output.as_posix())
    return output


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
