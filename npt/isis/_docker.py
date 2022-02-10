from sh import docker, awk, tail

from npt import log


def bake_container(name):
    """
    Return a Bash login shell from "inside" container 'name'

    "Inside" means it will exec whatever (wrapped) command from inside the
    (docker) container in a Bash login shell.
    """
    from sh import docker
    _exec_ = "exec -t {name!s} bash --login -c"
    if name not in list_containers():
        # TODO: together with an option "autorun", start/run container if not yet.
        raise ValueError
    dsh = docker.bake(_exec_.format(name=name).split())
    return dsh


def containers():
    """
    Return list of container (names) instanciated
    """
    from io import StringIO

    buf = StringIO()
    try:
        tail(awk(docker('ps','-a'), '{print $NF}'), '-n+2', _out=buf)
    except Exception as err:
        log.error(err)

    containers = buf.getvalue().split()
    return containers

list_containers = containers


def restart(name):
    """
    Re/Start a container
    """
    if name in containers():
        docker('start',name)
        return True
    else:
        log.warning(f"No container '{name}' instantiated. Nothing to restart.")
        return False

container_restart = restart
