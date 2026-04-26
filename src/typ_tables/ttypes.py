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
