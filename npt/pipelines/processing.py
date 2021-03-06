import os
import shutil
import tempfile
from pathlib import Path

from . import log

from ..utils.filenames import change_extension as _change_file_extension
from ..utils.filenames import change_dirname as _change_file_dirname
from ..utils.filenames import insert_preext as _add_file_subextension

from gpt.raster import mosaic


def echo(msg):
    #print(msg)
    log.info(msg)


def proj_planet2earth(filein, fileout):
    from npt.utils.raster import warp
    return warp(filein, fileout)


def mosaic(filenames, output_path, make_dirs=True):
    if not os.path.isdir(output_path):
        if make_dirs:
            os.makedirs(output_path, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(output_path))
            return None

    output = Path(output_path) / 'mosaic.tif'
    output = raster.mosaic(filenames, output.as_posix())
    return output
    

#TODO: Add argument to set docker container to run --e.g., isis3-- commands
def run_file(filename_init, output_path, map_projection="sinusoidal",
            tmpdir=None, cog=True, make_dirs=True,
            datasetId='mars/mro/ctx/edr'):

    _datasets = [
        'mars/mex/hrsc/refdr3',
        'mars/mro/ctx/edr',
        'mars/mro/hirise/rdrv11'
    ]

    assert datasetId in _datasets, f"Dataset {datasetId} not supported"

    # Create a temp dir for the processing
    if tmpdir:
        assert os.path.isdir(tmpdir), """Given tmpdir '{}' does not exist""".format(tmpdir)
        tempfile.tempdir = tmpdir

    # assert os.path.isdir(output_path), """Given output_path '{}' does not exist""".format(output_path)
    if not os.path.isdir(output_path):
        if make_dirs:
            os.makedirs(output_path, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(output_path))
            return None

    try:
        tmpdir = tempfile.mkdtemp(prefix='neanias_')
    except:
        log.error("Temporary directory ('{}') could not be created.".format(tmpdir))
        raise err
    else:
        log.info("Temp dir: '{}'".format(tmpdir))

    #TODO: Add argument to set docker container to run --e.g., isis3-- commands
    #       Something along the lines:
    #       > run_container = 'isis3_gdal'
    #       > from npt.isis import sh
    #       > if run_container: sh.set_docker(run_container)

    if datasetId == 'mars/mro/ctx/edr':
        return run_file_ctx(filename_init, output_path, map_projection, tmpdir, cog)
    elif datasetId == 'mars/mro/hirise/rdrv11':
        return run_file_hirise(filename_init, output_path, map_projection, tmpdir, cog)
    elif datasetId == 'mars/mex/hrsc/refdr3':
        return run_file_hrsc(filename_init, output_path, map_projection, tmpdir, cog)
    else:
        assert None, "This line should not be reached"



def _run_geo_feature(geojson_feature, output_path, projection="sinusoidal", tmpdir=None, datasetId=None):
    from copy import deepcopy
    echo("Processing Feature: {!s}".format(geojson_feature))
    echo("Output go to: {!s}".format(output_path))
    feature = deepcopy(geojson_feature)
    properties = feature['properties']
    target = properties['targetName']
    mission = properties['mission']
    instrument = properties['instrumentId']
    product_type = properties['observationMode']
    datasetId = f"{target}/{mission}/{instrument}/{product_type}"
    properties = _run_props(properties, output_path, projection, tmpdir, datasetId)
    feature['properties'] = properties
    echo("Post-processed feature: {!s}".format(feature))
    return feature

reduce = _run_geo_feature


def _run_props(properties, output_path, map_projection, tmpdir, datasetId):
    from copy import deepcopy
    properties = deepcopy(properties)
    image_filename = properties['image_path']
    out = run_file(image_filename, output_path, map_projection, tmpdir, datasetId=datasetId)
    echo("Output files (CUB,TIF): {!s}".format(out))
    if out:
        echo("IF 'out' (non-null output)")
        if len(out) == 2:
            assert len(out) == 2, "Was expecting a tuple of filenames (CUB,TIF). Instead got {!s}".format(out)
            img_isis, img_tiff = out
            echo("ISIS3/IMG output file: {!s}".format(img_isis))
            echo("GeoTIFF output file: {!s}".format(img_tiff))
            #TODO: change 'image_path' to 'cube_path'. 'image_path' to stay pointing to source file
            properties['image_path'] = img_isis
            properties['tiff_path'] = img_tiff
            return properties
        else:
            assert len(out) == 1, "Was expecting a tuple a filename (TIF). Instead got {!s}".format(out)
            img_tiff = out[0]
            echo("GeoTIFF output file: {!s}".format(img_tiff))
            properties['image_path'] = ''
            properties['tiff_path'] = img_tiff
            return properties
    log.error("Processing output is null. See the temp files.")
    return None



def run_file_hrsc(filename_init, output_path, map_projection, tmpdir, cog):
    from npt.isis import format

    f_in = shutil.copy(filename_init, tmpdir)
    log.info("File '{}' copied".format(filename_init))

    # FORMAT to TIFF
    f_tif = _change_file_extension(f_in, 'tif')
    format.jpeg2tiff(f_in, f_tif, cog=cog)

    f_tif_out = _change_file_extension(f_in, 'tif')
    f_tif_out = _change_file_dirname(f_tif_out, output_path)

    try:
        log.info("Copying from temp to archive/output path")
        shutil.move(f_tif, f_tif_out)
    except Exception as err:
        log.error("File '{}' could not be created".format(f_tif_out))
        log.error("Temporary files, '{}' will remain. Remove them manually.".format(tmpdir))
        raise err
    finally:
        log.info("Cleaning temporary files/directory ({})".format(tmpdir))
        shutil.rmtree(tmpdir)

    return (f_tif_out,)


def run_file_hirise(filename_init, output_path, map_projection, tmpdir, cog):
    from npt.isis import format

    f_in = shutil.copy(filename_init, tmpdir)
    log.info("File '{}' copied".format(filename_init))

    # FORMAT to TIFF
    f_tif = _change_file_extension(f_in, 'tif')
    format.jpeg2tiff(f_in, f_tif, cog=cog)

    f_tif_out = _change_file_extension(f_in, 'tif')
    f_tif_out = _change_file_dirname(f_tif_out, output_path)

    try:
        log.info("Copying from temp to archive/output path")
        shutil.move(f_tif, f_tif_out)
    except Exception as err:
        log.error("File '{}' could not be created".format(f_tif_out))
        log.error("Temporary files, '{}' will remain. Remove them manually.".format(tmpdir))
        raise err
    finally:
        log.info("Cleaning temporary files/directory ({})".format(tmpdir))
        shutil.rmtree(tmpdir)

    return (f_tif_out,)



def run_file_ctx(filename_init, output_path, map_projection, tmpdir, cog):
    try:
        f_in = shutil.copy(filename_init, tmpdir)
        log.info("File '{}' copied".format(filename_init))

        # FORMAT (pds->isis)
        from npt.isis import format
        # -- Transfrom PDS (IMG) into ISIS (CUB) file
        f_cub = _change_file_extension(f_in, 'cub')

        format.pds2isis(f_in, f_cub)
        # -- Init SPICE kernel
        format.init_spice(f_cub)

        #TODO: be able to define at function level the container to run
        #       Functions in FORMAT and CALIBRATION, for example, could use a
        #       container 'isis3', whereas the FORMATting to TIFF, could use a
        #       different container, 'gispy' with "gdal" in it (not in 'isis3')

        # CALIBRATION
        from npt.isis import calibration
        f_cal = _add_file_subextension(f_cub, 'cal')
        calibration.radiometry(f_cub, f_cal)

        # MAP-PROJECTION
        from npt.isis import projection
        ## Define projection
        f_map = _add_file_subextension(f_cal, 'map')
        _flist = [f_cal]
        proj_file = projection.define_projection(_flist, projection=map_projection, tmpdir=tmpdir)
        ## Project
        projection.map_project(f_cal, f_map, proj_file)

        # FORMAT to TIFF
        f_tif = _change_file_extension(f_map, 'tif')
        format.isis2tiff(f_map, f_tif, cog=cog)

    except Exception as err:
        log.error(err)
        raise err
    else:
        log.info("Processing finished, file '{}' created.".format(f_tif))

    f_tif_out = _change_file_extension(f_in, 'tif')
    f_tif_out = _change_file_dirname(f_tif_out, output_path)
    f_cub_out = _change_file_dirname(f_cub, output_path)

    try:
        log.info("Copying from temp to archive/output path")
        shutil.move(f_tif, f_tif_out)
        shutil.move(f_cub, f_cub_out)
    except Exception as err:
        log.error("File '{}','{}' could not be created".format(f_cub_out, f_tif_out))
        log.error("Temporary files, '{}' will remain. Remove them manually.".format(tmpdir))
        raise err
    finally:
        log.info("Cleaning temporary files/directory ({})".format(tmpdir))
        shutil.rmtree(tmpdir)

    return (f_cub_out, f_tif_out)
