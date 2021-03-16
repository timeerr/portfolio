#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the transactions table from portfolio.db
"""

from datetime import datetime
import sqlite3
import os

from . import balances


PATH_TO_DB = os.path.join('database', 'portfolio.db')


def createConnection(path_to_db=PATH_TO_DB):
    conn = None

    try:
        conn = sqlite3.connect(path_to_db)
    except Error as e:
        print(e)

    return conn


def addTransaction(date, account_send, amount, account_receive, depositwithdrawal):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        # If accounts do not exist, they get created
        account_send_exists = balances.getAccount(account_send)
        account_receive_exists = balances.getAccount(account_receive)
        if account_send_exists == []:
            balances.addAccount(account_send, 0)
        if account_receive_exists == []:
            balances.addAccount(account_receive, 0)

        # Amount part
        if depositwithdrawal not in [0, 1, -1]:
            raise TypeError(
                "deposit/withdrawal must be 1/-1, respectively, or 0 if normal trnasfer")
        if isinstance(amount, str):
            amount = int(float(amount))
        elif isinstance(amount, float):
            amount = int(round(amount, 0))

        # Finally, adding transaction on db
        add_transaction_query = """INSERT INTO 'transactions'
        ('date', 'account_send', 'amount', 'account_receive', 'depositwithdrawal')
        VALUES (?,?,?,?,?)"""

        cursor.execute(add_transaction_query, (date, account_send,
                                               amount, account_receive, depositwithdrawal))
        conn.commit()

    # Finally, we update the account balance on the balance table
    # Sender account
    balances.updateBalances_withNewResult(account_send, -amount)
    balances.updateBalances_withNewResult(account_receive, amount)


def deleteTransaction(transactionid):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        # First, we need to select the result
        # so that we know the amount and the account involved,
        # as we new to update the balances table aswell
        select_transaction_query = """SELECT account_send, account_receive, amount FROM transactions WHERE id= %d""" % transactionid
        result = cursor.execute(
            select_transaction_query).fetchall()
        print(result)
        account_send = result[0][0]
        account_receive = result[0][1]
        amount_from_transaction = result[0][2]

        # Now, we delete the result from the results table on the database
        delete_transaction_query = """DELETE FROM transactions WHERE id= %d""" % transactionid
        cursor.execute(delete_transaction_query)

        conn.commit()

        # Finally, we update the previous balance on the balances table,
        # taking the removal of the transaction into consideration
        balances.updateBalances_withNewResult(
            account_send, amount_from_transaction)
        balances.updateBalances_withNewResult(
            account_receive, -amount_from_transaction)


def getTransactions_All():
    """ Returns all transactions """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_transactions_all = """SELECT * FROM transactions"""

        cursor.execute(get_transactions_all)
        return cursor.fetchall()


def getTransactions_fromQuery(start_date=datetime(1900, 1, 1), end_date=datetime(3000, 1, 1),
                              senderaccount="All", receiveraccount="All"):
    """ Executing query to return rows with each result that satisfies the args """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_transactions_query = f"SELECT * FROM transactions WHERE date>={start_date.timestamp()} AND date<={end_date.timestamp()}"

        senderaccount_query_addon = """ AND account_send = '{}'""".format(
            senderaccount)
        receiveraccount_query_addon = """ AND account_receive = '{}'""".format(
            receiveraccount)

        if senderaccount != "All":
            get_transactions_query += senderaccount_query_addon
        if receiveraccount != "All":
            get_transactions_query += receiveraccount_query_addon

        cursor.execute(get_transactions_query)

        return cursor.fetchall()


def getAllSenderAccounts():
    """ Returns all send accounts from db """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_all_senders_query = """ SELECT account_send FROM transactions """

        cursor.execute(get_all_senders_query)

        return cursor.fetchall()


def getAllReceiverAccounts():
    """ Returns all receive accounts from db """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_all_receivers_query = """ SELECT account_receive FROM transactions """

        cursor.execute(get_all_receivers_query)

        return cursor.fetchall()
