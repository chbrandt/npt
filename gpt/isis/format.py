from ._sh import isissh

def pds2isis(filename_in, filename_out):
    # CTX:
    return isissh.mroctx2isis(FROM=filename_in, TO=filename_out)

def init_spice(filename):
    return isissh.spiceinit(FROM=filename)

def isis2tiff(filename_in, filename_out):
    return isissh.isis2std(FROM=filename_in, TO=filename_out, FORMAT='TIFF')
