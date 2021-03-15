#! /usr/bin/python3

import sqlite3
import os


def create_tables(path_to_db):
    conn = sqlite3.connect(path_to_db)
    cursor = conn.cursor()

    results_table_query = """CREATE TABLE IF NOT EXISTS results(
        id integer PRIMARY KEY,
        date integer NOT NULL,
        account text NOT NULL,
        amount integer NOT NULL
    )"""
    # Date is stored as UNIX time

    transactions_table_query = """CREATE TABLE IF NOT EXISTS transactions(
        id integer PRIMARY KEY,
        date timestamp NOT NULL,
        account_send text NOT NULL,
        amount integer NOT NULL,
        account_receive text NOT NULL,
        depositwithdrawal integer NOT NULL
    )"""

    balances_table_query = """CREATE TABLE IF NOT EXISTS balances(
        account text PRIMARY KEY,
        amount integer NOT NULL
    )
    """

    balancehistory_table_query = """CREATE TABLE IF NOT EXISTS balancehistory(
        id integer PRIMARY KEY,
        account text NOT NULL,
        date timestamp NOT NULL,
        balance integer NOT NULL,
        FOREIGN KEY (account)
            REFERENCES balances (account)
    )"""

    costbasis_table_query = """CREATE TABLE IF NOT EXISTS costbasis(
        account text PRIMARY KEY,
        amount integer NOT NULL,
        FOREIGN KEY (account)
            REFERENCES balances (account)
    )"""

    # Inserting tables
    cursor.execute(results_table_query)
    cursor.execute(transactions_table_query)
    cursor.execute(balances_table_query)
    cursor.execute(balancehistory_table_query)
    cursor.execute(costbasis_table_query)

    # Closing db
    conn.close()


if 'database' not in os.listdir():
    os.mkdir('database')
path_to_db = os.path.join('database', 'portfolio.db')
create_tables(path_to_db)
