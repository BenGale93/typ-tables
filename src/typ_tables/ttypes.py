"""Typ-Table Types."""

import typing as t

from narwhals import DataFrame
from narwhals.typing import IntoDataFrameT

Data = DataFrame[IntoDataFrameT]

Alignment = t.Literal["start", "end", "left", "center", "right", "top", "horizon", "bottom"]
Auto = t.Literal["auto"]

Gutter = Auto | str
Relative = str

Placement = t.Literal["left", "right"]

DateStyle = t.Literal[
    "iso",
    "wday_month_day_year",
    "wd_m_day_year",
    "wday_day_month_year",
    "month_day_year",
    "m_day_year",
    "day_m_year",
    "day_month_year",
    "day_month",
    "day_m",
    "year",
    "month",
    "day",
    "year.mn.day",
    "y.mn.day",
    "year_week",
    "year_quarter",
]

TimeStyle = t.Literal[
    "iso",
    "iso-short",
    "h_m_s_p",
    "h_m_p",
    "h_p",
]

TfStyle = t.Literal[
    "true-false",
    "yes-no",
    "up-down",
    "check-mark",
    "circles",
    "squares",
    "diamonds",
    "arrows",
    "triangles",
    "triangles-lr",
]

BytesStyle = t.Literal["decimal", "binary"]
