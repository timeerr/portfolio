#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime

import sqlite3
from datetime import datetime
from dbhandler import transactions
import os

PATH_TO_DB = os.path.join('database', 'portfolio.db')


def createConnection(path_to_db=PATH_TO_DB):
    conn = None

    try:
        conn = sqlite3.connect(path_to_db)
    except Error as e:
        print(e)

    return conn


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

        for acc in accounts_costbasis.keys():
            current_accounts_in_table
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
        else:
            return res[0][0]
