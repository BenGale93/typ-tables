"""Datetime formatting helper functions."""

from datetime import date

from typ_tables import ttypes


def get_date_format(date_style: ttypes.DateStyle) -> str:
    """Get the date format string based on the date style."""
    date_formats = {
        "iso": "%Y-%m-%d",
        "wday_month_day_year": "%A, %B %d, %Y",
        "wd_m_day_year": "%a, %b %d, %Y",
        "wday_day_month_year": "%A %d %B %Y",
        "month_day_year": "%B %d, %Y",
        "m_day_year": "%b %d, %Y",
        "day_m_year": "%d %b %Y",
        "day_month_year": "%d %B %Y",
        "day_month": "%d %B",
        "day_m": "%d %b",
        "year": "%Y",
        "month": "%B",
        "day": "%d",
        "year.mn.day": "%Y/%m/%d",
        "y.mn.day": "%y/%m/%d",
        "year_week": "%Y-W%W",
    }

    if date_style not in date_formats:
        msg = f"date_style must be one of: {', '.join(date_formats.keys())}"
        raise ValueError(msg)

    return date_formats[date_style]


def format_date(value: date, date_style: ttypes.DateStyle) -> str:
    """Format the date portion of a value using the given date style.

    `strftime` has no portable quarter directive (`%q` is not a Python format
    code), so the `year_quarter` style is computed explicitly rather than via
    `get_date_format`.
    """
    if date_style == "year_quarter":
        quarter = (value.month - 1) // 3 + 1
        return f"{value.year}-Q{quarter}"

    return value.strftime(get_date_format(date_style))


def get_time_format(time_style: ttypes.TimeStyle) -> str:
    """Get the time format string based on the time style."""
    time_formats = {
        "iso": "%H:%M:%S",
        "iso-short": "%H:%M",
        "h_m_s_p": "%I:%M:%S %p",
        "h_m_p": "%I:%M %p",
        "h_p": "%I %p",
    }

    if time_style not in time_formats:
        msg = f"time_style must be one of: {', '.join(time_formats.keys())}"
        raise ValueError(msg)

    return time_formats[time_style]
