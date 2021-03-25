#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the transactions table from portfolio.db
"""

from datetime import datetime
import sqlite3
import os

from gui.dbhandler import balances, costbasis


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

    # Finally, we update the account balance on the balance and costbasis tables
    # Sender account
    balances.updateBalances_withNewResult(account_send, -amount)
    balances.updateBalances_withNewResult(account_receive, amount)
    costbasis.updateCostBasis_withNewTransaction(account_send, -amount)
    costbasis.updateCostBasis_withNewTransaction(account_receive, amount)


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

        # Finally, we update the previous balance on the balances and cost basis tables,
        # taking the removal of the transaction into consideration
        balances.updateBalances_withNewResult(
            account_send, amount_from_transaction)
        balances.updateBalances_withNewResult(
            account_receive, -amount_from_transaction)
        costbasis.updateCostBasis_withNewTransaction(
            account_send, amount_from_transaction)
        costbasis.updateCostBasis_withNewTransaction(
            account_receive, - amount_from_transaction)


def updateTransaction(transactionid, newdate=None, newsenderaccount=None, newamount=None, newreceiveraccount=None, newtype=None):
    """
    Updates a transaction entry
    Note that it does not update the balances or strategies, etc.
    Meaning that if you change the transaction of an account,
    the account balance+costbasis of the balances+costbasis tables won't be updated here
    """
    transactionid = int(transactionid)

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        # First, we select the current result data, in case some of it does not need to be updated
        current_transaction_query = """ SELECT * FROM transactions WHERE id= %d """ % transactionid
        cursor.execute(current_transaction_query)
        r = cursor.fetchall()  # Here we get the actual row. Now we have to disect it

        currentdate = r[0][1]
        currentsenderaccount = r[0][2]
        currentamount = r[0][3]
        currentreceiveraccount = r[0][4]
        currenttype = r[0][5]

        # Now we check which new data has to be updated. If it does not, it stays the same
        if newdate is None:
            newdate = currentdate
        if newsenderaccount is None:
            newsenderaccount = currentsenderaccount
        if newamount is None:
            newamount = currentamount
        if newreceiveraccount is None:
            newreceiveraccount = currentreceiveraccount
        if newtype is None:
            newtype = currenttype

        update_transaction_query = """UPDATE transactions
            SET date = ? ,
                account_send = ? ,
                amount = ?,
                account_receive = ?,
                depositwithdrawal = ?
                WHERE id = ?
        """

        cursor.execute(update_transaction_query, (newdate, newsenderaccount,
                                                  newamount, newreceiveraccount, newtype, transactionid))
        conn.commit()


def getTransactions_All():
    """ Returns all transactions """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_transactions_all = """SELECT * FROM transactions"""

        cursor.execute(get_transactions_all)
        return cursor.fetchall()


def getTransactionById(_id):
    """
    Returns the transaction with a specific id
    """
    conn = createConnection()
    with conn:
        cursor = conn.cursor()

        get_transaction_by_id_query = "SELECT * FROM transactions WHERE id = {}".format(
            _id)

        cursor.execute(get_transaction_by_id_query)
        return cursor.fetchall()[0][0]


def getTransactionAmountById(_id):
    """
    Returns the transaction's amount with a specific id
    """
    conn = createConnection()
    with conn:
        cursor = conn.cursor()

        get_transaction_amount_by_id_query = "SELECT amount FROM transactions WHERE id = {}".format(
            _id)

        cursor.execute(get_transaction_amount_by_id_query)
        return cursor.fetchall()[0][0]


def getTransactionDateById(_id):
    """
    Returns the transaction's date with a specific id
    """
    conn = createConnection()
    with conn:
        cursor = conn.cursor()

        get_transaction_date_by_id_query = "SELECT date FROM transactions WHERE id = {}".format(
            _id)

        cursor.execute(get_transaction_date_by_id_query)
        return cursor.fetchall()[0][0]


def getTransactionSenderAccountById(_id):
    """
    Returns the transaction's sender account with a specific id
    """
    conn = createConnection()
    with conn:
        cursor = conn.cursor()

        get_transaction_senderaccount_by_id_query = "SELECT account_send FROM transactions WHERE id = {}".format(
            _id)

        cursor.execute(get_transaction_senderaccount_by_id_query)
        return cursor.fetchall()[0][0]


def getTransactionReceiverAccountById(_id):
    """
    Returns the transaction's receive account with a specific id
    """
    conn = createConnection()
    with conn:
        cursor = conn.cursor()

        get_transaction_receiveraccount_by_id_query = "SELECT account_receive FROM transactions WHERE id = {}".format(
            _id)

        cursor.execute(get_transaction_receiveraccount_by_id_query)
        return cursor.fetchall()[0][0]


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
