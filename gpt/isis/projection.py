import os
from ._sh import isissh

def define_projection(list_files, projection='sinusoidal', precision=0, tmpdir=None):
    tmpdir = tmpdir or ''
    _file_list = os.path.join(tmpdir, 'files_to_project.list')
    with open(_file_list, 'w') as fp:
        fp.write('\n'.join(list_files))
        fp.write('\n')
    _file_proj = os.path.join(tmpdir, projection+'.map')
    isissh.mosrange(FROMLIST=_file_list, TO=_file_proj,
                    PROJECTION=projection, PRECISION=precision)
    return _file_proj

def map_project(filename_in, filename_out, filename_proj):
    isissh.cam2map(FROM=filename_in, TO=filename_out, MAP=filename_proj, PIXRES='map')
