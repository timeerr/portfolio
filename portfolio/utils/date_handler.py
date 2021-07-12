import calendar


def next_month_date(d):
    """ Returns the next month number given a datetime """
    _year = d.year+(d.month//12)
    _month = 1 if (d.month//12) else d.month + 1
    next_month_len = calendar.monthrange(_year, _month)[1]
    next_month = d
    if d.day > next_month_len:
        next_month = next_month.replace(day=next_month_len)
    next_month = next_month.replace(year=_year, month=_month)
    return next_month


def prev_month_date(d):
    """ Returns the previous month number given a datetime """
    _year = d.year-1 if d.month == 1 else d.year
    _month = 12 if (d.month == 1) else d.month - 1
    next_month_len = calendar.monthrange(_year, _month)[1]
    next_month = d
    if d.day > next_month_len:
        next_month = next_month.replace(day=next_month_len)
    next_month = next_month.replace(year=_year, month=_month)
    return next_month
