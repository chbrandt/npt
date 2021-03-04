import os
import tempfile
import pathlib

from npt import log

def mkpath(basedir=None, prefix=None):
    """
    Return path of directory for temporary use

    Args:
        basedir: string
            Base path (already existent) for parenting new temp-dir
        prefix: string
            Prefix to use for new temp-dir name (a random string is appended to it)

    Return:
        Path (pathlib) object for newly created temp-dir
    """

    if basedir:
        assert os.path.isdir(basedir), "Given basedir '{}' does not exist".format(basedir)
        tempfile.tempdir = basedir

    try:
        tmpdir = tempfile.mkdtemp(prefix=prefix)
    except:
        log.error("Temporary directory ('{}') could not be created.".format(tmpdir))
        raise err
    else:
        log.info("Temp dir: '{}'".format(tmpdir))

    return pathlib.Path(tmpdir)
