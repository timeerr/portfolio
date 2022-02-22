#! /usr/bin/python3
"""
This module creates the table that holds all info about trading/investing accounts
"""

import sqlite3
import os

from portfolio.db.dbutils import DBHandler
from portfolio.db.dbutils import create_connection_f as create_connection


def create_tables(path_to_db):

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
    with create_connection() as conn:
        cursor = conn.cursor()
        for q in queries:
            cursor.execute(q)


def initialize(path=None):
    prev_cwd = os.getcwd()  # To return later
    if path is None:
        path = prev_cwd
    os.chdir(path)
    if 'database' not in os.listdir():
        os.mkdir('database')
    create_tables(DBHandler.F_PATH_TO_DB)
    os.chdir(prev_cwd)  # Come back
