"""
Datasets dynamic import
"""
import sys
import pkgutil
import importlib

pkg = sys.modules[__package__]

def _iter_modules(pkg):
    return pkgutil.iter_modules(pkg.__path__, pkg.__name__+'.')

for finder, name, ispkg in _iter_modules(pkg):
    importlib.import_module(name)

del pkg, finder, name, ispkg
del importlib, pkgutil, sys
