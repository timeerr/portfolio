#!/usr/bin/python3
"""
Handles all the input and output operations that use the results table from portfolio.db
"""

import sqlite3
import os
from datetime import datetime
from gui.dbhandler import balances, strategies


PATH_TO_DB = os.path.join('database', 'portfolio.db')


def createConnection(path_to_db=PATH_TO_DB):
    conn = None

    conn = sqlite3.connect(path_to_db)

    return conn


def addResult(date, account, strategy, amount, description=""):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        account_exists = balances.getAccount(account)
        if account_exists == []:
            # Create new account
            balances.addAccount(account, 0)
        strategy_exists = strategies.getStrategy(strategy)
        if strategy_exists == []:
            # Create new strategy
            # Markettype defaults as "None"
            strategies.addStrategy(strategy, 'None')

        add_result_query = """INSERT INTO 'results'
            ('date','account', 'strategy', 'amount', 'description')
            VALUES (?,?,?,?,?);"""
        cursor.execute(add_result_query, (date, account,
                                          strategy, amount, description))

        conn.commit()

        # Finally, we update the previous balance on the balances table with the new result
        balances.updateBalances_withNewResult(account, amount)
        strategies.updateStrategies_withNewResult(strategy, amount)


def deleteResult(resultid):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        # First, we need to select the result so that we know the amount and the account involved
        # as we'll need to update the balances table aswell
        select_result_query = """SELECT account,amount FROM results WHERE id= %d""" % resultid
        result = cursor.execute(
            select_result_query).fetchall()
        print(result)
        account_from_result = result[0][0]
        amount_from_result = result[0][1]

        # Now, we delete the result from the results table on the database
        delete_result_query = """DELETE FROM results WHERE id= %d""" % resultid
        cursor.execute(delete_result_query)

        conn.commit()

        # Finally, we update the previous balance on the balances table
        # taking the removal of the result into consideration
        balances.updateBalances_withNewResult(
            account_from_result, -amount_from_result)


def updateResult(resultid, newdate=None, newaccount=None, newstrategy=None, newamount=None):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        # First, we select the current result data, in case some of it does not need to be updated
        current_result_query = """ SELECT * FROM results WHERE id= %d """ % resultid
        cursor.execute(current_result_query)
        r = cursor.fetchall()  # Here we get the actual row. Now we have to disect it
        print(cursor.fetchall())

        currentdate = r[0][1]
        currentaccount = r[0][2]
        currentstrategy = r[0][3]
        currentamount = r[0][4]

        # Now we check which new data has to be updated. If it does not, it stays the same
        if newdate is None:
            newdate = currentdate
        if newaccount is None:
            newaccount = currentaccount
        if newstrategy is None:
            newstrategy = currentstrategy
        if newamount is None:
            newaccount = currentamount

        update_result_query = """UPDATE results
            SET date = ? ,
                account = ? ,
                amount = ?
                WHERE id = ?
        """

        cursor.execute(update_result_query,
                       (newdate, newaccount, newamount, resultid))
        conn.commit()


def getCurrentAccounts():
    """ Returns all accounts """
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_account_query = """SELECT DISTINCT account FROM results"""
        cursor.execute(get_account_query)

        accs = cursor.fetchall()
        result = []

        for a in accs:
            result.append(a[0])

        return result


def getResult_all():
    """ Returns all results """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_results_all = """SELECT * FROM results"""

        cursor.execute(get_results_all)
        return cursor.fetchall()


def getResults_fromQuery(start_date=datetime(1900, 1, 1), end_date=datetime(3000, 1, 1),
                         strategy="All", account="All"):
    """
    Executing query to return rows with certain start&end dates + account.
    Dates get passed as datetimes
    """

    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_results_query = f"SELECT * FROM results WHERE date>={start_date.timestamp()} AND date<={end_date.timestamp()}"
        account_query_addon = """ AND account = '{}'""".format(account)
        strategy_query_addon = """ AND STRATEGY = '{}'""".format(strategy)

        if start_date == end_date == None and account == "All" and strategy == "All":
            return cursor.execute("SELECT * FROM results").fetchall()

        if account != "All":
            get_results_query += account_query_addon
        if strategy != "All":
            get_results_query += strategy_query_addon
        cursor.execute(get_results_query)

        return cursor.fetchall()
