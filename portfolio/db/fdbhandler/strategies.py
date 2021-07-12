#!/usr/bin/python3
"""
Handles all the input and output operations that use the strategies table from portfolio.db
"""

import os
from datetime import datetime
import logging
import sqlite3

from portfolio.db.fdbhandler import balances
from portfolio.db.dbutils import create_connection_f as create_connection


def add_strategy(strategy: str, markettype: str):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        query = "INSERT INTO strategies ('strategy','markettype','amount') VALUES (?,?,?);"
        try:
            cursor.execute(query,
                           (strategy, markettype, 0))
            logging.info(f"Added new strategy '{strategy}' on database")
        except sqlite3.IntegrityError:
            logging.warning(
                f"Strategy {strategy} already exists on database")
        conn.commit()


def delete_strategy(strategy_name: str):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"DELETE FROM strategies WHERE strategy= '{strategy_name}' ")
        conn.commit()


def edit_strategy_name(strategy: str, new_name: str):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE strategies SET strategy = '{new_name}' WHERE strategy = '{strategy}' ")
        conn.commit()


def edit_strategy_type(_type: str, new_type: str):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE strategies SET markettype = '{_type}' WHERE markettype = '{new_type}' ")
        conn.commit()


def update_strategies_with_new_result(strategy: str, amount: float):
    """
    Adds the new result to the specific
    strategy involved, updating its balance
    """
    amount = int(round(float(amount[:-2]), 0) if '.' in amount else amount)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        new_balance = get_strategy_balance(strategy) + amount
        cursor.execute(
            f"UPDATE strategies SET amount = {new_balance} WHERE strategy = '{strategy}'")
        conn.commit()


def get_strategy(strategy: str):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM strategies WHERE strategy= '{strategy}'")
        result = cursor.fetchall()
        return result if result == [] else result[0]


def get_strategy_balance(strategy: str):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT amount FROM strategies WHERE strategy= '{strategy}'")
        result = cursor.fetchall()
        return result if result == [] else result[0][0]


def get_strategy_market_type(strategy: str):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT markettype FROM strategies WHERE strategy = '{strategy}'")
        return cursor.fetchall()[0][0]


def get_all_strategies():
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategies")
        return cursor.fetchall()


def get_all_strategy_names():
    return [i[0] for i in get_all_strategies()]
