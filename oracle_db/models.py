from pathlib import Path

import cx_Oracle
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    if sys.platform.startswith("darwin"):
        cx_Oracle.init_oracle_client(lib_dir=str(BASE_DIR) + "/instantclient_19_8")
    elif sys.platform.startswith("win32"):
        # Hard-code
        lib_dir=r"C:\inetpub\wwwroot\vnpt-ttkd\instantclient_19_11"
        cx_Oracle.init_oracle_client(lib_dir=lib_dir)
except Exception as err:
    sys.exit(1)

class ORACLE_DB:
    def __init__(self, kwargs):
        CONN_STR = "{oracle_user}/{oracle_psw}@{oracle_host}:{oracle_port}/{oracle_service}".format(**kwargs)
        self.conn = cx_Oracle.connect(CONN_STR)

    def query(self, query, params=None):
        cursor = self.conn.cursor()
        result = cursor.execute(query, params).fetchall()
        cursor.close()
        return result

    def insert_multiple(self, table, columns, rows):
        cursor = self.conn.cursor()
        columns_str = ', '.join(columns)
        insert_idx = ', '.join([":%s" % i for i in range(1, len(columns) + 1)])
        cursor.bindarraysize = len(rows)
        cursor.setinputsizes(int, 20, int, 100)
        cursor.executemany(f"insert into {table} ({columns_str}) values ({insert_idx})", rows)
        self.conn.commit()
        cursor.close()

    # def search(self, table):
    #     query = f"""SELECT * FROM {table} WHERE """


