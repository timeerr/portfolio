#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the costbasis table from portfolio.db
"""

import sqlite3
import os

from portfolio.db.fdbhandler import transactions

PATH_TO_DB = os.path.join('database', 'portfolio.db')


def createConnection(path_to_db=PATH_TO_DB):
    conn = None

    try:
        conn = sqlite3.connect(path_to_db)
    except sqlite3.OperationalError as e:
        print(e, path_to_db)

    return conn


def addCostBasis(new_account, starting_costbasis):
    conn = createConnection()
    with conn:
        cursor = conn.cursor()

        add_cb_query = """INSERT INTO 'costbasis'
            ('account','amount')
            VALUES (?,?);"""

        try:
            cursor.execute(add_cb_query,
                           (new_account, starting_costbasis))
            print("Added new account's '{}' costbasis on database".format(new_account))

        except sqlite3.IntegrityError:
            print("Account ", new_account, " cost basis already exists")
            return "Already Exists"

        conn.commit()

        return cursor.lastrowid


def editCostBasis(account_name, new_account_name):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        edit_account_query = """UPDATE costbasis SET account = '{}' WHERE account = '{}' """.format(
            new_account_name, account_name)
        cursor.execute(edit_account_query)

        conn.commit()


def updateCostBasis_withNewTransaction(account, amount):
    """Adds the new transaction to the specific account involved, updating its cost basis"""
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        currentbalance = getCostBasis(account)
        if isinstance(amount, str):
            if '.' in amount:
                amount = int(round(float(amount[:-2]), 0))
            else:
                amount = int(amount)

        update_cb_with_new_result_query = "UPDATE costbasis SET amount = {} WHERE account = '{}'".format(
            currentbalance+amount, account)

        cursor.execute(update_cb_with_new_result_query)

        conn.commit()


def updateCostBasis():
    """Reads all transactions, and sums deposits and withdrawal to update each account's cost basis"""

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        # Getting current cost basis
        all_transactions = transactions.getTransactions_All()
        accounts_costbasis = {}

        for t in all_transactions:
            sendaccount = t[2]
            amount = t[3]
            receiveaccount = t[4]

            if sendaccount not in accounts_costbasis.keys():
                accounts_costbasis[sendaccount] = 0
            if receiveaccount not in accounts_costbasis.keys():
                accounts_costbasis[receiveaccount] = 0

            accounts_costbasis[sendaccount] += -amount
            accounts_costbasis[receiveaccount] += amount

        # Updating table
        insert_account_query = """INSERT INTO 'costbasis'
        ('account', 'amount')
        VALUES (?,?);"""
        current_accounts_in_table = getCurrentAccountsInTable()

        for acc in accounts_costbasis:
            if acc not in current_accounts_in_table:
                # Adding new account data
                cursor.execute(insert_account_query,
                               (acc, accounts_costbasis[acc]))
            else:
                # Updating acount data
                update_cost_basis_query = """UPDATE costbasis
                    SET amount = ? 
                    WHERE account = ? """
                cursor.execute(update_cost_basis_query,
                               (accounts_costbasis[acc], acc))

        conn.commit()


def getCurrentAccountsInTable():
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        # Getting all accounts in table
        get_accounts_query = """SELECT account from costbasis"""
        cursor.execute(get_accounts_query)

        accs = cursor.fetchall()
        res = []
        for acc in accs:
            res.append(acc[0])

        return res


def getCostBasis(account):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_costbasis_query = """SELECT amount FROM costbasis WHERE account = '{}'""".format(
            account)

        cursor.execute(get_costbasis_query)

        res = cursor.fetchall()
        if res == []:
            return 0
        return res[0][0]
