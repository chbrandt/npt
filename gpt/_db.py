import sqlite3
from sqlite3 import Error

from gpt import log


class DB(object):
    _conn = None
    def __init__(self, db_file='/tmp/gpt.db'):
        super().__init__()
        # self.create_connection(db_file=':memory:')
        self.create_connection(db_file)

    def create_connection(self, db_file):
        self._conn = create_connection(db_file)

    def create_table(self, sql_create):
        create_table(self._conn, sql_create)

    def insert_record(self, sql_insert):
        insert_record(self._conn, sql_insert)



def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        log.info("Connection {!s} established.".format(conn))
    except Error as e:
        log.error(e)
        raise e
    return conn


def create_table(conn, sql_create):
    c = _exec(conn, sql_create)


def insert_record(conn, sql_insert):
    cur = _exec(conn, sql_insert)
    if cur:
        conn.commit()
    return cur.lastrowid


def _exec(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        log.error(e)
        raise e
    return c



db = DB()
