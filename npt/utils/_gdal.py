import os
# import osgeo

from . import log

COG_ARGS = (
    '-of GTiff',
    '-co TILED=YES',
    #'-co COPY_SRC_OVERVIEWS=YES',
    '-co BLOCKXSIZE=512',
    '-co BLOCKYSIZE=512',
    '-co COMPRESS=LZW',
    '-co NUM_THREADS=4',
    '-co GEOTIFF_VERSION=AUTO'
    )

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
    log.debug("Running 'warp' method.")

    # The merge function returns a single array and the affine transform info
    gdal.Warp(output, filenames, format="GTiff",
              options=["COMPRESS=LZW", "TILED=YES"])

    return output


def tif2cog(filein, fileout):
    """
    Transform GeoTIFF in COG
    """
    from osgeo import gdal

    cog_args = ' '.join(COG_ARGS)
    log.debug(f"Translating file {filein} to {fileout}")
    gdal.Translate(fileout, filein, options=cog_args)

    return fileout

tiff2cog = tif2cog


def lbl2cog(filein, fileout):
    """
    Transform the respective file from LABEL in filein to COG
    """
    return tif2cog(filein, fileout)


def virtual(filenames, output):
    """
    Makes a mosaic through GDAL virtual file + translate
    """
    log.debug("Running 'virtual' method.")
    _froot, _ = os.path.splitext(output)
    _fvrt = _froot + ".vrt"

    vrt = gdal.BuildVRT(_fvrt, filenames, allowProjectionDifference=True)
    gdal.Translate(output, vrt)
    vrt = None

    return output


def merge(filenames, output):
    # from npt.isis import sh
    import subprocess
    log.debug("Running 'gdal-merge' method.")

    # gdal_merge = sh.wrap('gdal_merge.py')
    cog_args = ' '.join([
        # '-of COG',
        # '-co BLOCKSIZE=512',
        '-co COMPRESS=LZW',
        # '-co NUM_THREADS=2',
        # '-co GEOTIFF_VERSION=AUTO'
        ]).split()
    log.debug(cog_args)
    # res = gdal_merge('-o', output, *cog_args, *filenames)
    try:
        res = subprocess.call(['gdal_merge.py','-o',output] + cog_args + filenames)
    except Exception as err:
        log.error(str(err))
        return None
    else:
        return output
