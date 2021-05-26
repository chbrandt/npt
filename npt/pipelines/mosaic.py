import os
import rasterio

from pathlib import Path

def from_features(features, files_field='tiff_path', output_path=None, tmpdir=None, make_dirs=True):
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
