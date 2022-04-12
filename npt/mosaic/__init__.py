import os
from pathlib import Path

from npt import log
from ..utils import raster
from ..utils.filenames import change_extension, change_dirname, insert_preext


def mosaic(geojson:dict, basepath:str, prefix_output:str="mosaic",
    method:str='merge', scale_factor:float=0.1):
    """
    Make mosaic from files in 'input_geojson' file. Write GeoJSON with mosaic feature.

    Input:
        scale_factor: float
            Between (0:1], define the down-scaling to apply on both axis
    """
    import geopandas
    from datetime import datetime

    _sep = '_'

    # Read the GeoJSON (dict) given as input
    gdf = geopandas.GeoDataFrame.from_features(geojson['features'])
    gdf = gdf.loc[gdf.area.sort_values(ascending=False).index]
    log.info("{:d} features read".format(len(gdf)))

    # Define the list of source images
    filenames = list(gdf['tiff_path'])
    log.debug(f"Sources: {filenames}")

    # Define the final/output geometry (the union of source geometries)
    geometry = [gdf.geometry.unary_union]

    # Define the output properties/metadata
    properties = {}
    for p in gdf.columns:
        # Use fields that have the same value across all sources
        if len(gdf[p].unique()) == 1:
            val = list(gdf[p].unique())
            properties[p] = val
        else:
            val = None

    # Add 'id_sources' for the field of images source IDs as a comma-separated string-list
    properties['id_sources'] = [','.join(list(gdf['id']))]

    # Define a GeoDataFrame/GeoJSON with (one feature of) such metadata
    ngdf = geopandas.GeoDataFrame(properties, geometry=geometry)
    _rec = ngdf.iloc[0]

    # Define name of output file
    c_lon,c_lat = geometry[0].centroid.coords.xy
    c_lon = '{:03d}'.format(int(c_lon[0]))
    c_lat = '{:03d}'.format(int(c_lat[0]))

    dtime = datetime.now().strftime("%Y%m%dT%H%M%S%f")

    mosaic_filename = _sep.join([
                                f"{prefix_output}",
                                f"{_rec['inst'].lower()}",
                                f"{dtime}",
                                f"lon{c_lon}lat{c_lat}.tif"
                                ])

    mosaic_path = _mosaic(filenames, basepath=basepath,
                          mosaic_filename=mosaic_filename,
                          method=method)

    assert mosaic_path

    ngdf['tiff_kbytes'] = [int(os.path.getsize(mosaic_path)/1000)]
    ngdf['tiff_path'] = [mosaic_path]

    return ngdf


def _mosaic(filenames, basepath, mosaic_filename=None, make_dirs=True,
            method='merge', scale_factor=0.1):
    """
    * method options: virtual, warp, merge
    """
    from npt.utils.raster import warp, merge, virtual

    # Rescale?
    assert 0 < scale_factor <= 1, "Scale-factor should be between (0:1]"
    if scale_factor < 1:
        filenames_rescaled = []
        for filename in filenames:
            filename_resc = insert_preext(change_dirname(filename, basepath), 'rescaled')
            log.debug(f"Rescaled filename to-write: {filename_resc}")
            try:
                filename_resc = raster.rescale(filename, filename_resc, scale_factor)
            except Exception as err:
                log.error(f"Failed to rescale (by {scale_factor}) file: {filename}")
                log.error(str(err))
                continue

            filenames_rescaled.append(filename_resc)

        filenames = filenames_rescaled[:]

    assert len(filenames), "No filenames/source to mosaic(?)!"

    if not os.path.isdir(basepath):
        if make_dirs:
            os.makedirs(basepath, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(basepath))
            return None

    if not mosaic_filename:
        mosaic_filename = "mosaic.tif"
    output = Path(basepath) / mosaic_filename
    output = output.as_posix()

    if method == 'virtual':
        output = virtual(filenames, output)
    elif method == 'warp':
        output = warp(filenames, output)
    else:
        output = merge(filenames, output)

    return output
