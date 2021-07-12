#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the costbasis table from portfolio.db
"""
import os
import logging
import sqlite3

from portfolio.db.fdbhandler import transactions
from portfolio.db.dbutils import create_connection_f as create_connection


def add_cost_basis(new_account: str, starting_costbasis: float):
    """ Adds new account with an initial costbasis """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        query = """INSERT INTO 'costbasis'
            ('account','amount')
            VALUES (?,?);"""
        try:
            cursor.execute(query,
                           (new_account, starting_costbasis))
            logging.info(
                f"Added new account's '{new_account}' costbasis on database")
        except sqlite3.IntegrityError:
            logging.warning(f"Account {new_account} cost basis already exists")
            return
        conn.commit()


def edit_cost_basis(new_name: str, account: str):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE costbasis SET account = '{new_name}' WHERE account = '{account}' ")
        conn.commit()


def update_cost_basis_with_new_transaction(account: str, amount: str):
    """
    Adds the new transaction to the specific
    account involved, updating its cost basis
    """
    amount = int(round(float(amount[:-2]), 0) if '.' in amount else amount)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        new_costbasis = get_cost_basis(account) + amount
        cursor.execute(
            f"UPDATE costbasis SET amount = {new_costbasis} WHERE account = '{account}'")
        conn.commit()


def update_cost_basis():
    """
    Reads all transactions, and sums deposits
    and withdrawals to update each account's cost basis
    """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        # Getting new cost basis
        all_transactions = transactions.get_transactions_all()
        accounts_costbasis = {}
        for t in all_transactions:
            _, _, sendaccount, amount, receiveaccount, *_ = t
            if sendaccount not in accounts_costbasis.keys():
                accounts_costbasis[sendaccount] = 0
            if receiveaccount not in accounts_costbasis.keys():
                accounts_costbasis[receiveaccount] = 0
            accounts_costbasis[sendaccount] += -amount
            accounts_costbasis[receiveaccount] += amount

        # Updating table
        insert_query = "INSERT INTO 'costbasis' ('account', 'amount') VALUES (?,?);"
        update_query = "UPDATE costbasis SET amount = ? WHERE account = ? "
        current_accounts = get_all_accounts()
        for acc in accounts_costbasis:
            if acc not in current_accounts:
                # Adding
                cursor.execute(insert_query,
                               (acc, accounts_costbasis[acc]))
            else:
                # Updating
                cursor.execute(update_query,
                               (accounts_costbasis[acc], acc))
        conn.commit()


def get_all_accounts():
    """Returns all accounts"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        # Getting all accounts in table
        cursor.execute("SELECT account from costbasis")
        return [acc[0] for acc in cursor.fetchall()]


def get_cost_basis(account):
    """Returns cost basis from an account"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT amount FROM costbasis WHERE account = '{account}'")
        res = cursor.fetchall()
        return res[0][0] if res != [] else 0
