import os
import rasterio

from . import log


def to_tiff(filename_in, filename_out, format_in, cog=False):
    """
    For accepted formats (in): https://gdal.org/drivers/raster/index.html
    """
    format_out = 'GTiff'
    format_in = 'ISIS3' if format_in == 'ISIS' else format_in

    try:
        if cog:
            res = tiff2cog(filename_in, filename_out)
        else:
            src = rasterio.open(filename_in, 'r', driver=format_in)
            data = src.read()
            params = src.meta
            params['driver'] = format_out
            dst = rasterio.open(filename_out, 'w', **params)
            dst.write(data)
            dst.close()
            src.close()
    except Exception as err:
        raise err
        return None
    return filename_out


# def warp(fileinname, fileoutname, dst_crs='EPSG:4326'):
#     import numpy as np
#     from rasterio.warp import calculate_default_transform, reproject, Resampling
#
#     with rasterio.open(fileinname) as src:
#         transform, width, height = calculate_default_transform(
#             src.crs, dst_crs, src.width, src.height, *src.bounds)
#         kwargs = src.meta.copy()
#         kwargs.update({
#             'crs': dst_crs,
#             'transform': transform,
#             'width': width,
#             'height': height
#         })
#
#         with rasterio.open(fileoutname, 'w', **kwargs) as dst:
#             for i in range(1, src.count + 1):
#                 reproject(
#                     source=rasterio.band(src, i),
#                     destination=rasterio.band(dst, i),
#                     src_transform=src.transform,
#                     src_crs=src.crs,
#                     dst_transform=transform,
#                     dst_crs=dst_crs,
#                     resampling=Resampling.nearest)
#
#     return fileoutname


def merge(filenames, output):
    """
    Return filename of merged 'filenames' GeoTIFFs

    Input:
        filenames : list
            List of filenames to merge
        output : string
            Mosaic filename
    """
    from rasterio.merge import merge as riomerge
    log.debug("Running 'merge' method.")

    with rasterio.open(filenames[0]) as src:
        meta = src.meta.copy()

    # The merge function returns a single array and the affine transform info
    arr, out_trans = riomerge(filenames)

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


def rescale(filename_in, filename_out, factor=0.5):
    """
    Resample data for faster processing. Rescale to HALF the resolution by default.
    """
    from rasterio.enums import Resampling

    with rasterio.open(filename_in) as src:

        height = int(src.height * factor)
        width = int(src.width * factor)
        transform = src.transform * src.transform.scale(
                    (src.width / width),
                    (src.height / height)
        )

        # resample data to target shape
        data = src.read(
            out_shape=(src.count, height, width),
            resampling=Resampling.bilinear
        )
        data[data<=src.nodata] = src.nodata

        # copy src metadata, update as necessary for 'dst'
        kwargs = src.meta.copy()
        kwargs.update({
            'transform': transform,
            'width': width,
            'height': height
        })

        # reproject "src" to "dst"
        with rasterio.open(filename_out, 'w', **kwargs) as dst:
            for i, band in enumerate(data, 1):
                dst.write(band, i)

        return filename_out

resample = rescale
