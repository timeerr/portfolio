#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the balances table from portfolio.db
"""

import sqlite3
import os

from portfolio.db.fdbhandler import costbasis
from portfolio.db.dbutils import create_connection_f as create_connection
from portfolio import logger


def add_account(new_account: str, starting_amount: float):
    """
    Adds account to database.
    If it already exists, skips.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        query = """INSERT INTO 'balances'
                ('account','amount')
                VALUES (?,?);"""
        try:
            cursor.execute(query, (new_account, starting_amount))
            logger.info(f"Added new account '{new_account}' on database")
        except sqlite3.IntegrityError:
            logger.warning(f"Account {new_account} already exists")
            return
        conn.commit()
    # A new cost basis associated with this account has to be added
    costbasis.add_cost_basis(new_account, starting_amount)


def delete_account(account_name: str):
    """Removes account from database"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM balances WHERE account= '{account_name}'")
        conn.commit()


def edit_account(account: str, new_name: str):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE balances SET account = '{new_name}' WHERE account = '{account}' ")
        conn.commit()


def update_balances_with_new_result(account: str, amount: float):
    """Adds the new result to the specific account involved, updating its balance"""
    # Convert if str
    if isinstance(amount, str):
        amount = int(
            (round(float(amount[:-2]), 0)) if '.' in amount else amount)

    with create_connection() as conn:
        cursor = conn.cursor()
        current_balance = get_account(account)[1]
        new_balance = current_balance + amount
        cursor.execute(
            f"UPDATE balances SET amount = {new_balance} WHERE account = '{account}'")
        conn.commit()


def get_account(account: str):
    """Returns account entry"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM balances WHERE account= '{account}'")
        result = cursor.fetchall()
        return result if result == [] else result[0]


def get_account_balance(account: str):
    """Returns account balance"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT amount FROM balances WHERE account= '{account}'")
        result = cursor.fetchall()
        return result[0][0] if result != [] else result


def get_all_accounts():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM balances")
        return cursor.fetchall()


def get_all_account_names():
    return [i[0] for i in get_all_accounts()]


def get_total_balance_all_accounts():
    """
    Returns the sum of all the balances of all the accounts on this table
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT amount FROM balances")
        return sum([i[0] for i in cursor.fetchall()])
