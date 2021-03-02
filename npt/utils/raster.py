import os
import rasterio

from . import log


def warp(fileinname, fileoutname, dst_crs='EPSG:4326'):
    import numpy as np
    from rasterio.warp import calculate_default_transform, reproject, Resampling

    with rasterio.open(fileinname) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(fileoutname, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)
    print('Done.')
    return


def to_tiff(filename_in, filename_out, format_in, cog=False):
    """
    For accepted formats (in): https://gdal.org/drivers/raster/index.html
    """
    format_out = 'GTiff'
    format_in = 'ISIS3' if format_in == 'ISIS' else format_in
    filename_out_tmp = filename_out + '.tmp' if cog else None
    try:
        src = rasterio.open(filename_in, 'r', driver=format_in)
        data = src.read()
        params = src.meta
        params['driver'] = format_out
        if cog:
            dst = rasterio.open(filename_out_tmp, 'w', **params)
        else:
            assert filename_out_tmp is None
            dst = rasterio.open(filename_out, 'w', **params)
        dst.write(data)
        src.close()
        dst.close()
    except Exception as err:
        raise err
        return None
    if cog:
        res = tiff2cog(filename_out_tmp, filename_out)
        # os.remove(filename_out_tmp)
    else:
        assert filename_out_tmp is None
    return filename_out

def tiff2cog(filename_in, filename_out):
    """
    Transform GeoTIFF in COG
    """
    from npt.isis import sh
    gdal_cmd = sh.wrap('gdal_translate')
    cog_args = """
        -co TILED=YES -co COMPRESS=LZW -co BLOCKXSIZE=512 -co BLOCKYSIZE=512
        -co COPY_SRC_OVERVIEWS=YES --config  GDAL_TIFF_OVR_BLOCKSIZE 512
    """.split()
    res = gdal_cmd(filename_in, filename_out, cog_args)
