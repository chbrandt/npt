from npt import log


def _set_sh():
    from sh import bash
    return bash.bake('--login -c'.split())

def _set_sh_docker(name):
    from sh import docker
    _exec_ = "exec -t {name!s} bash --login -c"
    _run_ = ""
    if name not in list_containers():
        # start/run conteiner
        raise NotImplementedError

    isissh = docker.bake(_exec_.format(name=name).split())
    return isissh

def list_containers():
    # from sh import docker
    # res = docker('ps','-a')
    #TODO: fix this!
    return ['gispy','isis3','isis3_gdal','isis3_gdal_npt_tests']

class Sh():
    _sh = None
    def __init__(self):
        self.reset()

    def __call__(self, *args, **kwargs):
        return self._sh(*args, **kwargs)

    @staticmethod
    def log(res):
        log.debug("Exit code: "+str(res and res.exit_code))

    def set_docker(self, name):
        assert name in list_containers()
        self._sh = _set_sh_docker(name)

    def reset(self):
        _sh = _set_sh()
        log.debug(_sh)
        self._sh = _sh

    def wrap(self, exec):
        return _wrapper(exec, sh=self)

sh = Sh()

def _wrapper(exec, sh=sh):
    """
    Wrap "exec" (eg, 'echo') by a 'Sh()'
    """
    if isinstance(exec, str):
        exec = [exec]
    def _sh(*args,**kwargs):
        v = [f'{v}' for v in args]
        kv = [f'{k}={v}' for k,v in kwargs.items()]
        comm = ' '.join(exec+v+kv)
        log.debug(comm)
        return sh(comm)
    return _sh
