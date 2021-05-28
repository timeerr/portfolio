#! /usr/bin/python3
"""
This module creates the table that holds all info about trading/investing accounts
"""

import sqlite3
import os


def create_tables(path_to_db):
    conn = sqlite3.connect(path_to_db)
    cursor = conn.cursor()

    results_table_query = """CREATE TABLE IF NOT EXISTS results(
        id integer PRIMARY KEY,
        date integer NOT NULL,
        account text NOT NULL,
        strategy text NOT NULL,
        amount integer NOT NULL,
        description text,
        FOREIGN KEY (strategy)
            REFERENCES strategies (strategy)
    )"""
    # Date is stored as UNIX time

    strategies_table_query = """CREATE TABLE IF NOT EXISTS strategies(
        strategy text PRIMARY KEY,
        markettype text NOT NULL,
        amount integer NOT NULL
    )"""

    transactions_table_query = """CREATE TABLE IF NOT EXISTS transactions(
        id integer PRIMARY KEY,
        date timestamp NOT NULL,
        account_send text NOT NULL,
        amount integer NOT NULL,
        account_receive text NOT NULL,
        depositwithdrawal integer NOT NULL,
        description text
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
    cursor.execute(strategies_table_query)
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