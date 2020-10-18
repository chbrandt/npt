from gpt import log
# import sh
# isissh = sh(_long_prefix="")

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

def set_sh():
    from sh import bash
    return bash.bake('--login -c'.split())


def set_sh_docker(name):
    from sh import docker
    _exec_ = "exec -t {name!s} bash --login -c"
    _run_ = ""
    # check if 'name' is running. if not, start
    if name not in list_containers():
        # start/run conteiner
        raise NotImplementedError

    isissh = docker.bake(_exec_.format(name=name).split())
    return isissh


def list_containers():
    # from sh import docker
    # res = docker('ps','-a')
    return ['isis3-test']


# isissh = set_sh()
isissh = Sh()
