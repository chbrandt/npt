from ._sh import shs

def radiometry(filename_in, filename_out):
    shs.ctxcal(FROM=filename_in, TO=filename_out)
    return
