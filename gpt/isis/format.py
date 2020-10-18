from gpt import log
from ._sh import isissh
# from ._sh import get_sh


def _wrapper(exec):
    if isinstance(exec, str):
        exec = [exec]
    def _isissh(*args,**kwargs):
        v = [f'{v}' for v in args]
        kv = [f'{k}={v}' for k,v in kwargs.items()]
        comm = ' '.join(exec+v+kv)
        log.info(comm)
        return isissh(comm)
        # from sh import sleep
        # return sleep('5')
    return _isissh

_dstools = {
    'pds2isis': {
        'ctx': _wrapper('mroctx2isis'),
        # Test
        'test': _wrapper(['echo','`hostname`'])
    },
    # 'init_spice': lambda **kwargs: isissh.spiceinit(**kwargs)
}

def pds2isis(filename_in, filename_out, dataset='test'):
    # CTX:
    # return isissh.mroctx2isis(FROM=filename_in, TO=filename_out)
    assert dataset in _dstools['pds2isis'], "Dataset '{}' not supported.".format(dataset)
    foo = _dstools['pds2isis'][dataset]
    res = foo(FROM=filename_in, TO=filename_out)
    log.info("Exit code: "+str(res and res.exit_code))
    return res

def init_spice(filename):
    return isissh.spiceinit(FROM=filename)

def isis2tiff(filename_in, filename_out):
    # return isissh.isis2std(FROM=filename_in, TO=filename_out, FORMAT='TIFF')
    from gpt import raster
    return raster.to_tiff(filename_in, filename_out, format_in='ISIS')
