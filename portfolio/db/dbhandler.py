#!/usr/bin/python3

from datetime import datetime
import calendar

from portfolio.db.fdbhandler import balances, historicalbalances, results
from portfolio.db.cdbhandler import cbalances, chistoricalbalances


def get_totalWealthByDay():
    """
    Groups the historicalbalances from portfolio and cportfolio,
    and returns a dictionary where:
     - keys are dates (timestamps)
     - values are total wealth on that day
    """

    balancesbyday = historicalbalances.getBalancesByDay()
    cbalancesbyday = chistoricalbalances.getBalancesByDay_fiat()

    wealthbyday = {}

    # Now that we have the days that have balances and crypto balances,
    # we iterate through them and calculate the sum for each day
    for day in balancesbyday:
        balance = balancesbyday[day]

        if day in wealthbyday.keys():
            wealthbyday[day] += balance
        else:
            wealthbyday[day] = balance

    for day in cbalancesbyday:
        balance = cbalancesbyday[day]

        if day in wealthbyday.keys():
            wealthbyday[day] += balance
        else:
            wealthbyday[day] = balance

    # Format to iterate better
    wealthbyday_formatted = []
    for day in wealthbyday:
        balance = wealthbyday[day]
        wealthbyday_formatted.append((day, balance))

    # Sort by timestamp
    wealthbyday_formatted.sort(key=lambda x: x[0])

    # Remake dictionary
    wealthbyday = {}
    for data in wealthbyday_formatted:
        day = data[0]
        balance = data[1]

        if day in wealthbyday.keys():
            wealthbyday[day] += balance
        else:
            wealthbyday[day] = balance

    return wealthbyday


def getWealthByDay(fiataccs=None, cryptoaccs=None, startdate=0, enddate=9999999999999999):
    """
    Groups the historicalbalances from portfolio and cportfolio,
    only considering the accounts from fiataccs & cryptoaccs parameters,
    between de period (startdate - enddate)
    and returns a dictionary where:
     - keys are dates (timestamps)
     - values are total wealth on that day
    """
    balancesbyday = historicalbalances.getBalancesByDay(fiataccs=fiataccs)
    cbalancesbyday = chistoricalbalances.getBalancesByDay_fiat(
        cryptoaccs=cryptoaccs)
    wealthbyday = {}

    # Now that we have the days that have balances and crypto balances,
    # we iterate through them and calculate the sum for each day
    for day in balancesbyday:
        balance = balancesbyday[day]

        if day in wealthbyday.keys():
            wealthbyday[day] += balance
        else:
            wealthbyday[day] = balance

    for day in cbalancesbyday:
        balance = cbalancesbyday[day]

        if day in wealthbyday.keys():
            wealthbyday[day] += balance
        else:
            wealthbyday[day] = balance

    # Format to iterate better
    wealthbyday_formatted = []
    for day in wealthbyday:
        balance = wealthbyday[day]
        wealthbyday_formatted.append((day, balance))

    # Sort by timestamp
    wealthbyday_formatted.sort(key=lambda x: x[0])

    # Remake dictionary
    wealthbyday = {}
    for data in wealthbyday_formatted:
        day = data[0]
        if int(day) < startdate or int(day) > enddate:
            continue
        balance = data[1]

        if day in wealthbyday.keys():
            wealthbyday[day] += balance
        else:
            wealthbyday[day] = balance

    return wealthbyday


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

    If there is not any historical data, returns 0
    """
    first_balance_day = historicalbalances.getFirstEntryDate()
    first_cbalance_day = chistoricalbalances.getFirstEntryDate()

    if first_cbalance_day == first_balance_day == 0:
        return 0
    elif first_cbalance_day == 0:
        return historicalbalances.getFirstTotalBalance()
    elif first_balance_day == 0:
        return chistoricalbalances.getFirstTotalBalance_fiat()

    # Remove hour, minute and second
    first_balance_day = datetime.fromtimestamp(first_balance_day)
    first_cbalance_day = datetime.fromtimestamp(first_cbalance_day)

    first_balance_day = datetime(
        first_balance_day.year, first_balance_day.month, first_balance_day.day)
    first_cbalance_day = datetime(
        first_cbalance_day.year, first_cbalance_day.month, first_cbalance_day.day)
    print(first_balance_day)
    print(first_cbalance_day)
    print(datetime.fromtimestamp(0))

    # Check if cbalancehistory or chistoricalbalances is empty
    if first_balance_day == first_cbalance_day:
        # First entry has both crypto and fiat data
        first_balance = historicalbalances.getFirstTotalBalance(
        ) + chistoricalbalances.getFirstTotalBalance_fiat()
    elif first_balance_day > first_cbalance_day:
        # First entry has crypto data only
        first_balance = chistoricalbalances.getFirstTotalBalance_fiat()
    else:
        # First entry has fiat data only
        first_balance = historicalbalances.getFirstTotalBalance()

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
    return historicalbalances.getCurrentMonthFirstTotalBalance() + chistoricalbalances.getCurrentMonthFirstTotalBalance_fiat()


def get_total_wealth_on_month(month, year=datetime.today().year):
    """
    Returns the total wealth (portfolio+cportfolio)
    of the first entry from the month selected

    month: int
    """

    return historicalbalances.getMonthFirstTotalBalance(month, year=year) + chistoricalbalances.getMonthFirstTotalBalance_fiat(month, year=year)


def get_change_last_month():
    """
    Returns the difference between the current total wealth
    and the total wealth from the first entry on the current month
    """
    first_day_month_total_wealth = get_first_total_wealth_current_month()
    if first_day_month_total_wealth > 0:
        current_total_wealth = balances.getTotalBalanceAllAccounts(
        ) + cbalances.getTotalBalanceAllAccounts_fiat()

        change_fiat_value = int(current_total_wealth -
                                first_day_month_total_wealth)
    else:
        change_fiat_value = 0

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


def getTotalResult(fiataccs, cryptoaccs, startdate, enddate):
    """
    Sums all results from both databases from the 
    selected accounts and on the selected period

    Parameters:
        - fiataccs: list of selected fiat accounts
        - cryptoaccs: list of selected crypto accounts
        - startdate: timestamp
        - enddate: timestamp
    """
    fiattotalresult = 0
    for fiatacc in fiataccs:
        result = results.getResults_fromQuery(start_date=datetime.fromtimestamp(
            startdate), end_date=datetime.fromtimestamp(enddate), account=fiatacc)
        fiattotalresult += result

    cryptototalresult = 0
    for cryptoacc in cryptoaccs:
        start_balance = chistoricalbalances.getAccountBalance_minDate(
            cryptoacc, startdate)
        end_balance = chistoricalbalances.getAccountBalance_minDate(
            cryptoacc, enddate)
        cryptototalresult += (end_balance-start_balance)

    result = fiattotalresult + cryptototalresult
    return round(result, 2)
