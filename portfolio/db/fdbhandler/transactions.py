#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the transactions table from portfolio.db
"""

import os
import logging
from datetime import datetime
import sqlite3

from portfolio.db.fdbhandler import balances, costbasis
from portfolio.db.dbutils import create_connection_f as create_connection


def add_transaction(date, account_send: str, amount: float,
                    account_receive: str, depositwithdrawal: str,
                    description: str = ""):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()

        # If accounts do not exist, they get created
        acc_send_exists = balances.get_account(account_send) != []
        acc_receive_exists = balances.get_account(account_receive) != []
        if not acc_send_exists:
            balances.add_account(account_send, 0)
        if not acc_receive_exists:
            balances.add_account(account_receive, 0)

        # Check args
        if depositwithdrawal not in (0, 1, -1):
            raise ValueError(
                "deposit/withdrawal must be 1/-1, respectively, or 0 if normal trnasfer")
        amount = int(amount)

        # Add
        query = """INSERT INTO 'transactions'
        ('date', 'account_send', 'amount', 'account_receive',
         'depositwithdrawal','description')
        VALUES (?,?,?,?,?,?)"""
        cursor.execute(query,
                       (date, account_send, amount,
                        account_receive, depositwithdrawal, description))
        conn.commit()

    # Finally, we update the account balance on the balance and costbasis tables
    # Sender account
    balances.update_balances_with_new_result(account_send, -amount)
    balances.update_balances_with_new_result(account_receive, amount)
    costbasis.update_cost_basis_with_new_transaction(account_send, -amount)
    costbasis.update_cost_basis_with_new_transaction(account_receive, amount)


def delete_transaction(transactionid):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        # First, we need to get it
        # so that we know the amount and the account involved,
        # as we new to update the balances table aswell
        select_query = f"SELECT account_send, account_receive, amount FROM transactions WHERE id= {transactionid}"
        result = cursor.execute(select_query).fetchall()[0]
        sender, receiver, amount, *_ = result
        # Now, we delete the result from the results table on the database
        cursor.execute(f"DELETE FROM transactions WHERE id= {transactionid}")
        conn.commit()
        # Finally, we update the previous balance on the balances and cost basis tables,
        # taking the removal of the transaction into consideration
        balances.update_balances_with_new_result(sender, amount)
        balances.update_balances_with_new_result(receiver, -amount)
        costbasis.update_cost_basis_with_new_transaction(sender, amount)
        costbasis.update_cost_basis_with_new_transaction(receiver, - amount)


def update_transaction(transactionid,
                       new_date=None, new_sender: str = None,
                       new_amount: float = None, new_receiver: str = None,
                       new_d_or_w: float = None, new_description: str = None):
    """
    Updates a transaction entry
    Note that it does not update the balances or strategies, etc.
    Meaning that if you change the transaction of an account,
    the account balance+costbasis of the balances+costbasis tables won't be updated here
    """
    transactionid = int(transactionid)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        # First, we select the current result data, in case some of it does not need to be updated
        cursor.execute(
            f" SELECT * FROM transactions WHERE id= {transactionid}")
        r = cursor.fetchall()[0]
        date, sender, amt, receiver, _type, d_or_w, descr, *_ = r

        new_date = date if new_date is None else new_date
        new_sender = sender if new_sender is None else new_sender
        new_amount = amt if new_amount is None else new_amount
        new_receiver = receiver if new_receiver is None else new_receiver
        new_d_or_w = d_or_w if new_d_or_w is None else new_d_or_w
        new_description = descr if new_description is None else new_description

        cursor.execute(f"""UPDATE transactions
                SET date = {new_date} ,
                account_send = {new_sender} ,
                amount = {new_amount},
                account_receive = {new_receiver},
                depositwithdrawal = {new_d_or_w},
                description = {new_description}
                WHERE id = {transactionid}""")
        conn.commit()
        logging.info(
            f"Updated {r} \nChanged to {new_date}{new_sender}{new_amount}{new_receiver}{new_d_or_w}{new_description}")


def get_transactions_all():
    """ Returns all transactions """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        return cursor.fetchall()


def get_transaction_by_id(_id):
    """Returns the transaction with a specific id"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM transactions WHERE id = {_id}")
        return cursor.fetchall()[0][0]


def get_transaction_amount_by_id(_id):
    """Returns the transaction's amount with a specific id"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT amount FROM transactions WHERE id = {_id}")
        return cursor.fetchall()[0][0]


def get_transaction_date_by_id(_id):
    """Returns the transaction's date with a specific id"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT date FROM transactions WHERE id = {_id}")
        return cursor.fetchall()[0][0]


def get_transaction_sender_account_by_id(_id):
    """Returns the transaction's sender account with a specific id"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT account_send FROM transactions WHERE id = {_id}")
        return cursor.fetchall()[0][0]


def get_transaction_receiver_account_by_id(_id):
    """Returns the transaction's receive account with a specific id"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT account_receive FROM transactions WHERE id = {_id}")
        return cursor.fetchall()[0][0]


def get_transactions_from_query(start_date=datetime(1900, 1, 1),
                                end_date=datetime(3000, 1, 1),
                                senderaccount="All", receiveraccount="All"):
    """
    Return rows with each result
    that satisfies the args
    """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()

        query = "SELECT * FROM transactions"
        if start_date == end_date == None and senderaccount == receiveraccount == "All":
            return cursor.execute(query).fetchall()
        start_date = start_date.timestamp()
        end_date = end_date.timestamp()

        query += f" WHERE date>={start_date} AND date<={end_date}"
        if senderaccount != "All":
            query += f" AND account_send = '{senderaccount}'"
        if receiveraccount != "All":
            query += f" AND account_receive = '{receiveraccount}'"

        cursor.execute(query)
        return cursor.fetchall()


def get_all_sender_accounts():
    """ Returns all send accounts from db """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(" SELECT account_send FROM transactions ")
        return cursor.fetchall()


def get_all_receiver_accounts():
    """ Returns all receive accounts from db """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(" SELECT account_receive FROM transactions ")
        return cursor.fetchall()
