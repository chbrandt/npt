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
        "descriptors": {
            'product_image': ('Description','PRODUCT DATA FILE WITH LABEL'),
        },
        "filters": {
            'product-id': ("^(CRU|MOI|T01)_", False)
        },
    },

    {
        "id": "{target}/{mission}/{instrument}/{product_type}",
        "target": "mars",
        "mission": "mro",
        "instrument": "hirise",
        "product_type": "rdrv11",
        "descriptors": {
            'product_image': ('Description', 'PRODUCT DATA FILE'),
            'product_label': ('Description', 'PRODUCT LABEL FILE'),
            'browse_image': ('Description', 'BROWSE'),
            'browse_thumbnail': ('Description', 'THUMBNAIL')
        },
        "filters": {
            'product-id': ("^(PSP|ESP)_.*(RED)", True)
        },
    },

    {
        "id": "{target}/{mission}/{instrument}/{product_type}",
        "target": "mars",
        "mission": "mex",
        "instrument": "hrsc",
        "product_type": "rdrv3",
        "descriptors": {
            'product_image': ('Description', 'PRODUCT DATA FILE'),
            'product_label': ('Description', 'PRODUCT LABEL FILE'),
            'browse_image': ('Description', 'BROWSE IMAGE'),
        },
        "filters": {
            'product-id': (".*_ND3.*", True)
        },
    },

    {
        "id": "{target}/{mission}/{instrument}/{product_type}",
        "target": "mars",
        "mission": "mex",
        "instrument": "hrsc",
        "product_type": "refdr3",
        "descriptors": {
            'product_image': ('Description', 'PRODUCT DATA FILE'),
            'product_label': ('Description', 'PRODUCT LABEL FILE'),
            'browse_image': ('Description', 'BROWSE IMAGE'),
        },
        "filters": {
            'product-id': (".*_ND3.*", True)
        },
    }
]


def _solve_datasets_references(dsets: list) -> dict:
    """
    Solve datasets/dictionary internal references
    """
    def _solve_self_references(mapin: dict) -> dict:
        """
        This function is able to resolve only simple references
        """
        def _resolved(value):
            import re
            return not re.match('.*{.+}.*', value)

        from copy import deepcopy
        mappings = deepcopy(mapin)

        keys_bypass = [k for k,v in mappings.items() if not isinstance(v,str)]
        mapout = {k:mappings.pop(k) for k in keys_bypass}
        mapaux = {k:v for k,v in mappings.items()
                      if _resolved(v)}
        cnt = 0
        while len(mapaux) < len(mappings):
            cnt += 1
            assert cnt <= len(mappings), "Apparently we are going for an infinite loop here..."
            _reset = set(mappings.keys()) - set(mapaux.keys())
            _aux = {k:mappings[k].format(**mapaux) for k in _reset}
            mapaux.update({ k:v for k,v in _aux.items()
                                # if not re.match('.*{.+}.*', v) })
                                if _resolved(v) })

        mapout.update(mapaux)
        return mapout

    _dsets = [_solve_self_references(d) for d in dsets]
    _pivot = {d['id']:d for d in _dsets}
    return _pivot


# Overwrite '_datasets' with parsed and pivot (list to dict{'id',...}) version
_datasets = _solve_datasets_references(_datasets)


def list():
    # dsets = [d['id'] for d in _datasets]
    # return sorted(dsets)
    return sorted(_datasets.keys())

def descriptors(dataset_id):
    return _datasets[dataset_id].get('descriptors')

def filters(dataset_id):
    try:
        _filters = _datasets[dataset_id].get('filters')
    except:
        _filters = None
    return _filters
