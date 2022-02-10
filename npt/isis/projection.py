import os
from npt import log
from . import sh


def define_projection(list_files, projection='sinusoidal', precision=0, tmpdir=None):
    tmpdir = tmpdir or ''
    _file_list = os.path.join(tmpdir, 'files_to_project.list')
    with open(_file_list, 'w') as fp:
        fp.write('\n'.join(list_files))
        fp.write('\n')
    _file_proj = os.path.join(tmpdir, projection+'.map')

    mosrange = sh.wrap('mosrange')
    res = mosrange(FROMLIST=_file_list, TO=_file_proj,
                   PROJECTION=projection, PRECISION=precision)
    sh.log(res)
    return _file_proj


def map_project(filename_in, filename_out, filename_proj):
    cam2map = sh.wrap('cam2map')
    res = cam2map(FROM=filename_in, TO=filename_out, MAP=filename_proj, PIXRES='map')
    sh.log(res)
    return res
