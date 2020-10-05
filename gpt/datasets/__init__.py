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

for finder, name, ispkg in _iter_modules(pkg):
    importlib.import_module(name)

del pkg, finder, name, ispkg
del importlib, pkgutil, sys


_database = r"C:\sqlite\db\pythonsqlite.db"
_name = 'datasets'

_sql_create_datasets_table = """
    CREATE TABLE IF NOT EXISTS {name} (
        id integer PRIMARY KEY,
        name text NOT NULL,
        begin_date text,
        end_date text
    );
""".format(name=_name)

gpt.db.create_table(_sql_create_datasets_table)

_sql_insert_dataset_record = """
    INSERT INTO datasets(name) VALUES('bla')
"""

gpt.db.insert_record(_sql_insert_dataset_record)
