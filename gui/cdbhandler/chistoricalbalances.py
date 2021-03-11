#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime

from datetime import datetime
import sqlite3
import os

from cdbhandler import cbalances
from prices import prices

PATH_TO_DB = os.path.join('database', 'cportfolio.db')


def createConnection(path_to_db=PATH_TO_DB):
    conn = None

    try:
        conn = sqlite3.connect(path_to_db)
    except Error as e:
        print(e)

    return conn


def getBalancesFromLastDay():
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        todays_start_timestamp = datetime(
            datetime.today().year, datetime.today().month, datetime.today().day, 0, 0, 0).timestamp()
        get_balances_from_last_day_query = "SELECT * FROM cbalancehistory WHERE date > %d" % todays_start_timestamp

        cursor.execute(get_balances_from_last_day_query)

        return(cursor.fetchall())


def addTodaysBalances():
    """ Reads balances from balances table, and updates the balancehistory table accordingly"""
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        todays_balances = getBalancesFromLastDay()
        current_accounts = cbalances.getAllEntries()

        add_balance_history_query = """INSERT INTO 'cbalancehistory'
                                (account, date, token, balance, balance_btc) 
                                VALUES (?,?,?,?,?);"""
        today = datetime.today().timestamp()

        if len(todays_balances) > 0:
            # Delete previous balances from today (that way we'll avoid dealing with new accounts)
            for balance_history in todays_balances:
                _id = balance_history[0]
                deleteBalanceFromId(_id)

        # Write today's balances
        for acc in current_accounts:
            account = acc[0]
            token = acc[1]
            balance = acc[2]
            balance_btc = prices.toBTC(token, balance)

            cursor.execute(add_balance_history_query,
                           (account, today, token, balance, balance_btc))


def deleteBalanceFromId(_id):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        delete_balance_query = """DELETE FROM cbalancehistory WHERE id= %d""" % _id

        cursor.execute(delete_balance_query)
