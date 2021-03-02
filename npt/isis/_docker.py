from npt import log

from sh import docker, awk, tail


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

containers_list = containers

def start_container(name):
    docker('start',name)
