#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the ctransactions table from cportfolio.db
"""

from datetime import datetime
import sqlite3
import os

from portfolio.db.cdbhandler import cbalances


PATH_TO_DB = os.path.join('database', 'cportfolio.db')


def createConnection(path_to_db=PATH_TO_DB):
    conn = None

    try:
        conn = sqlite3.connect(path_to_db)
    except sqlite3.OperationalError as e:
        print(e, path_to_db)
    return conn


def addTransaction(date, account_send, token, amount, account_receive, depositwithdrawal):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        # If accounts do not exist, they get created
        account_send_exists = cbalances.getAccountWithToken(
            account_send, token)
        account_receive_exists = cbalances.getAccountWithToken(
            account_receive, token)
        if account_send_exists == [] and account_receive_exists == []:
            print(
                "accounts involved in transaction don't exist. Maybe add them first manually?")
            return

        # Amount part
        if isinstance(amount, str):
            amount = int(float(amount))
        elif isinstance(amount, float):
            amount = int(round(amount, 0))

        # Finally, adding transaction on db
        add_transaction_query = """INSERT INTO 'ctransactions'
        ('date', 'account_send', 'token', 'amount', 'account_receive', 'depositwithdrawal')
        VALUES (?,?,?,?,?,?)"""

        cursor.execute(add_transaction_query, (date, account_send, token,
                                               amount, account_receive, depositwithdrawal))
        conn.commit()

#    # Finally, we update the account balance on the balance table
#    # Sender account
#    cbalances.updateBalances_withNewTransaction(account_send, token, -amount)
#    cbalances.updateBalances_withNewTransaction(account_receive, token, amount)


def deleteTransaction(transactionid):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        # First, we need to select the result so that we know the amount and the account involved, as we new to update the balances table aswell
        select_transaction_query = """SELECT account_send, account_receive, amount FROM ctransactions WHERE id= %d""" % transactionid
        cursor.execute(select_transaction_query).fetchall()

        # Now, we delete the result from the results table on the database
        delete_transaction_query = """DELETE FROM ctransactions WHERE id= %d""" % transactionid
        cursor.execute(delete_transaction_query)

        conn.commit()

#        # Finally, we update the previous balance on the balances table, taking the removal of the transaction into consideration
#        account_send = result[0][0]
#        account_receive = result[0][1]
#        amount_from_transaction = result[0][2]
#        cbalances.updateBalances_withNewResult(
#            account_send, amount_from_transaction)
#        cbalances.updateBalances_withNewResult(
#            account_receive, -amount_from_transaction)


def getTransactions_All():
    """ Returns all transactions """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_transactions_all = """SELECT * FROM ctransactions"""

        cursor.execute(get_transactions_all)
        return cursor.fetchall()


def getTransactions_fromQuery(start_date=datetime(1900, 1, 1), end_date=datetime(3000, 1, 1), senderaccount="All", receiveraccount="All"):
    """ Executing query to return rows with each result that satisfies the args """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_transactions_query = f"SELECT * FROM ctransactions WHERE date>={start_date.timestamp()} AND date<={end_date.timestamp()}"

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
    """ Returns all accounts that have been senders on the db """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_all_senders_query = """ SELECT account_send FROM ctransactions """

        cursor.execute(get_all_senders_query)

        return cursor.fetchall()


def getAllReceiverAccounts():
    """ Returns all receive accounts from db """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_all_receivers_query = """ SELECT account_receive FROM ctransactions """

        cursor.execute(get_all_receivers_query)

        return cursor.fetchall()
