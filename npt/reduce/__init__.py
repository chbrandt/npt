import os
import shutil
import tempfile
from pathlib import Path

from npt import log

from ..utils.filenames import change_extension as _change_file_extension
from ..utils.filenames import change_dirname as _change_file_dirname
from ..utils.filenames import insert_preext as _add_file_subextension
from ..utils.geojson import write_feature_json

from npt.isis import format

def echo(msg):
    #print(msg)
    log.debug(msg)


def proj_planet2earth(filein, fileout):
    from npt.utils.raster import warp
    return warp(filein, fileout)


def from_geojson(geojson:dict, dataset:str, basepath:str="./data/reduced/",
                 projection:str="sinusoidal",
                 tmpdir:str=None, keep_tmpdir:bool=False,
                 overwrite:bool=False):
    """
    Process all images in geojson features
    """
    from copy import copy as shallowcopy

    features = geojson['features']
    new_features = []
    for feature in features:
        new_feature = from_feature(feature, dataset, basepath,
                                    projection=projection,
                                    tmpdir=tmpdir,
                                    keep_tmpdir=keep_tmpdir,
                                    overwrite=overwrite)
        assert id(new_feature) != id(feature)
        # Write the image/product respective feature/metadata next to it
        feature_filename = write_feature_json(new_feature)
        print("Feature/metadata file '{}' written.".format(feature_filename))
        new_features.append(new_feature)

    new_geojson = shallowcopy(geojson)
    assert id(new_geojson) != id(geojson)
    new_geojson['features'] = new_features

    return new_geojson


def from_feature(geojson_feature, dataset:str, basepath:str="./data/reduced/",
                 projection:str="sinusoidal",
                 tmpdir:str=None, keep_tmpdir:bool=False,
                 overwrite:bool=False):
    echo("Processing Feature: {!s}".format(geojson_feature))
    echo("Output go to: {!s}".format(basepath))
    feature = geojson_feature.copy()
    properties = feature['properties']
    properties = _run_props(properties, dataset=dataset, basepath=basepath,
                            projection=projection,
                            tmpdir=tmpdir, keep_tmpdir=keep_tmpdir,
                            overwrite=overwrite)
    feature['properties'] = properties
    echo("Post-processed feature: {!s}".format(feature))
    return feature


def _run_props(properties:dict, dataset:str, basepath:str="./data/reduced/",
                 projection:str="sinusoidal",
                 tmpdir:str=None, keep_tmpdir:bool=False,
                 overwrite:bool=False):
    properties = properties.copy()
    image_filename = properties['image_path']
    tif = _run_file(image_filename,
        basepath=basepath,
        projection=projection,
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
        # properties['image_path'] = tif
        properties['tiff_path'] = tif
        return properties
    else:
        log.error("Processing output is null. See the temp files.")
        return None


#TODO: Add argument to set docker container to run --e.g., isis3-- commands
def _run_file(filename:str, dataset:str, basepath:str="./data/reduced/",
                projection:str="sinusoidal",
                tmpdir:str=None, keep_tmpdir:bool=False,
                overwrite:bool=False,
                cog:bool=True, make_dirs:bool=True):
# def run_file(filename_init, output_path, map_projection="sinusoidal",
#             tmpdir=None, cog=True, make_dirs=True,
#             dataset=None, overwrite=True, keep_tmpdir=False):
    filename_out = Path(basepath) / f"{_change_file_extension(filename.split('/')[-1], 'tif')}"
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

    if basepath and not os.path.isdir(basepath):
        if make_dirs:
            os.makedirs(basepath, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(basepath))
            return None

    assert os.path.isdir(basepath), """Given output_path '{}' does not exist""".format(basepath)

    try:
        tmpdir = tempfile.mkdtemp(prefix='neanias_')
    except:
        log.error("Temporary directory ('{}') could not be created.".format(tmpdir))
        raise err
    else:
        log.info("Temp dir: '{}'".format(tmpdir))

    if 'ctx' in dataset:
        f_tif = reduce_ctx(filename, projection, tmpdir)
    elif 'hirise' in dataset:
        f_tif = reduce_hirise(filename, tmpdir)
    elif 'hrsc' in dataset:
        f_tif = reduce_hrsc(filename, tmpdir)
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
