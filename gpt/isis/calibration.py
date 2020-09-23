from ._sh import isissh

def radiometry(filename_in, filename_out):
    isissh.ctxcal(FROM=filename_in, TO=filename_out)
    return
