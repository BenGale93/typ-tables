"""Module containing cell formatting.

Numeric formatting code is taken from Great-Tables and adapted slightly.
"""

import math
import typing as t
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import date, datetime, time

import narwhals as nw

from typ_tables import _locale, _location, ttypes
from typ_tables._constants import ROW_INDEX
from typ_tables._escape import formatted
from typ_tables._formats import _datetime, _numeric
from typ_tables._formats._numeric import NumericSubConfig


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


def _apply_pattern(value: str, pattern: str) -> str:
    value = formatted(value)
    if pattern != "{x}":
        value = pattern.replace("{x}", value)
    return value


def _apply_accounting(value: str, is_negative: bool) -> str:  # noqa: FBT001
    if is_negative:
        return f"({_numeric.remove_minus(value)})"
    return value


def _create_affix_pattern(  # noqa: PLR0913
    value_formatted: str,
    affix: str,
    placement: ttypes.Placement,
    *,
    incl_space: bool,
    is_negative: bool,
    is_positive: bool,
    force_sign: bool,
) -> str:
    space_character = " " if incl_space else ""
    affix_pattern = (
        f"{{x}}{space_character}{affix}"
        if placement == "right"
        else f"{affix}{space_character}{{x}}"
    )

    if is_negative and placement == "left":
        value_formatted = value_formatted.replace("-", "")
        value_formatted = affix_pattern.replace("{x}", value_formatted)
        value_formatted = "-" + value_formatted
    elif is_positive and force_sign and placement == "left":
        value_formatted = value_formatted.replace("+", "")
        value_formatted = affix_pattern.replace("{x}", value_formatted)
        value_formatted = "+" + value_formatted
    else:
        value_formatted = affix_pattern.replace("{x}", value_formatted)
    return value_formatted


class CellFormatter(ABC):
    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formatting numeric values in the given columns and rows."""
        return _format_by_cell(data, cols, rows, self.fmt_value)

    @abstractmethod
    def fmt_value(self, value: object) -> str | None:
        pass


@dataclass
class Numeric(CellFormatter):
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

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        value = _coerce_value_to_numeric(value)
        if not isinstance(value, (float, int)):
            return value

        nan_or_inf = _numeric.is_nan_or_inf(value)

        value = value * self.scale_by

        is_negative = value < 0

        sub_config = NumericSubConfig(
            decimals=self.decimals,
            n_sigfig=self.n_sigfig,
            drop_trailing_zeros=self.drop_trailing_zeros,
            drop_trailing_dec_mark=self.drop_trailing_dec_mark,
            use_seps=self.use_seps,
            sep_mark=self.sep_mark,
            dec_mark=self.dec_mark,
            force_sign=self.force_sign,
        )

        if nan_or_inf:
            value_formatted = str(value)
        elif self.compact:
            value_formatted = _numeric.format_number_compactly(value=value, config=sub_config)
        else:
            value_formatted = _numeric.value_to_decimal_notation(value=value, config=sub_config)

        if self.accounting:
            value_formatted = _apply_accounting(value_formatted, is_negative)

        return _apply_pattern(value_formatted, self.pattern)


@dataclass
class Integer(CellFormatter):
    """Format integer columns."""

    use_seps: bool
    accounting: bool
    scale_by: float
    compact: bool
    sep_mark: str
    force_sign: bool
    pattern: str

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
class Percentage(CellFormatter):
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

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        scale_by = 100 if self.scale_values else 1
        value = _coerce_value_to_numeric(value)
        if not isinstance(value, (float, int)):
            return value

        sub_config = NumericSubConfig(
            decimals=self.decimals,
            n_sigfig=None,
            drop_trailing_zeros=self.drop_trailing_zeros,
            drop_trailing_dec_mark=self.drop_trailing_dec_mark,
            use_seps=self.use_seps,
            sep_mark=self.sep_mark,
            dec_mark=self.dec_mark,
            force_sign=self.force_sign,
        )

        is_negative = value < 0
        if _numeric.is_nan_or_inf(value):
            value_formatted = str(value)
        else:
            value = value * scale_by
            value_formatted = _numeric.value_to_decimal_notation(value=value, config=sub_config)

            is_positive = value > 0

            percent_mark = "%"
            value_formatted = _create_affix_pattern(
                value_formatted,
                percent_mark,
                placement=self.placement,
                incl_space=self.incl_space,
                is_negative=is_negative,
                is_positive=is_positive,
                force_sign=self.force_sign,
            )

        if self.accounting:
            value_formatted = _apply_accounting(value_formatted, is_negative)

        return _apply_pattern(value_formatted, self.pattern)


@dataclass
class Scientific(CellFormatter):
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

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        value = _coerce_value_to_numeric(value)
        if not isinstance(value, (float, int)):
            return value

        if _numeric.is_nan_or_inf(value):
            value_formatted = str(value)
        else:
            value = value * self.scale_by
            is_positive = value > 0

            value_notn = self._to_notation(value)

            sci_parts = value_notn.split("E")

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

        return _apply_pattern(value_formatted, self.pattern)

    def _to_notation(self, value: float) -> str:
        return _numeric.value_to_scientific_notation(
            value=value,
            decimals=self.decimals,
            n_sigfig=self.n_sigfig,
            dec_mark=self.dec_mark,
        )


@dataclass
class Engineering(Scientific):
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

    def _to_notation(self, value: float) -> str:
        return _numeric.value_to_engineering_notation(
            value=value,
            decimals=self.decimals,
            n_sigfig=self.n_sigfig,
            dec_mark=self.dec_mark,
        )


@dataclass
class Currency(CellFormatter):
    """Format currency columns."""

    currency: str
    use_subunits: bool
    decimals: int
    drop_trailing_dec_mark: bool
    use_seps: bool
    accounting: bool
    scale_by: float
    compact: bool
    pattern: str
    sep_mark: str
    dec_mark: str
    force_sign: bool
    placement: ttypes.Placement
    incl_space: bool

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        value = _coerce_value_to_numeric(value)
        if not isinstance(value, (float, int)):
            return value

        is_negative = value < 0

        if _numeric.is_nan_or_inf(value):
            value_formatted = str(value)
        else:
            value = value * self.scale_by

            is_positive = value > 0

            currency_symbol = _locale.get_currency_str(self.currency)

            if currency_symbol == "$":
                currency_symbol = r"\$"

            sub_config = NumericSubConfig(
                decimals=self.decimals,
                n_sigfig=None,
                drop_trailing_zeros=False,
                drop_trailing_dec_mark=self.drop_trailing_dec_mark,
                use_seps=self.use_seps,
                sep_mark=self.sep_mark,
                dec_mark=self.dec_mark,
                force_sign=self.force_sign,
            )

            if self.compact:
                value_formatted = _numeric.format_number_compactly(value=value, config=sub_config)
            else:
                value_formatted = _numeric.value_to_decimal_notation(value=value, config=sub_config)

            value_formatted = _create_affix_pattern(
                value_formatted,
                currency_symbol,
                placement=self.placement,
                incl_space=self.incl_space,
                is_negative=is_negative,
                is_positive=is_positive,
                force_sign=self.force_sign,
            )

        if self.accounting:
            value_formatted = _apply_accounting(value_formatted, is_negative)

        return _apply_pattern(value_formatted, self.pattern)


@dataclass
class Date(CellFormatter):
    """Format date columns.

    Format input values to date values using one of 17 preset date styles.
    Input can be in the form of `date` type or as an ISO-8601 string
    (in the form of `YYYY-MM-DD HH:MM:SS` or `YYYY-MM-DD`).
    """

    date_style: ttypes.DateStyle = "iso"
    pattern: str = "{x}"

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        if value is None:
            return None

        # If `value` is a string, we assume it is an ISO date string and convert it to a date object
        if isinstance(value, str):
            # Convert the ISO date string to a date object
            value = datetime.fromisoformat(value).date()

        # Stop if `value` is not a valid date object
        elif not isinstance(value, date):
            msg = f"Invalid date object: '{value}'. The object must be a date object."
            raise ValueError(msg)  # noqa: TRY004

        # Get the date format string based on the `date_style` value
        date_format_str = _datetime.get_date_format(self.date_style)

        # Format the date object to a string using strftime
        value_formatted = value.strftime(date_format_str)

        return _apply_pattern(value_formatted, self.pattern)


@dataclass
class Time(CellFormatter):
    """Format time columns.

    Format input values to time values using one of 5 preset time styles.
    Input can be in the form of `time` values, or strings in the ISO 8601
    forms of `HH:MM:SS` or `YYYY-MM-DD HH:MM:SS`.
    """

    time_style: ttypes.TimeStyle = "iso"
    pattern: str = "{x}"

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        if value is None:
            return None

        # If `value` is a string, assume it is an ISO time string and convert it to a time object
        if isinstance(value, str):
            # Convert the ISO time string to a time object
            value = time.fromisoformat(value)

        # Stop if `value` is not a valid time object
        elif not isinstance(value, time):
            msg = f"Invalid time object: '{value}'. The object must be a time object."
            raise ValueError(msg)  # noqa: TRY004

        # Get the time format string based on the `time_style` value
        time_format_str = _datetime.get_time_format(self.time_style)

        # Format the time object to a string using strftime
        value_formatted = value.strftime(time_format_str)

        return _apply_pattern(value_formatted, self.pattern)


@dataclass
class Datetime(CellFormatter):
    """Format datetime columns.

    Format input values to datetime values using one of 17 preset date styles
    and one of 5 preset time styles. Input can be in the form of `datetime` values,
    or strings in the ISO 8601 forms of `YYYY-MM-DD HH:MM:SS` or `YYYY-MM-DD`.
    """

    date_style: ttypes.DateStyle = "iso"
    time_style: ttypes.TimeStyle = "iso"
    format_str: str | None = None
    sep: str = " "
    pattern: str = "{x}"

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        if value is None:
            return None

        # If `value` is a string, assume it is an ISO datetime string
        # and convert it to a datetime object
        if isinstance(value, str):
            # Convert the ISO datetime string to a datetime object
            value = datetime.fromisoformat(value)

        # Stop if `value` is not a valid datetime object
        elif not isinstance(value, datetime):
            msg = f"Invalid datetime object: '{value}'. The object must be a datetime object."
            raise ValueError(msg)  # noqa: TRY004

        if self.format_str is not None:
            value_formatted = value.strftime(self.format_str)
        else:
            # Get the date format string based on the `date_style` value
            date_format_str = _datetime.get_date_format(self.date_style)

            # Get the time format string based on the `time_style` value
            time_format_str = _datetime.get_time_format(self.time_style)

            # From the date and time format strings, create a datetime format string
            datetime_format_str = f"{date_format_str}{self.sep}{time_format_str}"

            # Format the datetime object to a string using strftime
            value_formatted = value.strftime(datetime_format_str)

        return _apply_pattern(value_formatted, self.pattern)


TF_FORMATS: dict[str, list[str]] = {
    "true-false": ["true", "false"],
    "yes-no": ["yes", "no"],
    "up-down": ["up", "down"],
    "check-mark": ["#sym.checkmark", "#sym.crossmark"],
    "circles": ["#sym.circle.filled", "#sym.circle"],
    "squares": ["#sym.square.filled", "#sym.square"],
    "diamonds": ["#sym.diamond.filled", "#sym.diamond"],
    "arrows": ["#sym.arrow.t", "#sym.arrow.b"],
    "triangles": ["#sym.triangle.filled.t", "#sym.triangle.filled.b"],
    "triangles-lr": ["#sym.triangle.filled.r", "#sym.triangle.filled.l"],
}


def _get_tf_vals(
    tf_style: str, true_val: str | None = None, false_val: str | None = None
) -> list[str]:
    """Get the `True`/`False` text values based on the `tf_style`, with optional overrides.

    Args:
        tf_style: The `True`/`False` mapping style to use.
        true_val: Optional override for the True value.
        false_val: Optional override for the False value.

    Returns:
        A list of two strings representing the `True` and `False` values.

    Raises:
        ValueError: If `tf_style` is not a valid style.
    """
    # Get the base values from the TF_FORMATS dictionary
    if tf_style not in TF_FORMATS:
        msg = f"Invalid `tf_style`: {tf_style}. Must be one of {list(TF_FORMATS.keys())}."
        raise ValueError(msg)
    tf_vals = TF_FORMATS[tf_style].copy()

    # Override with provided values if any
    if true_val is not None:
        tf_vals[0] = true_val
    if false_val is not None:
        tf_vals[1] = false_val

    return tf_vals


@dataclass
class Tf(CellFormatter):
    """Format boolean columns.

    Format boolean values using preset styles or custom text values.
    Supports mapping True/False values to text or symbols.
    """

    tf_style: ttypes.TfStyle = "true-false"
    pattern: str = "{x}"
    true_val: str | None = None
    false_val: str | None = None
    na_val: str | None = None

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        # Handle None/NA values
        if value is None:
            if self.na_val is None:
                return None
            return self.na_val

        # Validate that the value is a boolean
        if not isinstance(value, bool):
            msg = f"Expected boolean value or NA, but got {type(value)}."
            raise ValueError(msg)  # noqa: TRY004

        # Get the True/False text values with overrides
        tf_vals = _get_tf_vals(
            tf_style=self.tf_style, true_val=self.true_val, false_val=self.false_val
        )

        # Get the appropriate text value
        value_formatted = tf_vals[0] if value else tf_vals[1]

        return _apply_pattern(value_formatted, self.pattern)


@dataclass
class Bytes(CellFormatter):
    """Format bytes columns.

    Format numeric values as bytes with human-readable units. Supports either
    decimal units (powers of 1000, e.g., "kB", "MB") or binary units (powers of
    1024, e.g., "KiB", "MiB"). Input values are assumed to represent the number
    of bytes and will be automatically scaled to the appropriate unit.
    """

    standard: ttypes.BytesStyle = "decimal"
    decimals: int = 1
    n_sigfig: int | None = None
    drop_trailing_zeros: bool = True
    drop_trailing_dec_mark: bool = True
    use_seps: bool = True
    pattern: str = "{x}"
    sep_mark: str = ","
    dec_mark: str = "."
    force_sign: bool = False
    incl_space: bool = True

    def fmt_value(self, value: object) -> str | None:
        """Formats an individual value."""
        value = _coerce_value_to_numeric(value)
        if not isinstance(value, (float, int)):
            return value

        if _numeric.is_nan_or_inf(value):
            value_formatted = str(value)
        else:
            # Truncate all byte values by casting to an integer; this is done because bytes
            # are always whole numbers
            value = int(value)

            # Get the `base` value and the `byte_units` list based on the `standard` value
            if self.standard == "decimal":
                # This is the 'decimal' standard (the default)
                base = 1000
                byte_units = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
            else:
                # This is the 'binary' standard
                base = 1024
                byte_units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]

            # Determine the power index for the value
            if value == 0:
                # If the value is zero, then the power index is 1; otherwise, we'd get
                # an error when trying to calculate the log of zero
                num_power_idx = 1
            else:
                # Otherwise, we can calculate the power index by taking the log of the value
                # and dividing by the log of the base; we add 1 to the result to account for
                # the fact that the power index is 1-based (i.e., the first element in the
                # `byte_units` list is at index 0) --- the final statement ensures that the
                # power index is always at least 1
                num_power_idx = math.floor(math.log(abs(value), base)) + 1
                num_power_idx = max(1, min(len(byte_units), num_power_idx))

            # The `units_str` is obtained by indexing the `byte_units` list with the `num_power_idx`
            # value; this is the string that will be affixed to the formatted value
            units_str = byte_units[num_power_idx - 1]

            # Scale `value` by a defined `base` value, this is done by dividing by the
            # `base` value raised to the power index minus 1 (we subtract 1 because the
            # power index is 1-based)
            value = value / base ** (num_power_idx - 1)

            # Format the value to decimal notation; this is done before the `byte_units` text
            # is affixed to the value

            sub_config = NumericSubConfig(
                decimals=self.decimals,
                n_sigfig=self.n_sigfig,
                drop_trailing_zeros=self.drop_trailing_zeros,
                drop_trailing_dec_mark=self.drop_trailing_dec_mark,
                use_seps=self.use_seps,
                sep_mark=self.sep_mark,
                dec_mark=self.dec_mark,
                force_sign=self.force_sign,
            )
            value_formatted = _numeric.value_to_decimal_notation(value=value, config=sub_config)

            # Create a `bytes_pattern` object for affixing the `units_str`, which is the
            # string that represents the byte units
            space_character = " " if self.incl_space else ""
            bytes_pattern = f"{{x}}{space_character}{units_str}"

            value_formatted = bytes_pattern.replace("{x}", value_formatted)

        return _apply_pattern(value_formatted, self.pattern)
