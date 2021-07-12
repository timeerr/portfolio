#! /usr/bin/python3
"""
This module creates the table that holds all info about trading/investing accounts
"""

import sqlite3
import os

from portfolio.db.dbutils import DBHandler


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

    queries = (results_table_query, strategies_table_query,
               transactions_table_query, balances_table_query,
               balancehistory_table_query, costbasis_table_query)
    for q in queries:
        cursor.execute(q)
    conn.close()


def initialize():
    if 'database' not in os.listdir():
        os.mkdir('database')

    path_to_db = DBHandler.F_PATH_TO_DB
    create_tables(path_to_db)
