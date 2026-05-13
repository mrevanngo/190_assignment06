from __future__ import annotations

import re
from datetime import date, timedelta

from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta

WEEKDAYS: dict[str, int] = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
    "mon": 0,
    "tue": 1,
    "tues": 1,
    "wed": 2,
    "thurs": 3,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}

WORD_NUMS: dict[str, int] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "a": 1,
    "an": 1,
}

UNITS: dict[str, str] = {
    "day": "days",
    "days": "days",
    "week": "weeks",
    "weeks": "weeks",
    "month": "months",
    "months": "months",
    "year": "years",
    "years": "years",
}


def _to_int(s: str) -> int:
    s = s.strip().lower()
    if s.isdigit():
        return int(s)
    return WORD_NUMS.get(s, 1)


def _make_delta(unit: str, n: int) -> relativedelta:
    if unit == "days":
        return relativedelta(days=n)
    elif unit == "weeks":
        return relativedelta(weeks=n)
    elif unit == "months":
        return relativedelta(months=n)
    else:
        return relativedelta(years=n)


def _parse_offset(s: str) -> relativedelta:
    years = months = weeks = days = 0
    for m in re.finditer(r"(\w+)\s+(days?|weeks?|months?|years?)", s, re.IGNORECASE):
        n = _to_int(m.group(1))
        unit = UNITS[m.group(2).lower()]
        if unit == "days":
            days += n
        elif unit == "weeks":
            weeks += n
        elif unit == "months":
            months += n
        else:
            years += n
    return relativedelta(years=years, months=months, weeks=weeks, days=days)


def _next_weekday(d: date, wd: int) -> date:
    days = (wd - d.weekday()) % 7
    if days == 0:
        days = 7
    return d + timedelta(days=days)


def _last_weekday(d: date, wd: int) -> date:
    days = (d.weekday() - wd) % 7
    if days == 0:
        days = 7
    return d - timedelta(days=days)


def _try_absolute(s: str) -> date | None:
    try:
        return dateutil_parser.parse(s, dayfirst=False).date()
    except Exception:
        return None


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    text = s.strip()
    low = text.lower()

    # Strip leading "the " except for "the day after/before"
    if low.startswith("the ") and not re.match(r"^the day (after|before)", low):
        low = low[4:]
        text = text[4:]

    # Simple keywords
    if low == "today":
        return today
    if low == "tomorrow":
        return today + timedelta(days=1)
    if low == "yesterday":
        return today - timedelta(days=1)
    if low in ("day after tomorrow", "the day after tomorrow"):
        return today + timedelta(days=2)
    if low in ("day before yesterday", "the day before yesterday"):
        return today - timedelta(days=2)

    # "next/coming <weekday>"
    for prefix in ("next ", "coming "):
        if low.startswith(prefix):
            rest = low[len(prefix):]
            if rest in WEEKDAYS:
                return _next_weekday(today, WEEKDAYS[rest])

    # "last/previous/past <weekday>"
    for prefix in ("last ", "previous ", "past "):
        if low.startswith(prefix):
            rest = low[len(prefix):]
            if rest in WEEKDAYS:
                return _last_weekday(today, WEEKDAYS[rest])

    # "this <weekday>" — nearest occurrence including today
    if low.startswith("this "):
        rest = low[5:]
        if rest in WEEKDAYS:
            wd = WEEKDAYS[rest]
            days = (wd - today.weekday()) % 7
            return today + timedelta(days=days)

    # "next/last week/month/year"
    period_map: dict[str, relativedelta] = {
        "next week": relativedelta(weeks=1),
        "last week": relativedelta(weeks=-1),
        "next month": relativedelta(months=1),
        "last month": relativedelta(months=-1),
        "next year": relativedelta(years=1),
        "last year": relativedelta(years=-1),
    }
    if low in period_map:
        return today + period_map[low]

    # "in <n> <unit>"
    m = re.match(r"^in\s+(\w+)\s+(days?|weeks?|months?|years?)$", low)
    if m:
        n = _to_int(m.group(1))
        unit = UNITS[m.group(2)]
        return today + _make_delta(unit, n)

    # "<n> <unit> from now/today"
    m = re.match(
        r"^(\w+)\s+(days?|weeks?|months?|years?)\s+from\s+(now|today)$", low
    )
    if m:
        n = _to_int(m.group(1))
        unit = UNITS[m.group(2)]
        return today + _make_delta(unit, n)

    # "<n> <unit> ago"
    m = re.match(r"^(\w+)\s+(days?|weeks?|months?|years?)\s+ago$", low)
    if m:
        n = _to_int(m.group(1))
        unit = UNITS[m.group(2)]
        return today - _make_delta(unit, n)

    # "<offset> before/after <date>"
    mb = re.match(r"^(.+?)\s+(before|after)\s+(.+)$", low)
    if mb:
        offset_str = mb.group(1)
        direction = mb.group(2)
        date_str = mb.group(3)
        ref = parse(date_str, today)
        delta = _parse_offset(offset_str)
        return ref - delta if direction == "before" else ref + delta

    # "<offset> from <date>"
    mf = re.match(r"^(.+?)\s+from\s+(.+)$", low)
    if mf:
        offset_str = mf.group(1)
        date_str = mf.group(2)
        ref = parse(date_str, today)
        delta = _parse_offset(offset_str)
        return ref + delta

    # Absolute date (fallback to dateutil)
    result = _try_absolute(text)
    if result is not None:
        return result

    raise ValueError(f"Cannot parse date: {s!r}")
