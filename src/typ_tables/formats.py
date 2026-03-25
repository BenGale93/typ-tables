"""Module containing cell formatting."""

import typing as t
from dataclasses import dataclass

import narwhals as nw

from typ_tables import location, ttypes
from typ_tables.constants import ROW_INDEX


class FormatFn(t.Protocol):
    """Protocol defining a formatting function."""

    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formats the data in the given columns and rows."""


@dataclass
class Formatter:
    """A Formatter container."""

    func: FormatFn
    cols: list[str]
    rows: list[int]

    def fmt(self, data: ttypes.Data) -> ttypes.Data:
        """Formats the given data."""
        return self.func.fmt(data, self.cols, self.rows)


def fmt(
    data: ttypes.Data,
    func: FormatFn,
    columns: location.ColumnSelector | None = None,
    rows: location.RowSelector | None = None,
) -> Formatter:
    """Create a formatter container."""
    cols = location.resolve_columns(data, columns)
    rows = location.resolve_rows(data, rows)

    return Formatter(func, cols, rows)


@dataclass
class SubMissing:
    """Substitutes missing values in a table."""

    missing_text: str = ""

    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formatting missing values in the given columns and rows."""
        whens = []
        for col in cols:
            if data.select(nw.col(col)).schema[col].is_numeric():
                cond = nw.col(col).is_null() | nw.col(col).is_nan()
            else:
                cond = nw.col(col).is_null()

            when = (
                nw.when(nw.col(ROW_INDEX).is_in(rows), cond)
                .then(nw.lit(self.missing_text))
                .otherwise(nw.col(col).cast(nw.String))
                .alias(col)
            )
            whens.append(when)
        return data.with_columns(whens)


@dataclass
class FString:
    """Formats columns using the Polars fstring format."""

    f_string: str

    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formatting missing values in the given columns and rows."""
        whens = []
        for col in cols:
            when = (
                nw.when(nw.col(ROW_INDEX).is_in(rows))
                .then(nw.format(self.f_string, nw.col(col)))
                .otherwise(nw.col(col).cast(nw.String))
                .alias(col)
            )
            whens.append(when)
        return data.with_columns(whens)
