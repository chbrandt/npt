from gpt import log
from ._sh import sh


_dstools = {
    'pds2isis': {
        'ctx': sh.wrap('mroctx2isis'),
        # Test
        'test': sh.wrap(['echo','`hostname`'])
    },
}


def pds2isis(filename_in, filename_out, dataset='test'):
    assert dataset in _dstools['pds2isis'], "Dataset '{}' not supported.".format(dataset)
    foo = _dstools['pds2isis'][dataset]
    res = foo(FROM=filename_in, TO=filename_out)
    sh.log(res)
    return res

def init_spice(filename):
    spiceinit = sh.wrap('spiceinit')
    res = spiceinit(FROM=filename)
    sh.log(res)
    return res

def isis2tiff(filename_in, filename_out):
    # return isissh.isis2std(FROM=filename_in, TO=filename_out, FORMAT='TIFF')
    from gpt import raster
    return raster.to_tiff(filename_in, filename_out, format_in='ISIS')
