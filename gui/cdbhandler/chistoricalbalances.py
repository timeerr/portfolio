#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime
"""
Handles all the input and output operations that use the chistoricalbalances table from cportfolio.db
"""

from datetime import datetime
import sqlite3
import os

from gui.prices import prices
from gui.cdbhandler import cbalances
from gui import confighandler
from gui import utils

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

        return cursor.fetchall()


def getBalancesByDay(cryptoaccs=None):
    """ Returns a dictionary with the total btc balance of all accounts by each day """
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        if cryptoaccs is None:
            get_all_balances = "SELECT date, balance_btc FROM cbalancehistory"
            cursor.execute(get_all_balances)
        elif len(cryptoaccs) == 0:
            return {}
        else:
            if len(cryptoaccs) > 1:
                cryptoaccs = tuple(cryptoaccs)
                get_balances_by_day = f"SELECT date, balance_btc FROM cbalancehistory WHERE account IN {cryptoaccs}"
            else:
                cryptoaccs = cryptoaccs[0]
                get_balances_by_day = f"SELECT date,balance_btc FROM cbalancehistory WHERE account = '{cryptoaccs}'"

            cursor.execute(get_balances_by_day)

        result = cursor.fetchall()
        balances_by_date = {}
        for entry in result:
            date = str(entry[0])
            balance = entry[1]
            if date in balances_by_date.keys():
                balances_by_date[date] += balance
            else:
                balances_by_date[date] = balance

        return balances_by_date


def getBalancesByDayTuple():
    """ 
    Returns a dict of tuples with the total balance of all accounts by each day 
    Formatted as dict[date] = (balance_btc,balance_fiat)
    """
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_all_balances = f"SELECT date, balance_btc,balance_{confighandler.get_fiat_currency().lower()} FROM cbalancehistory"

        cursor.execute(get_all_balances)
        result = cursor.fetchall()
        balances_by_date = {}
        for entry in result:
            date = str(entry[0])
            balance_btc = entry[1]
            balance_fiat = entry[2]
            if date in balances_by_date.keys():
                new_balance_btc = balances_by_date[date][0] + balance_btc
                new_balance_fiat = balances_by_date[date][1] + balance_fiat
                balances_by_date[date] = (new_balance_btc, new_balance_fiat)
            else:
                balances_by_date[date] = (balance_btc, balance_fiat)

        return balances_by_date


def getBalancesByDay_fiat(cryptoaccs=None):
    """ Returns a dictionary with the total btc balance of all accounts by each day """
    conn = createConnection()

    FIAT_CURRENCY = confighandler.get_fiat_currency().lower()

    with conn:
        cursor = conn.cursor()

        if cryptoaccs is None:
            get_all_balances = f"SELECT date, balance_{FIAT_CURRENCY} FROM cbalancehistory"
            cursor.execute(get_all_balances)
        elif len(cryptoaccs) == 0:
            return {}
        else:
            if len(cryptoaccs) > 1:
                cryptoaccs = tuple(cryptoaccs)
                get_balances_by_day_fiat = f"SELECT date, balance_{FIAT_CURRENCY} FROM cbalancehistory WHERE account IN {cryptoaccs}"
            else:
                cryptoaccs = cryptoaccs[0]
                get_balances_by_day_fiat = f"SELECT date, balance_{FIAT_CURRENCY} FROM cbalancehistory WHERE account = '{cryptoaccs}'"

            cursor.execute(get_balances_by_day_fiat)

        result = cursor.fetchall()
        balances_by_date = {}
        for entry in result:
            date = str(entry[0])
            balance = entry[1]
            if date in balances_by_date.keys():
                balances_by_date[date] += balance
            else:
                balances_by_date[date] = balance

        return balances_by_date


def getBalancesWithToken(token):
    """Returns all entries where a token is involved"""
    token = token.lower()
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_balances_with_token = f"SELECT date,balance_btc,balance_{confighandler.get_fiat_currency().lower()} FROM cbalancehistory WHERE token = '{token}'"

        cursor.execute(get_balances_with_token)
        result = cursor.fetchall()
        balances_by_date = {}
        for entry in result:
            date = str(entry[0])
            balance = entry[1]
            if date in balances_by_date.keys():
                balances_by_date[date] += balance
            else:
                balances_by_date[date] = balance

        return balances_by_date


def getBalancesWithTokenTuple(token):
    """
    Returns all entries where a token is involved
    Formatted as dict[date] = (balance_btc,balance_fiat)
    """
    token = token.lower()
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_balances_with_token = f"SELECT date,balance_btc,balance_{confighandler.get_fiat_currency().lower()} FROM cbalancehistory WHERE token = '{token}'"

        cursor.execute(get_balances_with_token)
        result = cursor.fetchall()
        balances_by_date = {}
        for entry in result:
            date = str(entry[0])
            balance_btc = entry[1]
            balance_fiat = entry[2]
            if date in balances_by_date.keys():
                new_balance_btc = balances_by_date[date][0] + balance_btc
                new_balance_fiat = balances_by_date[date][1] + balance_fiat
                balances_by_date[date] = (new_balance_btc, new_balance_fiat)
            else:
                balances_by_date[date] = (balance_btc, balance_fiat)

        return balances_by_date


def getBalancesWithAccount(account):
    """Returns all entries where an account is involved"""
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_balances_with_account = f"SELECT date,balance_btc,balance_{confighandler.get_fiat_currency().lower()} FROM cbalancehistory WHERE account = '{account}'"

        cursor.execute(get_balances_with_account)
        result = cursor.fetchall()
        balances_by_date = {}
        for entry in result:
            date = str(entry[0])
            balance = entry[1]
            if date in balances_by_date.keys():
                balances_by_date[date] += balance
            else:
                balances_by_date[date] = balance

        return balances_by_date


def getBalancesWithAccountTuple(account):
    """
    Returns all entries where an account is involved
    Formatted as dict[date] = (balance_btc,balance_fiat)
    """
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_balances_with_account = f"SELECT date,balance_btc,balance_{confighandler.get_fiat_currency().lower()} FROM cbalancehistory WHERE account = '{account}'"

        cursor.execute(get_balances_with_account)
        result = cursor.fetchall()
        balances_by_date = {}
        for entry in result:
            date = str(entry[0])
            balance_btc = entry[1]
            balance_fiat = entry[2]
            if date in balances_by_date.keys():
                new_balance_btc = balances_by_date[date][0] + balance_btc
                new_balance_fiat = balances_by_date[date][1] + balance_fiat
                balances_by_date[date] = (new_balance_btc, new_balance_fiat)
            else:
                balances_by_date[date] = (balance_btc, balance_fiat)

        return balances_by_date


def addTodaysBalances():
    """ Reads balances from balances table, and updates the balancehistory table accordingly"""
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        todays_balances = getBalancesFromLastDay()
        current_accounts = cbalances.getAllEntries()

        add_balance_history_query = """INSERT INTO 'cbalancehistory'
                                (account, date, token, balance, balance_btc, balance_eur,balance_usd,balance_jpy)
                                VALUES (?,?,?,?,?,?,?,?);"""
        today = int(float(datetime.today().timestamp()))

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
            balance_eur = prices.btcToFiat(balance_btc, currency='eur')
            balance_usd = prices.btcToFiat(balance_btc, currency='usd')
            balance_jpy = prices.btcToFiat(balance_btc, currency='jpy')

            cursor.execute(add_balance_history_query,
                           (account, today, token, balance, balance_btc, balance_eur, balance_usd, balance_jpy))


def getFirstTotalBalance():
    """
    Returns the sum of all balances from the earliest day
    """

    balancesbyday = getBalancesByDay()
    if len(balancesbyday.keys()) > 0:
        firstday = min(balancesbyday.keys())
        firstday_balance = balancesbyday[firstday]
        return(firstday_balance)
    return 0


def getFirstTotalBalance_fiat():
    """
    Returns the sum of all balances from the earliest day
    """
    balancesbyday = getBalancesByDay_fiat()
    if len(balancesbyday.keys()) > 0:
        firstday = min(balancesbyday.keys())
        firstday_balance = balancesbyday[firstday]
        return(firstday_balance)
    return 0


def getAllEntryDates():
    """
    Returns all the dates with an entry on the database
    """
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_all_entry_dates_query = "SELECT date FROM cbalancehistory"
        cursor.execute(get_all_entry_dates_query)

        return list(set([i[0] for i in cursor.fetchall()]))


def getMonthFirstTotalBalance(month, year=datetime.today().year):
    """
    Returns the total balance from the earliest entry of the month selected
    """
    # Get date of first entry of selected month
    all_dates = getAllEntryDates()

    selected_month_first_day_timestamp = datetime(year, month, 1).timestamp()
    selected_month_last_day_timestamp = utils.next_month_date(
        datetime(year, month, 1)).timestamp()

    all_dates_from_month = [d for d in all_dates if d >
                            selected_month_first_day_timestamp and d < selected_month_last_day_timestamp]

    if len(all_dates_from_month) == 0:
        # No entries on selected month, no balance assumed
        return 0

    # Now that we have all the entries from a certain month,
    # we want the earliest one
    first_entry_from_month_date = min(all_dates_from_month)

    return getBalancesByDay()[str(first_entry_from_month_date)]


def getMonthFirstTotalBalance_fiat(month, year=datetime.today().year):
    """
    Returns the total balance from the earliest entry of the month selected
    Expressed in fiat
    """
    # Get date of first entry of selected month
    all_dates = getAllEntryDates()

    selected_month_first_day_timestamp = datetime(year, month, 1).timestamp()
    selected_month_last_day_timestamp = utils.next_month_date(
        datetime(year, month, 1)).timestamp()

    all_dates_from_month = [d for d in all_dates if d >
                            selected_month_first_day_timestamp and d < selected_month_last_day_timestamp]

    if len(all_dates_from_month) == 0:
        # No entries on selected month, no balance assumed
        return 0

    # Now that we have all the entries from a certain month,
    # we want the earliest one
    first_entry_from_month_date = min(all_dates_from_month)

    result = getBalancesByDay_fiat()[str(first_entry_from_month_date)]
    return result


def getFirstEntryDate():
    """
    Returns timestamp of the day of the first entry ont he table
    """
    balancesbyday = getBalancesByDay()
    if len(balancesbyday.keys()) > 0:
        firstday = int(float(min(balancesbyday.keys())))
        return firstday
    return datetime.today().timestamp()


def getCurrentMonthFirstTotalBalance():
    """
    Returns the total balance from the earliest entry from the current month
    """
    current_month_first_day_timestamp = str(datetime(
        datetime.today().year, datetime.today().month, 1).timestamp())

    balancesbyday = getBalancesByDay()
    balancesbyday_days_from_current_month = [
        i for i in balancesbyday.keys() if i > current_month_first_day_timestamp]

    first_total_balance_day = min(balancesbyday_days_from_current_month)

    return balancesbyday[first_total_balance_day]


def getCurrentMonthFirstTotalBalance_fiat():
    """
    Returns the total balance from the earliest entry from the current month
    Expressed in fiat
    """
    current_month_first_day_timestamp = str(datetime(
        datetime.today().year, datetime.today().month, 1).timestamp())

    balancesbyday = getBalancesByDay_fiat()
    balancesbyday_days_from_current_month = [
        i for i in balancesbyday.keys() if i > current_month_first_day_timestamp]
    if len(balancesbyday_days_from_current_month) == 0:
        # No balances yet
        return 0

    first_total_balance_day = min(balancesbyday_days_from_current_month)
    first_total_balance = balancesbyday[first_total_balance_day]

    return first_total_balance


def getAccountBalance_minDate(cryptoacc, startdate):
    """
    Returns the first entry of an account's balance after the 
    selected startdate
    """
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        timestamps = getAllEntryDates()
        timestamps.sort()
        date = None
        for tm in timestamps:
            if tm >= startdate:
                date = tm
                break

        if date is None:
            return cbalances.getTotalAccountBalance_fiat(cryptoacc)

        get_account_balance_mindate_query = f"SELECT balance_{confighandler.get_fiat_currency()} FROM cbalancehistory WHERE date={date} and account='{cryptoacc}'"
        cursor.execute(get_account_balance_mindate_query)

        result = [i[0] for i in cursor.fetchall()]

        return sum(result)


def getAllEntries():
    """
    Returns all entries
    """
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_all_entries_query = f"SELECT * FROM cbalancehistory"
        cursor.execute(get_all_entries_query)

        return cursor.fetchall()


def getEntriesWithToken(token):
    """
    Returns all entries where token=token
    """
    token = token.lower()
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_entries_with_token_query = f"SELECT * FROM cbalancehistory WHERE token='{token}'"
        cursor.execute(get_entries_with_token_query)

        return cursor.fetchall()


def getEntriesWithAccount(account):
    """
    Returns all entries where account=account
    """
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_entries_with_account_query = f"SELECT * FROM cbalancehistory WHERE account='{account}'"
        cursor.execute(get_entries_with_account_query)

        return cursor.fetchall()


def deleteBalanceFromId(_id):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        delete_balance_query = """DELETE FROM cbalancehistory WHERE id= %d""" % _id

        cursor.execute(delete_balance_query)
