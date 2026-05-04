"""Shared public type aliases used by TypTable APIs."""

import typing as t

from narwhals import DataFrame
from narwhals.typing import IntoDataFrameT

Data = DataFrame[IntoDataFrameT]
"""Narwhals eager DataFrame used internally after input normalization."""

Alignment = t.Literal["start", "end", "left", "center", "right", "top", "horizon", "bottom"]
"""Typst alignment keyword for table cell content."""
Auto = t.Literal["auto"]
"""Typst automatic value keyword."""

Gutter = Auto | str
"""Typst gutter value.

Use `"auto"` for Typst's automatic spacing, or a Typst-compatible string for a
specific gutter value.
"""
Relative = str
"""Typst relative length value.

Use a Typst-compatible string such as `"10pt"`, `"1em"`, or `"20%"`.
"""

Placement = t.Literal["left", "right"]
"""Side placement keyword."""

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
"""Named date formatting style."""

TimeStyle = t.Literal[
    "iso",
    "iso-short",
    "h_m_s_p",
    "h_m_p",
    "h_p",
]
"""Named time formatting style."""

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
"""Named true/false formatting style."""

BytesStyle = t.Literal["decimal", "binary"]
"""Named byte-size formatting standard."""
