"""Typ-Table Types."""

from narwhals import DataFrame
from narwhals.typing import IntoDataFrameT

Data = DataFrame[IntoDataFrameT]
