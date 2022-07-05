"""
Datasets dynamic import
"""
# Refs:
# - https://packaging.python.org/guides/creating-and-discovering-plugins/
# - https://stackoverflow.com/a/64124377/687896
import npt


def list():
    """
    Return (sorted) list of available datasets
    """
    # dsets = [d['id'] for d in _datasets]
    # return sorted(dsets)
    return sorted(_datasets.keys())


def descriptors(dataset_id):
    """
    Return descriptors set for given 'dataset'
    """
    return _datasets[dataset_id].get('descriptors')


def filters(dataset_id):
    """
    Return filters set for given 'dataset'
    """
    try:
        _filters = _datasets[dataset_id].get('filters')
    except:
        _filters = None
    return _filters

# -----------------------------------------
# Dynamic load module in current directory:
# (Not being used anymore, but for records;
#  It implements a kind of plugin for data)
#
_bla = '''
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
'''
# -----------------------------------------


## Descriptors are the fields/values of ODE Results the identify the data products
## of our interest per project. Here is template, each project have them different.
# _DESCRIPTORS_TEMPLATE = {
#     'product_image': ('Description', 'PRODUCT DATA FILE'),
#     'product_label': ('Description', 'PRODUCT LABEL FILE'),
#     'browse_image': ('Description', 'BROWSE IMAGE'),
#     'browse_thumbnail': ('Description', 'THUMBNAIL IMAGE')
# }

## Filters are (regex) applied over Product IDs (project-based).
## Filters are tuples: "(<regex>, <True=include, or False=exclude>)" from output
# FILTERS = {
#     'ctx': ("^(CRU|MOI|T01)_", False),
#     'hirise': ("^(PSP|ESP)_.*(RED)", True),
#     'hrsc': (".*_ND3.*", True)
# }


# FIXME: datasets should be an object "label:{sets}" (not a list/anonymous)
_datasets = [
    {
        "target": "mars",
        "mission": "mro",
        "instrument": "ctx",
        "product_type": "edr",
        "id": "{target}/{mission}/{instrument}/{product_type}",
        "descriptors": {
            'product_image': ('Description','PRODUCT DATA FILE WITH LABEL'),
        },
        "filters": {
            'product-id': ("^(CRU|MOI|T01)_", False)
        },
    },

    {
        "target": "mars",
        "mission": "mro",
        "instrument": "hirise",
        "product_type": "rdrv11",
        "id": "{target}/{mission}/{instrument}/{product_type}",
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
        "target": "mars",
        "mission": "mex",
        "instrument": "hrsc",
        "product_type": "rdrv3",
        "id": "{target}/{mission}/{instrument}/{product_type}",
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
        "target": "mars",
        "mission": "mex",
        "instrument": "hrsc",
        "product_type": "refdr3",
        "id": "{target}/{mission}/{instrument}/{product_type}",
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
        Return version of 'maps_in' where simple "{internal}-{reference}" are resolved.

        Example:
            input:
            ```
            {
                "id": "{target}/{mission}/{instrument}/{product_type}",
                "target": "some_body",
                "mission": "some_spacecraft",
                "instrument": "some_sensor",
                "product_type": "some_dataset"
            }
            ```
            output:
            ```
            {
                "id": "some_body/some_spacecraft/some_sensor/some_dataset",
                "target": "some_body",
                "mission": "some_spacecraft",
                "instrument": "some_sensor",
                "product_type": "some_datalevel"
            }
            ```
        """
        def _resolved(value):
            """
            Return True if 'value' has NO more "{}": all fields are resolved.
            """
            import re
            return not re.match('.*{.+}.*', value)

        from copy import deepcopy
        mappings = deepcopy(mapin)

        # Fields/Keys to skip dereferencing: we only map flate/self references,
        # values that are not "str" (ie, data-structures) are moved to 'map_out'.
        # 'map_aux' is composed by all values already "resolved" (without "{}")
        keys_bypass = [k for k,v in mappings.items() if not isinstance(v,str)]
        mapout = {k:mappings.pop(k) for k in keys_bypass}
        mapaux = {k:v for k,v in mappings.items()
                      if _resolved(v)}
        cnt = 0
        while len(mapaux) < len(mappings):
            # if 'mapaux' is smaller than 'mappings' it means non-resolved values still there
            cnt += 1
            assert cnt <= len(mappings), f"Apparently going for an infinite loop: {mappings} {mapaux}"
            _reset = set(mappings.keys()) - set(mapaux.keys())
            _aux = {k:mappings[k].format(**mapaux) for k in _reset}
            mapaux.update({ k:v for k,v in _aux.items()
                                if _resolved(v) })

        # Once 'mapaux' has same size as 'mappings' (all fields resolved),
        # update 'map-out' with flat-fields resolved.
        mapout.update(mapaux)
        return mapout

    _dsets = [_solve_self_references(d) for d in dsets]
    # Make the output a pivot table with dataset/objects for keyword "dataset 'id'"
    _pivot = {d['id']:d for d in _dsets}
    return _pivot

# Overwrite '_datasets' with parsed and pivot (list to dict{'id',...}) version
_datasets = _solve_datasets_references(_datasets)
