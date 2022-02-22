#!/usr/bin/python3
"""
Handles all the input and output operations that use the results table from portfolio.db
"""

import sqlite3
import os
from datetime import datetime

from portfolio.db.fdbhandler import balances, strategies
from portfolio.db.dbutils import create_connection_f as create_connection


def add_result(date, account: str, strategy: str, amount: str, description: str = ""):
    with create_connection() as conn:
        cursor = conn.cursor()
        account_exists = balances.get_account(account) != []
        if not account_exists:
            # Create new account
            balances.add_account(account, 0)
        strategy_exists = strategies.get_strategy(strategy) != []
        if not strategy_exists:
            # Create new strategy
            strategies.add_strategy(strategy, 'None')

        query = """INSERT INTO 'results'
                ('date','account', 'strategy', 'amount', 'description')
                VALUES (?,?,?,?,?);"""
        cursor.execute(query,
                       (date, account, strategy, amount, description))
        conn.commit()

    # Finally, we update the previous balance on the balances table with the new result
    balances.update_balances_with_new_result(account, amount)
    strategies.update_strategies_with_new_result(strategy, amount)


def delete_result(resultid):
    with create_connection() as conn:
        cursor = conn.cursor()
        # First, we need to select the result so that we know the amount and the account involved
        # as we'll need to update the balances table aswell
        cursor.execute(
            f"SELECT account,amount FROM results WHERE id= {resultid}")
        account_from_result, amount_from_result = cursor.fetchall()[0]
        # Now, we delete the result from the results table on the database
        cursor.execute(f"DELETE FROM results WHERE id= {resultid}")
        conn.commit()

    # Finally, we update the previous balance on the balances table
    # taking the removal of the result into consideration
    balances.update_balances_with_new_result(
        account_from_result, - amount_from_result)


def update_result(resultid, new_date=None, new_account=None,
                  new_strategy=None, new_amount=None, new_description=None):
    """
    Updates a result entry
    Note that it does not update the balances or strategies, etc.
    meaning that if you change the result of an account,
    the account balance of the balances table won't be updated here
    """
    resultid = int(resultid)
    with create_connection() as conn:
        cursor = conn.cursor()
        # First, we get the current result data,
        # in case some of it doesn't need to be updated
        cursor.execute(f" SELECT * FROM results WHERE id= {resultid}")
        date, acc, strgy, amt, descr, *_ = cursor.fetchall()[0]

        # Now we check which new data has to be updated. If it does not, it stays the same
        new_date = date if new_date is None else new_date
        new_account = acc if new_account is None else new_account
        new_strategy = strgy if new_strategy is None else new_strategy
        new_amount = amt if new_amount is None else new_amount
        new_description = descr if new_description is None else new_description

        cursor.execute(f"""UPDATE results
                SET date = {new_date} ,
                account = {new_account} ,
                strategy = {new_strategy},
                amount = {new_amount},
                description = {new_description}
                WHERE id = {resultid}""")
        conn.commit()


def get_current_accounts():
    """ Returns all accounts """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT account FROM results")
        return [acc[0] for acc in cursor.fetchall()]


def get_result_all():
    """ Returns all results """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM results")
        return cursor.fetchall()


def get_result_by_id(_id):
    """Returns the result with a specific id"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM results WHERE id = {_id}")
        return cursor.fetchall()[0][0]


def get_result_date_by_id(_id):
    """Returns the result's date with a specific id"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT date FROM results WHERE id = {_id}")
        return cursor.fetchall()[0][0]


def get_result_account_by_id(_id):
    """Returns the result's account with a specific id"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT account FROM results WHERE id = {_id}")
        return cursor.fetchall()[0][0]


def get_result_strategy_by_id(_id):
    """Returns the result's strategy with a specific id"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT strategy FROM results WHERE id = {_id}")
        return cursor.fetchall()[0][0]


def get_result_amount_by_id(_id):
    """Returns the result's amount with a specific id"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT amount FROM results WHERE id = {_id}")
        return cursor.fetchall()[0][0]


def get_results_from_query(start_date: datetime = datetime(1980, 1, 1),
                           end_date: datetime = datetime(3000, 1, 1),
                           strategy="All", account="All"):
    """
    Returns rows with certain start&end dates + account.
    Dates get passed as datetimes
    """
    with create_connection() as conn:
        cursor = conn.cursor()

        query = "SELECT * FROM results"
        if start_date == end_date == None and account == strategy == "All":
            return cursor.execute(query).fetchall()
        start_date = start_date.timestamp()
        end_date = end_date.timestamp()

        query += f" WHERE date>={start_date} AND date<={end_date}"
        if account != "All":
            query += f" AND account = '{account}'"
        if strategy != "All":
            query += f" AND STRATEGY = '{strategy}'"

        cursor.execute(query)
        return cursor.fetchall()


def get_strategies_from_account(account: str):
    """Searchs for all the strategies where an account is involved"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT strategy FROM results WHERE account = '{account}'")
        return set([i[0] for i in cursor.fetchall()])
