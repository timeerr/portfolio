#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the chistoricalbalances table from portfolio.db
"""

from datetime import datetime
import sqlite3
import os

from portfolio.db.fdbhandler import balances
from portfolio.utils import date_handler
from portfolio.db.dbutils import create_connection_f as create_connection


def get_balances_from_last_day():
    with create_connection() as conn:
        cursor = conn.cursor()
        tdy = datetime.today()
        tdy_start_tmstp = datetime(
            tdy.year, tdy.month, tdy.day, 0, 0, 0).timestamp()
        cursor.execute(
            f"SELECT * FROM balancehistory WHERE date > {tdy_start_tmstp}")
        return cursor.fetchall()


def get_balances_by_day(fiataccs=None):
    """
    Returns a dictionary with the total balance
    of all accounts by each day
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT date, balance FROM balancehistory"
        if fiataccs is not None:
            query += f" WHERE account IN {tuple(fiataccs)}"
        cursor.execute(query)

        result = cursor.fetchall()
        final = {d[0]: 0 for d in result}
        for entry in result:
            date, balance = entry
            final[date] += balance
        return final


def add_todays_balances():
    """
    Reads balances from balances table,
    and updates the balancehistory table accordingly
    """
    conn = create_connection()
    with create_connection() as conn:
        cursor = conn.cursor()
        todays_balances = get_balances_from_last_day()
        current_accounts = balances.get_all_accounts()
        # Delete previous balances from today
        # (that way we'll avoid dealing with new accounts)
        for balance_history in todays_balances:
            _id = balance_history[0]
            delete_balance_from_id(_id)
        # Write today's balances
        query = "INSERT INTO 'balancehistory' (account, date, balance) VALUES (?,?,?);"
        for acc in current_accounts:
            account, balance, *_ = acc
            cursor.execute(query,
                           (account, int(datetime.today().timestamp()), balance))
        conn.commit()


def get_first_total_balance():
    """
    Returns the sum of all balances from the earliest day

    If there is no historical data yet, returns 0
    """
    balancesbyday = get_balances_by_day()
    if len(balancesbyday.keys()) > 0:
        firstday = min(balancesbyday.keys())
        return balancesbyday[firstday]
    return 0


def get_all_entry_dates():
    """Returns all the dates with an entry on the database"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date FROM balancehistory")
        return list(set([i[0] for i in cursor.fetchall()]))


def get_first_month_entry_date(month: float, year: float = datetime.today().year):
    """
    Returns the date from the first entry of
    the selected month.
    If there are no entries, returns None
    """
    all_dates = get_all_entry_dates()

    selected_month_first_day = datetime(year, month, 1).timestamp()
    selected_month_last_day = date_handler.next_month_date(
        datetime(year, month, 1)).timestamp()

    dates_from_month = [d for d in all_dates if d >
                        selected_month_first_day and d < selected_month_last_day]
    if len(dates_from_month) == 0:
        # No entries on selected month, no balance assumed
        return None
    # We want the earliest entry from the month
    return str(min(dates_from_month))


def get_month_first_total_balance(month: float, year: float = datetime.today().year):
    """
    Returns the total balance from the
    earliest entry of the month selected
    """
    # Get date of first entry of selected month
    # TODO: new function to get balance from specific day
    first_month_entry_date = get_first_month_entry_date(month, year)
    if first_month_entry_date is None:
        return 0
    return get_balances_by_day()[int(first_month_entry_date)]


def get_first_entry_date():
    """
    Returns timestamp of the day of the first entry ont he table
    """
    balancesbyday = get_balances_by_day()
    if len(balancesbyday.keys()) > 0:
        return int(float(min(balancesbyday.keys())))
    return datetime.today().timestamp()


def get_current_month_first_total_balance():
    """
    Returns the total balance from the earliest entry from the current month
    """
    return get_month_first_total_balance(datetime.today().month)


def delete_balance_from_id(_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM balancehistory WHERE id= {_id}")
