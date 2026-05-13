from datetime import date

import pytest

from nldate import parse

# Fixed reference date: Thursday, March 14, 2024
TODAY = date(2024, 3, 14)


def test_today() -> None:
    assert parse("today", today=TODAY) == TODAY


def test_tomorrow() -> None:
    assert parse("tomorrow", today=TODAY) == date(2024, 3, 15)


def test_yesterday() -> None:
    assert parse("yesterday", today=TODAY) == date(2024, 3, 13)


def test_day_after_tomorrow() -> None:
    assert parse("the day after tomorrow", today=TODAY) == date(2024, 3, 16)


def test_day_before_yesterday() -> None:
    assert parse("the day before yesterday", today=TODAY) == date(2024, 3, 12)


def test_next_tuesday() -> None:
    # Today is Thursday Mar 14 → next Tuesday is Mar 19
    assert parse("next Tuesday", today=TODAY) == date(2024, 3, 19)


def test_last_monday() -> None:
    # Today is Thursday Mar 14 → last Monday is Mar 11
    assert parse("last Monday", today=TODAY) == date(2024, 3, 11)


def test_next_weekday_wraps() -> None:
    # "next Thursday" from Thursday should skip to the following Thursday
    assert parse("next Thursday", today=TODAY) == date(2024, 3, 21)


def test_last_weekday_wraps() -> None:
    # "last Thursday" from Thursday should go back one week
    assert parse("last Thursday", today=TODAY) == date(2024, 3, 7)


def test_in_n_days() -> None:
    assert parse("in 5 days", today=TODAY) == date(2024, 3, 19)


def test_in_n_weeks() -> None:
    assert parse("in 2 weeks", today=TODAY) == date(2024, 3, 28)


def test_n_days_ago() -> None:
    assert parse("3 days ago", today=TODAY) == date(2024, 3, 11)


def test_n_months_ago() -> None:
    assert parse("2 months ago", today=TODAY) == date(2024, 1, 14)


def test_n_days_from_now() -> None:
    assert parse("7 days from now", today=TODAY) == date(2024, 3, 21)


def test_n_weeks_from_now() -> None:
    assert parse("1 week from now", today=TODAY) == date(2024, 3, 21)


def test_n_days_before_absolute() -> None:
    assert parse("5 days before December 1st, 2025", today=TODAY) == date(2025, 11, 26)


def test_n_days_after_absolute() -> None:
    assert parse("10 days after January 1, 2025", today=TODAY) == date(2025, 1, 11)


def test_complex_offset_after_relative() -> None:
    # 1 year and 2 months after Mar 13, 2024 = May 13, 2025
    result = parse("1 year and 2 months after yesterday", today=TODAY)
    assert result == date(2025, 5, 13)


def test_two_weeks_from_tomorrow() -> None:
    # tomorrow = Mar 15, + 2 weeks = Mar 29
    assert parse("two weeks from tomorrow", today=TODAY) == date(2024, 3, 29)


def test_word_number_offset() -> None:
    assert parse("three days ago", today=TODAY) == date(2024, 3, 11)


def test_next_month() -> None:
    assert parse("next month", today=TODAY) == date(2024, 4, 14)


def test_next_year() -> None:
    assert parse("next year", today=TODAY) == date(2025, 3, 14)


def test_last_month() -> None:
    assert parse("last month", today=TODAY) == date(2024, 2, 14)


def test_last_year() -> None:
    assert parse("last year", today=TODAY) == date(2023, 3, 14)


def test_absolute_full_date() -> None:
    assert parse("December 1st, 2025") == date(2025, 12, 1)


def test_absolute_iso() -> None:
    assert parse("2025-06-15") == date(2025, 6, 15)


def test_absolute_short() -> None:
    assert parse("Jan 5, 2024") == date(2024, 1, 5)


def test_today_defaults_to_real_today() -> None:
    result = parse("today")
    assert result == date.today()


def test_next_week() -> None:
    assert parse("next week", today=TODAY) == date(2024, 3, 21)


def test_last_week() -> None:
    assert parse("last week", today=TODAY) == date(2024, 3, 7)


def test_invalid_raises() -> None:
    with pytest.raises(ValueError):
        parse("not a date at all xyz")


def test_a_week_from_today() -> None:
    assert parse("a week from today", today=TODAY) == date(2024, 3, 21)


def test_one_month_before_date() -> None:
    assert parse("one month before March 14, 2025", today=TODAY) == date(2025, 2, 14)
