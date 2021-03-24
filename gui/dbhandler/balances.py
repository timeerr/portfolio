#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the balances table from portfolio.db
"""

import sqlite3
import os

from gui.dbhandler import costbasis

PATH_TO_DB = os.path.join('database', 'portfolio.db')


def createConnection(path_to_db=PATH_TO_DB):
    """Connects to the database on a certain path, returning the connection"""
    conn = None

    try:
        conn = sqlite3.connect(path_to_db)
    except sqlite3.Operational as e:
        print(e, path_to_db)

    return conn


def addAccount(new_account, starting_amount):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        add_account_query = """INSERT INTO 'balances'
            ('account','amount')
            VALUES (?,?);"""

        try:
            cursor.execute(add_account_query,
                           (new_account, starting_amount))
            print("Added new account '{}' on database".format(new_account))

        except sqlite3.IntegrityError:
            print("Account ", new_account, "already exists")
            return "Already Exists"

        conn.commit()

        # A new cost basis associated with this account has to be added
        costbasis.addCostBasis(new_account, starting_amount)

        return cursor.lastrowid


def deleteAccount(account_name):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        delete_account_query = """DELETE FROM balances WHERE account= '{}' """.format(
            account_name)
        cursor.execute(delete_account_query)

        conn.commit()


def editAccount(account_name, new_account_name):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        edit_account_query = """UPDATE balances SET account = '{}' WHERE account = '{}' """.format(
            new_account_name, account_name)
        cursor.execute(edit_account_query)

        conn.commit()


def updateBalances_withNewResult(account, amount):
    """Adds the new result to the specific acccount involved, updating its balance"""
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        currentbalance = getAccount(account)[1]
        if isinstance(amount, str):
            if '.' in amount:
                amount = int(round(float(amount[:-2]), 0))
            else:
                amount = int(amount)

        update_balance_with_new_result_query = "UPDATE balances SET amount = {} WHERE account = '{}'".format(
            currentbalance+amount, account)
        print(update_balance_with_new_result_query)

        try:
            cursor.execute(update_balance_with_new_result_query)
        except Error as e:
            print(e)

        conn.commit()


def getAccount(account):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_account_query = "SELECT * FROM balances WHERE account= '{}'".format(
            account)

        cursor.execute(get_account_query)

        result = cursor.fetchall()
        if result == []:
            return result
        return result[0]


def getAccountBalance(account):
    conn = createConnection()
    with conn:
        cursor = conn.cursor()

        get_account_query = "SELECT amount FROM balances WHERE account= '{}'".format(
            account)

        cursor.execute(get_account_query)

        result = cursor.fetchall()
        return result[0][0]


def getAllAccounts():
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_all_accounts_query = "SELECT * FROM balances"

        cursor.execute(get_all_accounts_query)

        return cursor.fetchall()
