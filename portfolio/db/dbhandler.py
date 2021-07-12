#!/usr/bin/python3

import os
from datetime import datetime

from portfolio.utils.date_handler import next_month_date
from portfolio.db.fdbhandler import balances, historicalbalances, results
from portfolio.db.cdbhandler import cbalances, chistoricalbalances


def get_wealth_by_day(fiataccs=None, cryptoaccs=None,
                      startdate=0, enddate=9999999999999999):
    """
    Groups the historicalbalances from portfolio and cportfolio,
    only considering the accounts from fiataccs & cryptoaccs parameters,
    between de period (startdate - enddate)
    and returns a dictionary where:
     - keys are dates (timestamps)
     - values are total wealth on that day
    """
    balancesbyday = historicalbalances.get_balances_by_day(fiataccs=fiataccs)
    cbalancesbyday = chistoricalbalances.get_balances_by_day_fiat(
        cryptoaccs=cryptoaccs)

    # Now that we have the days that have balances and crypto balances,
    # we iterate through them and calculate the sum for each day
    wealthbyday = {}
    for day in balancesbyday:
        balance = balancesbyday[day]
        if day not in wealthbyday.keys():
            wealthbyday[day] = 0
        wealthbyday[day] += balance
    for day in cbalancesbyday:
        balance = cbalancesbyday[day]
        if day not in wealthbyday.keys():
            wealthbyday[day] = 0
        wealthbyday[day] += balance

    # Use tuple to sort
    wealthbyday_formatted = []
    for day in wealthbyday:
        balance = wealthbyday[day]
        wealthbyday_formatted.append((day, balance))
    wealthbyday_formatted.sort(key=lambda x: x[0])

    # Remake dictionary
    final = {}
    for data in wealthbyday_formatted:
        day, balance = data
        if int(day) < startdate or int(day) > enddate:
            continue
        if day not in final.keys():
            final[day] = 0
        final[day] += balance
    return final


def get_total_wealth_by_day_current_month():
    """
    Groups the historicalbalances from current month from portfolio and cportfolio,
    and returns a dictionary where:
     - keys are days
     - values are total wealth on that day
    """
    totalwealthbyday = get_wealth_by_day()
    today = datetime.today()
    month_first_day = datetime(
        today.year, today.month, 1)
    next_month = next_month_date(month_first_day)

    month_first_day = month_first_day.timestamp()
    next_month_first_day = datetime(
        next_month.year, next_month.month, 1).timestamp()

    final = {}
    for day in totalwealthbyday:
        if int(float(day)) > month_first_day and int(float(day)) < next_month_first_day:
            final[day] = totalwealthbyday[day]
    return final


def get_first_balance():
    """
    Returns the total wealth from the first day of this full portfolio
    - Check if first historicalbalance and chistoricalbalance have the same day
    - If not, then consider the earliest only
    - If yes, sum them

    If there is not any historical data, returns 0
    """
    first_f = historicalbalances.get_first_entry_date()
    first_c = chistoricalbalances.get_first_entry_date()

    if first_c == first_f == 0:
        return 0
    elif first_c == 0:
        return historicalbalances.get_first_total_balance()
    elif first_f == 0:
        return chistoricalbalances.get_first_total_balance_fiat()

    # Remove hour, minute and second
    first_f = datetime.fromtimestamp(first_f)
    first_c = datetime.fromtimestamp(first_c)

    first_f = datetime(
        first_f.year, first_f.month, first_f.day)
    first_c = datetime(
        first_c.year, first_c.month, first_c.day)

    # Check if cbalancehistory or chistoricalbalances is empty
    if first_f == first_c:
        # First entry has both crypto and fiat data
        first_balance = historicalbalances.get_first_total_balance(
        ) + chistoricalbalances.get_first_total_balance_fiat()
    elif first_f > first_c:
        # First entry has crypto data only
        first_balance = chistoricalbalances.get_first_total_balance_fiat()
    else:
        # First entry has fiat data only
        first_balance = historicalbalances.get_first_total_balance()
    return first_balance


def get_last_balance():
    """Returns the sum of the current total balance on portfolio and cportfolio"""
    return balances.get_total_balance_all_accounts() + cbalances.get_total_balance_all_accounts_fiat()


def get_first_total_wealth_current_month():
    """
    Returns the total wealth from the first entry of
    the current month
    """
    return historicalbalances.get_current_month_first_total_balance() + chistoricalbalances.get_current_month_first_total_balance_fiat()


def get_total_wealth_on_month(month, year=datetime.today().year):
    """
    Returns the total wealth (portfolio+cportfolio)
    of the first entry from the month selected

    month: int
    """
    return historicalbalances.get_month_first_total_balance(month, year=year) + chistoricalbalances.get_month_first_total_balance_fiat(month, year=year)


def get_change_last_month():
    """
    Returns the difference between the current total wealth
    and the total wealth from the first entry on the current month
    """
    current_total_wealth = balances.get_total_balance_all_accounts(
    ) + cbalances.get_total_balance_all_accounts_fiat()
    first_day_month_total_wealth = get_first_total_wealth_current_month()
    return int(current_total_wealth - first_day_month_total_wealth)


def get_total_result(fiataccs, cryptoaccs, startdate, enddate):
    """
    Sums all results from both databases from the
    selected accounts and on the selected period

    Parameters:
        - fiataccs: list of selected fiat accounts
        - cryptoaccs: list of selected crypto accounts
        - startdate: timestamp
        - enddate: timestamp
    """
    raise NotImplementedError  # TODO
#    fiattotalresult = 0
#    for fiatacc in fiataccs:
#        result = results.get_results_from_query(
#            start_date=datetime.fromtimestamp(startdate),
#            end_date=datetime.fromtimestamp(enddate),
#            account=fiatacc)
#        fiattotalresult += result
#
#    cryptototalresult = 0
#    for cryptoacc in cryptoaccs:
#        start_balance = chistoricalbalances.getAccountBalance_minDate(
#            cryptoacc, startdate)
#        end_balance = chistoricalbalances.getAccountBalance_minDate(
#            cryptoacc, enddate)
#        cryptototalresult += (end_balance-start_balance)
#
#    result = fiattotalresult + cryptototalresult
#    return round(result, 2)
