#! /usr/bin/python3
"""
This module creates the table that holds all info about cryptocurrency accounts
"""

import sqlite3
import os

from portfolio.db.dbutils import DBHandler


def create_tables(path_to_db):
    conn = sqlite3.connect(path_to_db)
    cursor = conn.cursor()

    transactions_table_query = """
        CREATE TABLE IF NOT EXISTS ctransactions(
        id integer PRIMARY KEY,
        date timestamp NOT NULL,
        account_send text NOT NULL,
        token text NOT NULL,
        amount integer NOT NULL,
        account_receive text NOT NULL
    )"""

    balances_table_query = """
        CREATE TABLE IF NOT EXISTS cbalances(
        account text NOT NULL,
        token text NOT NULL,
        amount integer NOT NULL,
        type text NOT NULL,
        kyc text NOT NULL,
        description text ,
        UNIQUE(account,token)
    )
    """

    balancehistory_table_query = """
        CREATE TABLE IF NOT EXISTS cbalancehistory(
        id integer PRIMARY KEY,
        account text NOT NULL,
        date timestamp NOT NULL,
        token text NOT NULL,
        balance integer NOT NULL,
        balance_btc integer NOT NULL,
        balance_eur integer NOT NULL,
        balance_usd integer NOT NULL,
        balance_jpy integer NOT NULL
    )"""

    # Inserting tables
    cursor.execute(transactions_table_query)
    cursor.execute(balances_table_query)
    cursor.execute(balancehistory_table_query)

    # Closing db
    conn.commit()
    conn.close()


def initialize(path=None):
    prev_cwd = os.getcwd()  # To return later
    if path is None:
        path = prev_cwd
    os.chdir(path)
    if 'database' not in os.listdir():
        os.mkdir('database')
    create_tables(DBHandler.C_PATH_TO_DB)
    os.chdir(prev_cwd)  # Come back
