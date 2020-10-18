from gpt import log
# import sh
# isissh = sh(_long_prefix="")

def set_sh():
    from sh import bash
    return bash.bake('--login -c'.split())


def set_sh_docker(name):
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
    return ['isis3-test']


class Sh():
    _sh = None
    def __init__(self):
        self.reset()

    def __call__(self, *args, **kwargs):
        return self._sh(*args, **kwargs)

    def set_docker(self, name):
        assert name in list_containers()
        self._sh = set_sh_docker(name)

    def reset(self):
        _sh = set_sh()
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
