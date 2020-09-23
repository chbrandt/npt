from ._sh import isissh

def define_projection(list_files, filename_proj, projection='sinusoidal', precision=0):
    proj = projection
    fout = filename_proj
    isissh.mosrange(FROMLIST=list_files, TO=fout, PROJECTION=proj, PRECISION=precision)

def map_project(filename_in, filename_out, filename_proj):
    isissh.cam2map(FROM=filename_in, TO=filename_out, MAP=filename_proj, PIXRES='map')
