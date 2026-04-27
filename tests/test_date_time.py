from datetime import date, datetime, time

import polars as pl
import pytest
from inline_snapshot import external

from typ_tables import TypTable


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({}, external("uuid:default-date.typ")),
        ({"rows": [0], "date_style": "month_day_year"}, external("uuid:just-top-row-date.typ")),
        ({"date_style": "month_day_year"}, external("uuid:month-day-year.typ")),
        ({"date_style": "wd_m_day_year"}, external("uuid:wd-m-day-year.typ")),
        ({"date_style": "day_month_year"}, external("uuid:day-month-year.typ")),
        ({"date_style": "year"}, external("uuid:year-only.typ")),
        ({"date_style": "month"}, external("uuid:month-only.typ")),
        ({"date_style": "day"}, external("uuid:day-only.typ")),
        ({"date_style": "year.mn.day"}, external("uuid:year-mn-day.typ")),
        ({"date_style": "y.mn.day"}, external("uuid:y-mn-day.typ")),
        ({"date_style": "year_week"}, external("uuid:year-week.typ")),
        ({"date_style": "year_quarter"}, external("uuid:year-quarter.typ")),
        ({"pattern": "Date: {x}"}, external("uuid:date-pattern.typ")),
    ],
)
def test_date(table_check, args, result):
    df = pl.DataFrame(
        {
            "date": [
                date(2000, 2, 29),
                date(2023, 12, 25),
                date(1999, 7, 4),
                date(2024, 1, 1),
                None,
            ],
        }
    )

    table = TypTable(df).fmt_date(**args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_date_from_string(table_check):
    df = pl.DataFrame(
        {
            "date": [
                "2000-02-29",
                "2023-12-25",
                "1999-07-04",
                "2024-01-01",
                None,
            ],
        }
    )

    table = TypTable(df).fmt_date()
    typst_table = table.to_typst()

    assert typst_table == external("uuid:date-from-string.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_date_invalid_object():
    df = pl.DataFrame({"date": [10]})

    table = TypTable(df).fmt_date()

    with pytest.raises(ValueError, match="Invalid date object"):
        table.to_typst()


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({}, external("uuid:default-time.typ")),
        ({"rows": [0], "time_style": "iso-short"}, external("uuid:just-top-row-time.typ")),
        ({"time_style": "iso-short"}, external("uuid:iso-short-time.typ")),
        ({"time_style": "h_m_s_p"}, external("uuid:h-m-s-p-time.typ")),
        ({"time_style": "h_m_p"}, external("uuid:h-m-p-time.typ")),
        ({"time_style": "h_p"}, external("uuid:h-p-time.typ")),
        ({"pattern": "Time: {x}"}, external("uuid:time-pattern.typ")),
    ],
)
def test_time(table_check, args, result):
    df = pl.DataFrame(
        {
            "time": [
                time(14, 35, 0),
                time(9, 0, 0),
                time(23, 59, 59),
                time(0, 0, 0),
                None,
            ],
        }
    )

    table = TypTable(df).fmt_time(**args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_time_from_string(table_check):
    df = pl.DataFrame(
        {
            "time": [
                "14:35:00",
                "09:00:00",
                "23:59:59",
                "00:00:00",
                None,
            ],
        }
    )

    table = TypTable(df).fmt_time()
    typst_table = table.to_typst()

    assert typst_table == external("uuid:time-from-string.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_time_invalid_object():
    df = pl.DataFrame({"time": [10]})

    table = TypTable(df).fmt_time()

    with pytest.raises(ValueError, match="Invalid time object"):
        table.to_typst()


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({}, external("uuid:default-datetime.typ")),
        (
            {"rows": [0], "date_style": "month_day_year", "time_style": "h_m_s_p"},
            external("uuid:just-top-row-datetime.typ"),
        ),
        ({"date_style": "month_day_year", "time_style": "h_m_s_p"}, external("uuid:mdy-hmsp.typ")),
        ({"date_style": "wd_m_day_year", "time_style": "h_m_p"}, external("uuid:wdmdy-hmp.typ")),
        ({"date_style": "day_month_year", "time_style": "h_p"}, external("uuid:dmy-hp.typ")),
        ({"date_style": "year", "time_style": "iso"}, external("uuid:year-iso.typ")),
        ({"sep": " - "}, external("uuid:sep-dash.typ")),
        ({"sep": "T"}, external("uuid:sep-t.typ")),
        ({"pattern": "Datetime: {x}"}, external("uuid:datetime-pattern.typ")),
    ],
)
def test_datetime(table_check, args, result):
    df = pl.DataFrame(
        {
            "datetime": [
                datetime(2000, 2, 29, 14, 35, 0),
                datetime(2023, 12, 25, 9, 0, 0),
                datetime(1999, 7, 4, 23, 59, 59),
                datetime(2024, 1, 1, 0, 0, 0),
                None,
            ],
        }
    )

    table = TypTable(df).fmt_datetime(**args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_datetime_from_string(table_check):
    df = pl.DataFrame(
        {
            "datetime": [
                "2000-02-29 14:35:00",
                "2023-12-25 09:00:00",
                "1999-07-04 23:59:59",
                "2024-01-01 00:00:00",
                None,
            ],
        }
    )

    table = TypTable(df).fmt_datetime()
    typst_table = table.to_typst()

    assert typst_table == external("uuid:datetime-from-string.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_datetime_with_format_str(table_check):
    df = pl.DataFrame(
        {
            "datetime": [
                datetime(2000, 2, 29, 14, 35, 0),
                datetime(2023, 12, 25, 9, 0, 0),
                datetime(1999, 7, 4, 23, 59, 59),
                datetime(2024, 1, 1, 0, 0, 0),
                None,
            ],
        }
    )

    table = TypTable(df).fmt_datetime(format_str="%Y/%m/%d %H:%M")
    typst_table = table.to_typst()

    assert typst_table == external("uuid:datetime-format-str.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_datetime_invalid_object():
    df = pl.DataFrame({"datetime": [10]})

    table = TypTable(df).fmt_datetime()

    with pytest.raises(ValueError, match="Invalid datetime object"):
        table.to_typst()


def test_date_invalid_style():
    df = pl.DataFrame({"date": [date(2000, 1, 1)]})

    table = TypTable(df).fmt_date(date_style="invalid_style")  # type: ignore [bad-argument-type]

    with pytest.raises(ValueError, match="date_style must be one of"):
        table.to_typst()


def test_time_invalid_style():
    df = pl.DataFrame({"time": [time(12, 0, 0)]})

    table = TypTable(df).fmt_time(time_style="invalid_style")  # type: ignore [bad-argument-type]

    with pytest.raises(ValueError, match="time_style must be one of"):
        table.to_typst()
