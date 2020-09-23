from ._sh import shs

def pds2isis(filename_in, filename_out):
    # CTX:
    shs.mroctx2isis(FROM=filename_in, TO=filename_out)
    return

def init_spice(filename):
    shs.spiceinit(FROM=filename)
    return
