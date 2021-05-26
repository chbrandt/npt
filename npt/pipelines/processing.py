import os
import shutil
import tempfile
from pathlib import Path

from . import log

from ..utils.filenames import change_extension as _change_file_extension
from ..utils.filenames import change_dirname as _change_file_dirname
from ..utils.filenames import insert_preext as _add_file_subextension

from npt.isis import format

def echo(msg):
    #print(msg)
    log.debug(msg)


def proj_planet2earth(filein, fileout):
    from npt.utils.raster import warp
    return warp(filein, fileout)


def _run_geo_feature(geojson_feature, output_path, projection="sinusoidal", tmpdir=None, dataset=None, overwrite=True, keep_tmpdir=False):
    echo("Processing Feature: {!s}".format(geojson_feature))
    echo("Output go to: {!s}".format(output_path))
    feature = geojson_feature.copy()
    properties = feature['properties']
    properties = _run_props(properties, output_path, projection, tmpdir, dataset=dataset, overwrite=overwrite, keep_tmpdir=keep_tmpdir)
    feature['properties'] = properties
    echo("Post-processed feature: {!s}".format(feature))
    return feature

run = _run_geo_feature


def _run_props(properties, output_path, map_projection, tmpdir, dataset=None, overwrite=True, keep_tmpdir=False):
    properties = properties.copy()
    image_filename = properties['image_path']
    tif = run_file(image_filename,
        output_path=output_path,
        map_projection=map_projection,
        tmpdir=tmpdir,
        dataset=dataset,
        overwrite=overwrite,
        keep_tmpdir=keep_tmpdir)
    echo("Output file (TIF): {!s}".format(tif))
    if tif:
        # echo("IF 'out' (non-null output)")
        # assert len(out) == 2, "Was expecting a tuple of filenames (CUB,TIF). Instead got {!s}".format(out)
        # img_isis, img_tiff = out
        # echo("ISIS3/IMG output file: {!s}".format(img_isis))
        # echo("GeoTIFF output file: {!s}".format(img_tiff))
        #TODO: change 'image_path' to 'cube_path'. 'image_path' to stay pointing to source file
        try:
            tmp = tif.as_posix()
            tif = tmp
        except:
            assert isinstance(tif, str)
        properties['image_path'] = tif
        properties['tiff_path'] = tif
        return properties
    log.error("Processing output is null. See the temp files.")
    return None


#TODO: Add argument to set docker container to run --e.g., isis3-- commands
def run_file(filename_init, output_path, map_projection="sinusoidal", tmpdir=None, cog=True, make_dirs=True, dataset=None, overwrite=True, keep_tmpdir=False):
    filename_out = Path(output_path) / f"{_change_file_extension(filename_init.split('/')[-1], 'tif')}"
    if not overwrite:
        if filename_out.exists():
            log.info(f"File '{filename_out}' already exists. Use overwrite to force rewriting.")
            return filename_out.as_posix()

    # Create a temp dir for the processing
    if tmpdir and not os.path.isdir(tmpdir):
        if make_dirs:
            os.makedirs(tmpdir, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(tmpdir))
            return None

    if tmpdir:
        assert os.path.isdir(tmpdir), """Given tmpdir '{}' does not exist""".format(tmpdir)
        tempfile.tempdir = tmpdir

    if output_path and not os.path.isdir(output_path):
        if make_dirs:
            os.makedirs(output_path, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(output_path))
            return None

    assert os.path.isdir(output_path), """Given output_path '{}' does not exist""".format(output_path)

    try:
        tmpdir = tempfile.mkdtemp(prefix='neanias_')
    except:
        log.error("Temporary directory ('{}') could not be created.".format(tmpdir))
        raise err
    else:
        log.info("Temp dir: '{}'".format(tmpdir))

    if 'ctx' in dataset:
        f_tif = reduce_ctx(filename_init, map_projection, tmpdir)
    elif 'hirise' in dataset:
        f_tif = reduce_hirise(filename_init, tmpdir)
    elif 'hrsc' in dataset:
        f_tif = reduce_hrsc(filename_init, tmpdir)
    else:
        raise NotImplementedError

    # f_tif_out = _change_file_extension(f_in, 'tif')
    # f_tif_out = _change_file_dirname(f_tif_out, output_path)
    # f_cub_out = _change_file_dirname(f_cub, output_path)
    # f_tif_out = _change_file_dirname(f_tif, output_path)
    f_tif_out = filename_out

    try:
        log.info("Copying from temp to archive/output path")
        shutil.move(f_tif, f_tif_out)
        # shutil.move(f_cub, f_cub_out)
    except Exception as err:
        # log.error("File '{}','{}' could not be created".format(f_cub_out, f_tif_out))
        log.error("File '{}' could not be created".format(f_tif_out))
        log.error("Temporary files, '{}' will remain. Remove them manually.".format(tmpdir))
        raise err
    finally:
        if not keep_tmpdir:
            log.info("CLEANING temporary files/directory ({})".format(tmpdir))
            shutil.rmtree(tmpdir)
        else:
            log.info("KEEPING temporary files/directory ({})".format(tmpdir))

    return f_tif_out


def reduce_ctx(filename_init, map_projection, tmpdir):
    try:
        f_in = shutil.copy(filename_init, tmpdir)
        log.info("File '{}' copied".format(filename_init))

        # FORMAT (pds->isis)
        # -- Transfrom PDS (IMG) into ISIS (CUB) file
        f_cub = _change_file_extension(f_in, 'cub')

        format.pds2isis(f_in, f_cub)
        # -- Init SPICE kernel
        # format.init_spice(f_cub)

        #TODO: be able to define at function level the container to run
        #       Functions in FORMAT and CALIBRATION, for example, could use a
        #       container 'isis3', whereas the FORMATting to TIFF, could use a
        #       different container, 'gispy' with "gdal" in it (not in 'isis3')

        # CALIBRATION
        from npt.isis import calibration
        f_cal = _add_file_subextension(f_cub, 'cal')
        calibration.radiometry(f_cub, f_cal)

        # -- Init SPICE kernel
        format.init_spice(f_cal)

        # MAP-PROJECTION
        from npt.isis import projection
        ## Define projection
        f_map = _add_file_subextension(f_cal, 'map')
        _flist = [f_cal]
        proj_file = projection.define_projection(_flist, projection=map_projection, tmpdir=tmpdir)
        ## Project
        projection.map_project(f_cal, f_map, proj_file)

        # FORMAT to TIFF
        f_tif = _change_file_extension(f_in, 'tif')
        format.isis2tiff(f_map, f_tif, cog=True)

    except Exception as err:
        log.error(err)
        raise err
    else:
        log.info("Processing finished, file '{}' created.".format(f_tif))

    return f_tif


def reduce_hirise(filename_init, tmpdir):
    return _jpeg2tiff(filename_init, tmpdir)


def reduce_hrsc(filename_init, tmpdir):
    return _jpeg2tiff(filename_init, tmpdir)


def _jpeg2tiff(filename_init, tmpdir):
    try:
        # FORMAT (pds->isis)
        from npt.isis import format
        f_jp2 = shutil.copy(filename_init, tmpdir)
        # FORMAT to TIFF
        f_tif = _change_file_extension(f_jp2, 'tif')
        format.jpeg2tiff(f_jp2, f_tif, cog=True)

    except Exception as err:
        log.error(err)
        raise err

    else:
        log.info("Processing finished, file '{}' created.".format(f_tif))

    return f_tif
