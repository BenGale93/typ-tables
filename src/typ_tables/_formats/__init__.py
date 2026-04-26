"""Module containing cell formatting.

Numeric formatting code is taken from Great-Tables and adapted slightly.
"""

import typing as t
from dataclasses import asdict, dataclass

import narwhals as nw

from typ_tables import _location, ttypes
from typ_tables._constants import ROW_INDEX
from typ_tables._escape import formatted
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
                cond = nw.col(col).is_null() | (nw.col(col).str.contains("nan"))

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


def _coerce_value_to_numeric(value: object) -> float | int | str | None:
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return value
    elif value is None:
        return value
    elif not isinstance(value, (float, int)):  # pragma: no cover
        return str(value)
    return value


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
        value = _coerce_value_to_numeric(value)
        if not isinstance(value, (float, int)):
            return value

        nan_or_inf = _numeric.is_nan_or_inf(value)

        value = value * self.scale_by

        is_negative = value < 0

        if nan_or_inf:
            value_formatted = str(value)
        elif self.compact:
            value_formatted = _numeric.format_number_compactly(value=value, config=self)
        else:
            value_formatted = _numeric.value_to_decimal_notation(value=value, config=self)

        if is_negative and self.accounting:
            value_formatted = f"({_numeric.remove_minus(value_formatted)})"

        value_formatted = formatted(value_formatted)

        if self.pattern != "{x}":
            value_formatted = self.pattern.replace("{x}", value_formatted)

        return value_formatted


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


@dataclass
class Percentage:
    """Format percentage columns."""

    decimals: int
    drop_trailing_zeros: bool
    drop_trailing_dec_mark: bool
    scale_values: bool
    use_seps: bool
    accounting: bool
    pattern: str
    sep_mark: str
    dec_mark: str
    force_sign: bool
    placement: ttypes.Placement
    incl_space: bool

    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formatting percentage values in the given columns and rows."""
        return _format_by_cell(data, cols, rows, self.fmt_value)

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        scale_by = 100 if self.scale_values else 1
        value = _coerce_value_to_numeric(value)
        if not isinstance(value, (float, int)):
            return value

        numeric_config = Numeric(
            decimals=self.decimals,
            drop_trailing_zeros=self.drop_trailing_zeros,
            drop_trailing_dec_mark=self.drop_trailing_dec_mark,
            scale_by=scale_by,
            use_seps=self.use_seps,
            sep_mark=self.sep_mark,
            dec_mark=self.dec_mark,
            force_sign=False,
            accounting=False,
            n_sigfig=None,
            compact=False,
            pattern="{x}",
        )

        value = value * scale_by

        if _numeric.is_nan_or_inf(value):
            return str(value)

        value_formatted = _numeric.value_to_decimal_notation(value=value, config=numeric_config)

        is_negative = value < 0
        is_positive = value > 0

        percent_mark = "%"

        space_character = " " if self.incl_space else ""
        percent_pattern = (
            f"{{x}}{space_character}{percent_mark}"
            if self.placement == "right"
            else f"{percent_mark}{space_character}{{x}}"
        )

        if is_negative and self.placement == "left":
            value_formatted = value_formatted.replace("-", "")
            value_formatted = percent_pattern.replace("{x}", value_formatted)
            value_formatted = "-" + value_formatted
        elif is_positive and self.force_sign and self.placement == "left":
            value_formatted = value_formatted.replace("+", "")
            value_formatted = percent_pattern.replace("{x}", value_formatted)
            value_formatted = "+" + value_formatted
        else:
            value_formatted = percent_pattern.replace("{x}", value_formatted)

        value_formatted = formatted(value_formatted)

        if is_negative and self.accounting:
            value_formatted = f"({_numeric.remove_minus(value_formatted)})"

        if self.pattern != "{x}":
            value_formatted = self.pattern.replace("{x}", value_formatted)

        return value_formatted


@dataclass
class Scientific:
    """Format scientific columns."""

    decimals: int
    n_sigfig: int | None
    drop_trailing_zeros: bool
    drop_trailing_dec_mark: bool
    scale_by: float
    pattern: str
    sep_mark: str
    dec_mark: str
    force_sign_m: bool
    force_sign_n: bool

    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formatting scientific values in the given columns and rows."""
        return _format_by_cell(data, cols, rows, self.fmt_value)

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        value = _coerce_value_to_numeric(value)
        if not isinstance(value, (float, int)):
            return value

        nan_or_inf = _numeric.is_nan_or_inf(value)

        value = value * self.scale_by

        if nan_or_inf:
            value_formatted = str(value)
        else:
            is_positive = value > 0

            value_sci_notn = _numeric.value_to_scientific_notation(
                value=value,
                decimals=self.decimals,
                n_sigfig=self.n_sigfig,
                dec_mark=self.dec_mark,
            )
            sci_parts = value_sci_notn.split("E")

            m_part, n_part = sci_parts

            if self.drop_trailing_zeros:
                m_part = m_part.rstrip("0")
            if self.drop_trailing_dec_mark:
                m_part = m_part.rstrip(".")

            if is_positive and self.force_sign_m:
                m_part = f"+{m_part}"

            small_pos = _numeric.has_sci_order_zero(value=value)

            if self.force_sign_n and not _numeric.str_detect(n_part, "-"):
                n_part = "+" + n_part

            value_formatted = m_part if small_pos else f"{m_part} #sym.times 10#super[{n_part}]"

        value_formatted = formatted(value_formatted)

        if self.pattern != "{x}":
            value_formatted = self.pattern.replace("{x}", value_formatted)

        return value_formatted


@dataclass
class Engineering:
    """Format engineering columns.

    Engineering notation is like scientific notation, but the exponent is always
    a multiple of 3. This makes it convenient for expressing values in SI units
    (e.g., 1.23E3 = 1.23 k, 1.23E6 = 1.23 M, etc.).
    """

    decimals: int
    n_sigfig: int | None
    drop_trailing_zeros: bool
    drop_trailing_dec_mark: bool
    scale_by: float
    pattern: str
    sep_mark: str
    dec_mark: str
    force_sign_m: bool
    force_sign_n: bool

    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formatting engineering values in the given columns and rows."""
        return _format_by_cell(data, cols, rows, self.fmt_value)

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        value = _coerce_value_to_numeric(value)
        if not isinstance(value, (float, int)):
            return value

        nan_or_inf = _numeric.is_nan_or_inf(value)

        value = value * self.scale_by

        if nan_or_inf:
            value_formatted = str(value)
        else:
            is_positive = value > 0

            value_eng_notn = _numeric.value_to_engineering_notation(
                value=value,
                decimals=self.decimals,
                n_sigfig=self.n_sigfig,
                dec_mark=self.dec_mark,
            )
            eng_parts = value_eng_notn.split("E")

            m_part, n_part = eng_parts

            if self.drop_trailing_zeros:
                m_part = m_part.rstrip("0")
            if self.drop_trailing_dec_mark:
                m_part = m_part.rstrip(".")

            if is_positive and self.force_sign_m:
                m_part = f"+{m_part}"

            small_pos = _numeric.has_sci_order_zero(value=value)

            if self.force_sign_n and not _numeric.str_detect(n_part, "-"):
                n_part = "+" + n_part

            value_formatted = m_part if small_pos else f"{m_part} #sym.times 10#super[{n_part}]"

        value_formatted = formatted(value_formatted)

        if self.pattern != "{x}":
            value_formatted = self.pattern.replace("{x}", value_formatted)

        return value_formatted
