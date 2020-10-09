"""
Datasets dynamic import
"""
# Refs:
# - https://packaging.python.org/guides/creating-and-discovering-plugins/
# - https://stackoverflow.com/a/64124377/687896
import gpt

import sys
import pkgutil
import importlib

pkg = sys.modules[__package__]

def _iter_modules(pkg):
    return pkgutil.iter_modules(pkg.__path__, pkg.__name__+'.')

_datasets = []
for finder, name, ispkg in _iter_modules(pkg):
    importlib.import_module(name)
    _datasets.append(name)

del pkg, finder, name, ispkg
del importlib, pkgutil, sys


class Datasets(object):
    """
    Manage datasets package<->db
    """
    _name = 'datasets'
    _schema = {'name': {'type': 'text', 'attr':'NOT NULL'},
                'provider': {'type': 'text', 'attr':'NOT NULL'},
                'id': {'type': 'integer', 'attr':'PRIMARY KEY'},
                'target': {'type': 'text', 'attr':'NOT NULL'},
                'mission': {'type': 'text', 'attr':'NOT NULL'},
                'instrument': {'type': 'text', 'attr':'NOT NULL'},
                'product_type': {'type': 'text', 'attr':'NOT NULL'},
                }

    def __init__(self, datasets=None):
        self.init_table()
        if datasets:
            self.insert_datasets(datasets)


    def init_table(self):
        _sql_create_datasets_table = """
            CREATE TABLE IF NOT EXISTS {table}
        """.format(table=self._name)
        _s = ','.join([
                    "{col} {typ} {att}".format(col=c, typ=d['type'], att=d['attr'])
                    for c,d in self._schema.items()
                ])
        _sql_create_datasets_table += "({})".format(_s)
        gpt.db.create_table(_sql_create_datasets_table)


    def insert_datasets(self, datasets):
        for dset in datasets:
            self.insert_dataset(dset)


    def insert_dataset(self, dataset):
        """
        dataset is a map column:value

        # TODO: Columns must respect a schema.
        """
        cols,vals = list(dataset.items())

        _sql_insert_dataset_record = """
            INSERT INTO {table}({cols}) VALUES({vals})
        """.format(table=self._name, cols=cols, vals=vals)

        gpt.db.insert_record(_sql_insert_dataset_record)


datasets = Datasets(_datasets)
