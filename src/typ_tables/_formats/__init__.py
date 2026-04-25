"""Module containing cell formatting.

Numeric formatting code is taken from Great-Tables and adapted slightly.
"""

import typing as t
from dataclasses import asdict, dataclass

import narwhals as nw

from typ_tables import _location, ttypes
from typ_tables._constants import ROW_INDEX
from typ_tables._formats import _numeric


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
    columns: _location.ColumnSelector | None = None,
    rows: _location.RowSelector | None = None,
) -> Formatter:
    """Create a formatter container."""
    cols = _location.resolve_columns(data, columns)
    rows = _location.resolve_rows(data, rows)

    return Formatter(func, cols, rows)


def _create_when(col: str, rows: list[int], then: nw.Expr, when: nw.Expr | None = None) -> nw.Expr:
    whens = [nw.col(ROW_INDEX).is_in(rows)]
    if when is not None:
        whens.append(when)
    return nw.when(*whens).then(then).otherwise(nw.col(col).cast(nw.String)).alias(col)


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
                cond = nw.col(col).is_null() | (nw.col(col) == nw.lit("nan"))

            when = _create_when(col, rows, nw.lit(self.missing_text), cond)
            whens.append(when)
        return data.with_columns(whens)


@dataclass
class FString:
    """Formats columns using the Polars fstring format."""

    f_string: str

    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formats values in the given columns and rows."""
        whens = [_create_when(col, rows, nw.format(self.f_string, nw.col(col))) for col in cols]
        return data.with_columns(whens)


def _format_by_cell(
    data: ttypes.Data, cols: list[str], rows: list[int], fmt_value: t.Callable[[object], str | None]
) -> ttypes.Data:
    unique_rows = set(rows)
    new_cols = []
    for col in cols:
        new_col = nw.new_series(
            name=col,
            values=[
                fmt_value(value) if i in unique_rows else str(value)
                for i, value in enumerate(data[col])
            ],
            backend=data.implementation,
        )
        new_cols.append(new_col)
    return data.with_columns(*new_cols)


@dataclass
class Numeric:
    """Format numeric columns."""

    decimals: int
    n_sigfig: int | None
    drop_trailing_zeros: bool
    drop_trailing_dec_mark: bool
    use_seps: bool
    accounting: bool
    scale_by: float
    compact: bool
    sep_mark: str
    dec_mark: str
    force_sign: bool
    pattern: str

    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formatting numeric values in the given columns and rows."""
        return _format_by_cell(data, cols, rows, self.fmt_value)

    def fmt_value(self, value: object) -> str | None:  # pragma: no cover
        """Formats an individual value."""
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return value
        elif value is None:
            return None
        elif not isinstance(value, (float, int)):
            return str(value)

        nan_or_inf = _numeric.is_nan_or_inf(value)

        value = value * self.scale_by

        is_negative = value < 0

        if nan_or_inf:
            x_formatted = str(value)
        elif self.compact:
            x_formatted = _numeric.format_number_compactly(value=value, config=self)
        else:
            x_formatted = _numeric.value_to_decimal_notation(value=value, config=self)

        if is_negative and self.accounting:
            x_formatted = f"({_numeric.remove_minus(x_formatted)})"

        if self.pattern != "{x}":
            x_formatted = self.pattern.replace("{x}", x_formatted)

        return x_formatted


@dataclass
class Integer:
    """Format integer columns."""

    use_seps: bool
    accounting: bool
    scale_by: float
    compact: bool
    sep_mark: str
    force_sign: bool
    pattern: str

    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formatting integer values in the given columns and rows."""
        return _format_by_cell(data, cols, rows, self.fmt_value)

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        numeric_config = Numeric(
            **asdict(self),
            decimals=0,
            n_sigfig=None,
            drop_trailing_zeros=False,
            drop_trailing_dec_mark=True,
            dec_mark="not used",
        )
        return numeric_config.fmt_value(value)
