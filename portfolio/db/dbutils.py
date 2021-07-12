import os
import sqlite3


class DBHandler:
    C_PATH_TO_DB = os.path.join('database', 'cportfolio.db')
    F_PATH_TO_DB = os.path.join('database', 'portfolio.db')


def create_connection_f(path_to_db=DBHandler.F_PATH_TO_DB):
    conn = None
    try:
        conn = sqlite3.connect(path_to_db)
    except sqlite3.OperationalError:
        import traceback
        print(traceback.format_exc(), path_to_db)
    return conn


def create_connection_c(path_to_db=DBHandler.C_PATH_TO_DB):
    conn = None
    try:
        conn = sqlite3.connect(path_to_db)
    except sqlite3.OperationalError:
        import traceback
        print(traceback.format_exc(), path_to_db)
    return conn
