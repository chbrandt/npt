from npt import log
from . import sh

from npt.utils import raster

_dstools = {
    'pds2isis': {
        'ctx': sh.wrap('mroctx2isis'),
        # Test
        'test': sh.wrap(['echo','`hostname`'])
    },
}


def pds2isis(filename_in, filename_out, dataset='ctx'):
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

def isis2tiff(filename_in, filename_out, cog=False):
    # return isissh.isis2std(FROM=filename_in, TO=filename_out, FORMAT='TIFF')
    return raster.to_tiff(filename_in, filename_out, format_in='ISIS', cog=cog)

def jpeg2tiff(filename_in, filename_out, cog=False):
    # return isissh.isis2std(FROM=filename_in, TO=filename_out, FORMAT='TIFF')
    return raster.to_tiff(filename_in, filename_out, format_in='JP2OpenJPEG', cog=cog)
