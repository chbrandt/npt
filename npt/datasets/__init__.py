"""
Datasets dynamic import
"""
# Refs:
# - https://packaging.python.org/guides/creating-and-discovering-plugins/
# - https://stackoverflow.com/a/64124377/687896
import npt



# -----------------------------------------
# Dynamic load module in current directory:
#
# DEPRECATED
#
import sys
import pkgutil
import importlib

pkg = sys.modules[__package__]

_datasets = []
for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__, pkg.__name__+'.'):
    mod = importlib.import_module(name)
    _datasets.append(mod)

del pkg, finder, name, ispkg
del importlib, pkgutil, sys
#
# -----------------------------------------

_datasets = [
    {
        "id": "{target}/{mission}/{instrument}/{product_type}",
        "target": "mars",
        "mission": "mro",
        "instrument": "ctx",
        "product_type": "edr",
    },

    {
        "id": "{target}/{mission}/{instrument}/{product_type}",
        "target": "mars",
        "mission": "mro",
        "instrument": "hirise",
        "product_type": "rdrv11",
    },

    {
        "id": "{target}/{mission}/{instrument}/{product_type}",
        "target": "mars",
        "mission": "mex",
        "instrument": "hrsc",
        "product_type": "rdrv3",
    },

    {
        "id": "{target}/{mission}/{instrument}/{product_type}",
        "target": "mars",
        "mission": "mex",
        "instrument": "hrsc",
        "product_type": "refdr3",
    }
]

def _solve_datasets_references(dsets: list) -> list:
    """
    Solve datasets/dictionary internal references
    """
    def _solve_self_references(mappings: dict) -> dict:
        """
        This function is able to resolve only simple references
        """
        import re
        mapout = {k:v for k,v in mappings.items()
                      if not re.match('.*{.+}.*', v) }
        cnt = 0
        while len(mapout) < len(mappings):
            cnt += 1
            assert cnt <= len(mappings), "Apparently we are going for an infinite loop here..."
            _reset = set(mappings.keys()) - set(mapout.keys())
            _aux = {k:mappings[k].format(**mapout) for k in _reset}
            mapout.update({ k:v for k,v in _aux.items()
                                if not re.match('.*{.+}.*', v) })
        return mapout

    return [_solve_self_references(d) for d in dsets]

# Overwrite '_datasets' with parsed/dereferenced version
_datasets = _solve_datasets_references(_datasets)

def list():
    for dset in _datasets:
        print(dset['id'])
