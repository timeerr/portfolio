#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the chistoricalbalances table from cportfolio.db
"""

from datetime import datetime
import sqlite3
import os

from portfolio.utils.prices import prices
from portfolio.db.cdbhandler import cbalances
from portfolio.utils import confighandler, date_handler
from portfolio.db.dbutils import create_connection_c as create_connection


def get_balances_from_last_day():
    with create_connection() as conn:
        cursor = conn.cursor()
        tdy = datetime.today()
        tdy_start_tmstp = datetime(
            tdy.year, tdy.month, tdy.day, 0, 0, 0).timestamp()
        cursor.execute(
            f"SELECT * FROM cbalancehistory WHERE date > {tdy_start_tmstp}")
        return cursor.fetchall()


def get_balances_by_day(cryptoaccs=None):
    """ Returns a dictionary with the total btc balance of all accounts by each day """
    with create_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT date, balance_btc FROM cbalancehistory"
        if cryptoaccs is not None:
            query += f" WHERE account IN {cryptoaccs}"
        cursor.execute(query)

        result = cursor.fetchall()
        final = {d[0]: 0 for d in result}
        for entry in result:
            date, balance = entry
            final[date] += balance
        return final


def get_balances_by_day_fiat(cryptoaccs=None):
    """ Returns a dictionary with the total btc balance of all accounts by each day """
    fiat = confighandler.get_fiat_currency().lower()
    with create_connection() as conn:
        cursor = conn.cursor()
        query = f"SELECT date, balance_{fiat} FROM cbalancehistory"
        if cryptoaccs is not None:
            query += f" WHERE account IN {tuple(cryptoaccs)}"
        cursor.execute(query)

        result = cursor.fetchall()
        final = {d[0]: 0 for d in result}
        for entry in result:
            date, balance = entry
            final[date] += balance
        return final


def get_balances_by_day_tuple():
    """
    Returns a dict of tuples with the total balance of all accounts by each day
    Formatted as dict[date] = (balance_btc,balance_fiat)
    """
    fiat = confighandler.get_fiat_currency().lower()
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT date, balance_btc,balance_{fiat} FROM cbalancehistory")

        result = cursor.fetchall()
        final = {str(d[0]): (0, 0) for d in result}
        for entry in result:
            date, balance_btc, balance_fiat = entry
            date = str(date)
            final[date] = (balance_btc+final[date][0],
                           balance_fiat+final[date][1])
        return final


def get_balances_with_token(token: str):
    """Returns all entries where a token is involved"""
    token = token.lower()
    with create_connection() as conn:
        cursor = conn.cursor()
        fiat = confighandler.get_fiat_currency().lower()
        cursor.execute(
            f"SELECT date,balance_btc,balance_{fiat} FROM cbalancehistory \
            WHERE token = '{token}'")
        return cursor.fetchall()


def get_balances_with_token_tuple(token: str):
    """
    Returns all entries where a token is involved
    Formatted as dict[date] = (balance_btc,balance_fiat)
    """
    data = get_balances_with_token(token)
    final = {d[0]: (0, 0) for d in data}
    for entry in data:
        date, btc, fiat = entry
        final[date] = (final[date][0]+btc, final[date][0]+fiat)
    return final


def get_balances_with_account(account: str):
    """Returns all entries where an account is involved"""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT date,balance_btc,balance_{confighandler.get_fiat_currency().lower()} \
            FROM cbalancehistory \
            WHERE account = '{account}'")
        return cursor.fetchall()


def get_balances_with_account_tuple(account: str):
    """
    Returns all entries where an account is involved
    Formatted as dict[date] = (balance_btc,balance_fiat)
    """
    conn = create_connection()
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT date, balance_btc, balance_{confighandler.get_fiat_currency().lower()} FROM cbalancehistory \
            WHERE account='{account}'")
        data = cursor.fetchall()

    final = {d[0]: (0, 0) for d in data}
    for entry in data:
        date, btc, fiat = entry
        final[date] = (final[date][0]+btc, final[date][0]+fiat)
    return final


def add_todays_balances():
    """
    Reads balances from balances table,
    and updates the balancehistory table accordingly
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        query = """INSERT INTO 'cbalancehistory'
                (account, date, token, balance, balance_btc,
                balance_eur,balance_usd,balance_jpy)
                VALUES (?,?,?,?,?,?,?,?);"""
        # Delete previous balances from today
        todays_balances = get_balances_from_last_day()
        if len(todays_balances) > 0:
            for balance_history in todays_balances:
                _id = balance_history[0]
                delete_balance_from_id(_id)
        # Write today's balances
        accounts = cbalances.get_all_entries()
        for acc in accounts:
            # Prepare
            account, token, balance, *_ = acc
            date = int(datetime.today().timestamp())
            b_btc = prices.to_btc(token, balance)
            b_eur = prices.btc_to_fiat(b_btc, currency='eur')
            b_usd = prices.btc_to_fiat(b_btc, currency='usd')
            b_jpy = prices.btc_to_fiat(b_btc, currency='jpy')
            # Insert
            cursor.execute(query,
                           (account, date, token, balance, b_btc, b_eur, b_usd, b_jpy))
        conn.commit()


def get_first_total_balance():
    """
    Returns the sum of all balances from the earliest day
    """
    balancesbyday = get_balances_by_day()
    if len(balancesbyday.keys()) > 0:
        firstday = min(balancesbyday.keys())
        return balancesbyday[firstday]
    return 0


def get_first_total_balance_fiat():
    """
    Returns the sum of all balances from the earliest day
    """
    balancesbyday = get_balances_by_day_fiat()
    if len(balancesbyday.keys()) > 0:
        firstday = min(balancesbyday.keys())
        return balancesbyday[firstday]
    return 0


def get_all_entry_dates():
    """
    Returns all the dates with an entry on the database
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date FROM cbalancehistory")
        return list(set([i[0] for i in cursor.fetchall()]))  # No duplicates


def get_first_entry_date():
    """
    Returns timestamp of the day of the first entry on the table
    If there are no entries, returns current date
    """
    balancesbyday = get_balances_by_day()
    if len(balancesbyday.keys()) > 0:
        return int(float(min(balancesbyday.keys())))
    return datetime.today().timestamp()


def get_first_month_entry_date(month: int, year: int = datetime.today().year):
    """
    Returns the date from the first entry of
    the selected month.
    If there are no entries, returns None
    """
    all_dates = get_all_entry_dates()

    month_first_day = datetime(year, month, 1)
    month_last_day = date_handler.next_month_date(month_first_day).timestamp()
    month_first_day = month_first_day.timestamp()

    dates_from_month = [d for d in all_dates
                        if d > month_first_day and d < month_last_day]
    if len(dates_from_month) == 0:
        # No entries on selected month, no balance assumed
        return None
    # We want the earliest entry from the month
    return str(min(dates_from_month))


def get_month_first_total_balance(month: int, year: int = datetime.today().year):
    """
    Returns the total balance from the earliest entry of
    the selected month
    """
    # Get date of first entry of selected month
    # TODO: new function to get balance from specific day
    first_month_entry_date = get_first_month_entry_date(month, year)
    if first_month_entry_date is None:
        return 0
    return get_balances_by_day()[int(first_month_entry_date)]


def get_month_first_total_balance_fiat(month: int, year: int = datetime.today().year):
    """
    Returns the total balance from the earliest entry of
    the selected month.
    Expressed in fiat
    """
    # Get date of first entry of selected month
    first_month_entry_date = get_first_month_entry_date(month, year)
    if first_month_entry_date is None:
        return 0
    # We want the earliest one
    return get_balances_by_day_fiat()[int(first_month_entry_date)]


def get_current_month_first_total_balance():
    """
    Returns the total balance from the earliest entry from the current month
    """
    return get_month_first_total_balance(datetime.today().month)


def get_current_month_first_total_balance_fiat():
    """
    Returns the total balance from the earliest entry from the current month
    Expressed in fiat
    """
    return get_month_first_total_balance_fiat(datetime.today().month)


def get_account_balance_min_date(cryptoacc: str, startdate):
    """
    Returns the first entry of an account's balance after the
    selected startdate (in timestamp).
    If there are no entries, retuns current balance from that acc.
    Expressed in fiat
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        timestamps = get_all_entry_dates().sort()
        min_date = None
        # Get first entry's date
        for tm in timestamps:
            if tm >= startdate:
                min_date = tm
                break
        if min_date is None:
            # Return current balance
            return cbalances.get_total_account_balance_fiat(cryptoacc)
        # Get data
        cursor.execute(f"SELECT balance_{confighandler.get_fiat_currency()} \
                       FROM cbalancehistory WHERE date={min_date} and account='{cryptoacc}'")
        return sum([i[0] for i in cursor.fetchall()])


def get_all_entries():
    """ Returns all entries """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cbalancehistory")
        return cursor.fetchall()


def get_entries_with_token(token: str):
    """ Returns all entries where token=token """
    token = token.lower()
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM cbalancehistory WHERE token='{token}'")
        return cursor.fetchall()


def get_entries_with_account(account: str):
    """ Returns all entries where account=account """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM cbalancehistory WHERE account='{account}'")
        return cursor.fetchall()


def delete_balance_from_id(_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM cbalancehistory WHERE id = {_id}")
