from ._sh import isissh

def pds2isis(filename_in, filename_out):
    # CTX:
    isissh.mroctx2isis(FROM=filename_in, TO=filename_out)
    return

def init_spice(filename):
    isissh.spiceinit(FROM=filename)
    return
