from datetime import datetime


def utcnow_day():
    now = datetime.utcnow()
    return datetime(year=now.year, month=now.month, day=now.day)
