import os
from gpt import log


def _change_file_extension(filename, new_ext):
    fn = '.'.join(filename.split('.')[:-1] + [new_ext])
    return fn
def _add_file_subextension(filename, sub_ext):
    fs = filename.split('.')
    fs.insert(-1, sub_ext)
    fn = '.'.join(fs)
    return fn
def _change_file_dirname(filename, new_dir):
    bn = os.path.basename(filename)
    fn = os.path.join(new_dir, bn)
    return fn

class Processing:
    """
    Pre-processing (format+calibration+projection)

    Don't forget init-spice!
    """
    @staticmethod
    def _run_geo_feature(geojson_feature, output_path, projection="sinusoidal", tmpdir=None):
        feature = geojson_feature.copy()
        result_filename = Processing._run_props(feature['properties'], output_path)
        return feature

    run = _run_geo_feature

    @staticmethod
    def _run_props(properties, output_path, map_projection, tmpdir):
        image_filename = properties['image_path']
        output = Processing.run_file(image_filename, output_path, map_projection, tmpdir)


    @staticmethod
    def run_file(filename_init, output_path, map_projection="sinusoidal", tmpdir=None):
        # Create a temp dir for the processing
        import shutil
        import tempfile
        if tmpdir:
            assert os.path.isdir(tmpdir), """Given tmpdir '{}' does not exist""".format(tmpdir)
            tempfile.tempdir = tmpdir

        try:
            tmpdir = tempfile.mkdtemp(prefix='neanias_')
        except:
            print("Temporary directory ('{}') could not be created.".format(tmpdir))
            raise err
        else:
            print("Processing temporary dir: '{}'".format(tmpdir))

        try:
            f_in = shutil.copy(filename_init, tmpdir)

            # FORMAT (pds->isis)
            from gpt.isis import format
            # -- Transfrom PDS (IMG) into ISIS (CUB) file
            f_cub = _change_file_extension(f_in, 'cub')
            format.pds2isis(f_in, f_cub)
            # -- Init SPICE kernel
            format.init_spice(f_cub)

            # CALIBRATION
            from gpt.isis import calibration
            f_cal = _add_file_subextension(f_cub, 'cal')
            calibration.radiometry(f_cub, f_cal)

            # MAP-PROJECTION
            from gpt.isis import projection
            ## Define projection
            f_map = _add_file_subextension(f_cal, 'map')
            _flist = [f_cal]
            proj_file = projection.define_projection(_flist, projection=map_projection, tmpdir=tmpdir)
            ## Project
            projection.map_project(f_cal, f_map, proj_file)

            # FORMAT to TIFF
            f_tif = _change_file_extension(f_map, 'tif')
            format.isis2tiff(f_map, f_tif)

        except Exception as err:
            print("OOOPS, something went wrong.")
            raise err
        else:
            print("Processing finished, file '{}' created.".format(f_tif))

        try:
            print("Copying from temp to archive/output path")
            f_out =  _change_file_dirname(f_tif, output_path)
            shutil.move(f_tif, f_out)
        except Exception as err:
            print("File '{}' could not be moved to '{}'".format(f_tif, f_out))
            print("Temporary files, '{}' will remain. Remove them manually.".format(tmpdir))
            raise err
        finally:
            print("Cleaning temporary files/directory ({})".format(tmpdir))
            shutil.rmtree(tmpdir)

        return f_out

    @staticmethod
    def proj_planet2earth(filein, fileout):
        from gpt.raster import warp
        warp(filein, fileout)
