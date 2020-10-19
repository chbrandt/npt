from npt import log

from . import search as Search
from . import download as Download
from . import processing as Processing


class Pipeline(object):
    """
    Manage environment for running processing blocks

    * set Data base path
      - in case of a docker container, base path must be set accordingly
    """
