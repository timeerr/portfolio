#!/usr/bin/python3

from datetime import datetime
import calendar

from gui.dbhandler import balances, historicalbalances
from gui.cdbhandler import cbalances, chistoricalbalances


def get_totalWealthByDay():
    """
    Groups the historicalbalances from portfolio and cportfolio,
    and returns a dictionary where:
     - keys are days
     - values are total wealth on that day
    """

    balancesbyday = historicalbalances.getBalancesByDay()
    cbalancesbyday = chistoricalbalances.getBalancesByDay_fiat()

    balancesbyday_days = set([datetime.fromtimestamp(
        int(float(i))) for i in balancesbyday.keys()])
    cbalancesbyday_days = set([datetime.fromtimestamp(
        int(float(i))) for i in cbalancesbyday.keys()])

    wealthbyday_days = list(balancesbyday_days & cbalancesbyday_days)
    wealthbyday = {}

    # Now that we have the days that have balances and crypto balances,
    # we iterate through them and calculate the sum for each day
    for day in balancesbyday:
        day_datetime = datetime.fromtimestamp(int(float(day)))
        balance = balancesbyday[day]

        if day_datetime in wealthbyday_days:
            if day_datetime in wealthbyday.keys():
                wealthbyday[day_datetime] += balance
            else:
                wealthbyday[day_datetime] = balance

    for day in cbalancesbyday:
        day_datetime = datetime.fromtimestamp(int(float(day)))
        balance = cbalancesbyday[day]

        if day_datetime in wealthbyday_days:
            if day_datetime in wealthbyday.keys():
                wealthbyday[day_datetime] += balance
            else:
                wealthbyday[day_datetime] = balance

    # Changing the keys to timestamp format
    wealthbyday_timestamps = {}
    for day_datetime in wealthbyday:
        wealthbyday_timestamps[day_datetime.timestamp()
                               ] = wealthbyday[day_datetime]

    return wealthbyday_timestamps


def get_totalWealthByDay_LastMonth():
    """
    Groups the historicalbalances from las month from portfolio and cportfolio,
    and returns a dictionary where:
     - keys are days
     - values are total wealth on that day
    """
    totalwealthbyday_lastmonth = {}
    totalwealthbyday = get_totalWealthByDay()
    first_day_current_month_timestamp = datetime(
        datetime.today().year, datetime.today().month, 1).timestamp()

    for day in totalwealthbyday:
        if int(float(day)) > first_day_current_month_timestamp:
            totalwealthbyday_lastmonth[day] = totalwealthbyday[day]

    return totalwealthbyday_lastmonth


def get_firstBalance():
    """
    Returns the total wealth from the first day of this full portfolio
    - Check if first historicalbalance and chistoricalbalance have the same day
    - If not, then consider the earliest only
    - If yes, sum them
    """
    first_balance_day = datetime.fromtimestamp(
        historicalbalances.getFirstEntryDate())
    first_cbalance_day = datetime.fromtimestamp(
        chistoricalbalances.getFirstEntryDate())

    # Remove hour, minute and second
    first_balance_day = datetime(
        first_balance_day.year, first_balance_day.month, first_balance_day.day)
    first_cbalance_day = datetime(
        first_cbalance_day.year, first_cbalance_day.month, first_cbalance_day.day)

    if first_balance_day == first_cbalance_day:
        first_balance = historicalbalances.getFirstTotalBalance(
        ) + chistoricalbalances.getFirstTotalBalance_fiat()
    elif first_balance_day < first_cbalance_day:
        first_balance = historicalbalances.getFirstTotalBalance()
    else:
        first_balance = chistoricalbalances.getFirstTotalBalance_fiat()

    return first_balance


def get_lastBalance():
    """
    Returns the sum of the current total balance on portfolio and cportfolio
    """
    return balances.getTotalBalanceAllAccounts() + cbalances.getTotalBalanceAllAccounts_fiat()


def get_first_total_wealth_current_month():
    """
    Returns the total wealth from the first entry of
    the current month
    """
    return historicalbalances.getCurrentMonthFirstTotalBalance() + \
        chistoricalbalances.getCurrentMonthFirstTotalBalance_fiat()


def get_total_wealth_on_month(month, year=datetime.today().year):
    """
    Returns the total wealth (portfolio+cportfolio)
    of the first entry from the month selected

    month: int
    """

    return historicalbalances.getMonthFirstTotalBalance(month, year=year) +  \
        chistoricalbalances.getMonthFirstTotalBalance_fiat(month, year=year)


def get_change_last_month():
    """
    Returns the difference between the current total wealth
    and the total wealth from the first entry on the current month
    """
    first_day_month_total_wealth = get_first_total_wealth_current_month()
    current_total_wealth = balances.getTotalBalanceAllAccounts(
    ) + cbalances.getTotalBalanceAllAccounts_fiat()

    change_fiat_value = int(current_total_wealth -
                            first_day_month_total_wealth)

    return change_fiat_value


def next_month_date(d):
    _year = d.year+(d.month//12)
    _month = 1 if (d.month//12) else d.month + 1
    next_month_len = calendar.monthrange(_year, _month)[1]
    next_month = d
    if d.day > next_month_len:
        next_month = next_month.replace(day=next_month_len)
    next_month = next_month.replace(year=_year, month=_month)
    return next_month


def prev_month_date(d):
    _year = d.year-1 if d.month == 1 else d.year
    _month = 12 if (d.month == 1) else d.month - 1
    next_month_len = calendar.monthrange(_year, _month)[1]
    next_month = d
    if d.day > next_month_len:
        next_month = next_month.replace(day=next_month_len)
    next_month = next_month.replace(year=_year, month=_month)
    return next_month