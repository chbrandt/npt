"""
Provides functions to run `ISIS3`_ commands

Modules you'll find here handle tasks primarily thought to handle processing for
`NEANIAS`_ and `GMAP`_, where we are particularly interest on images from
Mars, the Moon, and Mercury.
Modules (``format``, ``calibration``, etc) provide some functions to process
and handle our (`PDS`_) data.

The `isissh` callable you'll find here is an interface to `sh`_ adapted to
the way ISIS3 define their command line interface (without hifen (``--``), with ``=``);
E.g,
.. code-block:: bash

   $ automos FROMLIST=mapcubs.list MOSAIC=mosaic.cub

E.g, :command: `automos FROMLIST=mapcubs.list mosaic=B01_009_mosaic.cub`

With ``isissh`` the command above would be called (here, in python):
.. code-block:: python
   isissh.automos(FROMLIST='mapcubs.list', MOSAIC=mosaic.cub)

**Always** use *UPPER-CASE* on those calls' arguments, that will free yourself
from any Python `reserved keywords`_ such as ``from``; You *cannot* call:
:command: isissh.spiceinit(from=filename)
, Python will give you a syntax error. But you *can* call:
.. code-block:: python
   isissh.spiceinit(FROM=filename)
 since ISIS3 command arguments are case *in*\ sensitive.

.. _ISIS3: bla
.. _NEANIAS: bla
.. _GMAP: bla
.. _sh: bla
"""
from . import (format,
               calibration,
               projection)

from ._sh import sh

isissh = sh    # Deprecated, here only for backwards compatibility

def set_docker(name):
    isissh.set_docker(name)


__all__ = ['isissh']
