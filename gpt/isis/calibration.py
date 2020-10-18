from ._sh import sh

def radiometry(filename_in, filename_out):
    ctxcal = sh.wrap('ctxcal')
    res = ctxcal(FROM=filename_in, TO=filename_out)
    sh.log(res)
    return res
