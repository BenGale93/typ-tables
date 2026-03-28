"""Module containing cell formatting.

Numeric formatting code is taken from Great-Tables and adapted slightly.
"""

import math
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
                cond = nw.col(col).is_null()

            when = _create_when(col, rows, nw.lit(self.missing_text), cond)
            whens.append(when)
        return data.with_columns(whens)


@dataclass
class FString:
    """Formats columns using the Polars fstring format."""

    f_string: str

    def fmt(self, data: ttypes.Data, cols: list[str], rows: list[int]) -> ttypes.Data:
        """Formatting missing values in the given columns and rows."""
        whens = [_create_when(col, rows, nw.format(self.f_string, nw.col(col))) for col in cols]
        return data.with_columns(whens)


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
        """Formatting missing values in the given columns and rows."""
        unique_rows = set(rows)
        new_cols = []
        for col in cols:
            new_col = nw.new_series(
                name=col,
                values=[self.fmt_value(value) if i in unique_rows else str(value) for i, value in enumerate(data[col])],
                backend=data.implementation,
            )
            new_cols.append(new_col)
        return data.with_columns(*new_cols)

    def fmt_value(self, value: object) -> object:
        """Formats an individual value."""
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return value
        elif not isinstance(value, float):
            return value

        return fmt_number(value, config=self)


def fmt_number(value: float, config: Numeric) -> str:
    """Formats the given number using the config."""
    value = value * config.scale_by

    is_negative = value < 0

    if config.compact:
        x_formatted = _format_number_compactly(value=value, config=config)
    else:
        x_formatted = _value_to_decimal_notation(value=value, config=config)

    if is_negative and config.accounting:
        x_formatted = f"({_remove_minus(x_formatted)})"

    if config.pattern != "{x}":
        x_formatted = config.pattern.replace("{x}", x_formatted)

    return x_formatted


def _remove_minus(string: str) -> str:
    return string.replace("-", "")


def _format_number_compactly(value: float, config: Numeric) -> str:
    if value == 0:
        return "0"

    if config.n_sigfig is not None:
        _validate_n_sigfig(n_sigfig=config.n_sigfig)

    # Determine the power index for the value and put it in the range of 0 to 5 which
    # corresponds to the list of suffixes `["", "K", "M", "B", "T", "Q"]`
    num_power_idx = math.floor(math.log(abs(value), 1000))
    num_power_idx = max(0, min(5, num_power_idx))

    # The `units_str` is obtained by indexing a list of suffixes with the `num_power_idx`
    units_str = ["", "K", "M", "B", "T", "Q"][num_power_idx]

    # Scale `x` value by a defined `base` value, this is done by dividing by the `base`
    # value (`1000`) raised to the power index
    value = value / 1000**num_power_idx

    # Format the value to decimal notation; this is done before the `byte_units` text
    # is affixed to the value
    x_formatted = _value_to_decimal_notation(value=value, config=config)

    # Create a `suffix_pattern` object for affixing the `units_str`, which is the
    # string that represents the 'K', 'M', 'B', 'T', or 'Q' suffix
    suffix_pattern = f"{{x}}{units_str}"

    return suffix_pattern.replace("{x}", x_formatted)


def _value_to_decimal_notation(value: float, config: Numeric) -> str:
    """Decimal notation.

    Returns a string value with the correct precision or fixed number of decimal places (with
    optional formatting of the decimal part).
    """
    is_positive = value > 0

    if config.n_sigfig:
        # If there is a value provided to `n_sigfig` then number formatting proceeds through the
        # significant digits pathway, which ignores `decimals` and any removal of trailing zero values
        # in the decimal portion of the value
        result = _format_number_n_sigfig(
            value=value,
            n_sigfig=config.n_sigfig,
            use_seps=config.use_seps,
            sep_mark=config.sep_mark,
            dec_mark=config.dec_mark,
        )

    else:
        # If there is nothing provided to `n_sigfig` then the conventional decimal number formatting
        # pathway is taken; this formats to a specific number of decimal places and removal of
        # trailing zero values can be undertaken
        result = _format_number_fixed_decimals(
            value=value,
            decimals=config.decimals,
            drop_trailing_zeros=config.drop_trailing_zeros,
            use_seps=config.use_seps,
            sep_mark=config.sep_mark,
            dec_mark=config.dec_mark,
        )

    if config.drop_trailing_dec_mark:
        result = result.rstrip(config.dec_mark)

    if config.drop_trailing_dec_mark is False and config.dec_mark not in result:
        result = result + config.dec_mark

    if is_positive and config.force_sign:
        result = "+" + result

    return result


def _format_number_n_sigfig(
    value: float,
    *,
    n_sigfig: int,
    use_seps: bool = True,
    sep_mark: str = ",",
    dec_mark: str = ".",
) -> str:
    sig_digits, power, is_negative = _get_number_profile(value, n_sigfig)

    formatted_value = ("-" if is_negative else "") + _insert_decimal_mark(digits=sig_digits, power=power, dec_mark=".")

    # Get integer and decimal parts
    # Split number at `.` and obtain the integer and decimal parts
    number_parts = formatted_value.split(".")
    integer_part = number_parts[0].lstrip("-")
    decimal_part = number_parts[1] if len(number_parts) > 1 else ""

    # Initialize formatted representations of integer and decimal parts
    formatted_integer = ""
    formatted_decimal = dec_mark + decimal_part if decimal_part else ""

    # Insert grouping separators within the integer part
    if use_seps:
        for count, digit in enumerate(reversed(integer_part)):
            if count and count % 3 == 0:
                formatted_integer = sep_mark + formatted_integer
            formatted_integer = digit + formatted_integer
    else:
        formatted_integer = integer_part

    # Add back the negative sign if the number is negative
    if is_negative:
        formatted_integer = "-" + formatted_integer

    # Combine the integer and decimal parts
    return formatted_integer + formatted_decimal


def _format_number_fixed_decimals(  # noqa: PLR0913
    value: float,
    *,
    decimals: int,
    drop_trailing_zeros: bool = False,
    use_seps: bool = True,
    sep_mark: str = ",",
    dec_mark: str = ".",
) -> str:
    is_negative = value < 0

    fmt_spec = f".{decimals}f"

    # Get the formatted `x` value
    value_str = format(value, fmt_spec)

    # Split number at `.` and obtain the integer and decimal parts
    number_parts = value_str.split(".")
    integer_part = number_parts[0].lstrip("-")
    decimal_part = number_parts[1] if len(number_parts) > 1 else ""

    # Initialize formatted representations of integer and decimal parts
    formatted_integer = ""
    formatted_decimal = dec_mark + decimal_part if decimal_part else ""

    # Insert grouping separators within the integer part
    if use_seps:
        for count, digit in enumerate(reversed(integer_part)):
            if count and count % 3 == 0:
                formatted_integer = sep_mark + formatted_integer
            formatted_integer = digit + formatted_integer
    else:
        formatted_integer = integer_part

    # Add back the negative sign if the number is negative
    if is_negative:
        formatted_integer = "-" + formatted_integer

    # Combine the integer and decimal parts
    result = formatted_integer + formatted_decimal

    # Drop any trailing zeros if option is taken (this purposefully doesn't apply to numbers
    # formatted to a specific number of significant digits)
    if drop_trailing_zeros:
        result = result.rstrip("0")

    return result


def _get_number_profile(value: float, n_sigfig: int) -> tuple[str, int, bool]:
    """Get key components of a number for decimal number formatting.

    Returns a tuple containing: (1) a string value of significant digits, (2) an
    exponent to get the decimal mark to the proper location, and (3) a boolean
    value that's True if the value is less than zero (i.e., negative).
    """
    value = float(value)
    is_negative = value < 0
    value = abs(value)

    if value == 0:
        sig_digits = "0" * n_sigfig
        power = -(1 - n_sigfig)
    else:
        power = -1 * math.floor(math.log10(value)) + n_sigfig - 1
        value_power = value * 10.0**power

        if value < 1 and math.floor(math.log10(round(value_power))) > math.floor(
            math.log10(int(value_power))
        ):  # pragma: no cover
            power -= 1

        sig_digits = str(round(value * 10.0**power))

    return sig_digits, -power, is_negative


def _insert_decimal_mark(digits: str, power: int, dec_mark: str) -> str:
    """Places the decimal mark in the correct location within the digits.

    Should the decimal mark be outside the numeric range, zeros will be added.
    If `drop_trailing_zeros` is True, trailing decimal zeros will be removed.

    Examples:
      _insert_decimal_mark("123",   2, False) => "12300"
      _insert_decimal_mark("123",  -2, False) => "1.23"
      _insert_decimal_mark("123",   3, False) => "0.123"
      _insert_decimal_mark("123",   5, False) => "0.00123"
      _insert_decimal_mark("120",   0, False) => "120."
      _insert_decimal_mark("1200", -2, False) => "12.00"
      _insert_decimal_mark("1200", -2, True ) => "12"
      _insert_decimal_mark("1200", -1, False) => "120.0"
      _insert_decimal_mark("1200", -1, True ) => "120"
    """
    if power > 0:
        out = digits + "0" * power

    elif power < 0:
        power = abs(power)
        n_sigfig = len(digits)

        if power < n_sigfig:
            out = digits[:-power] + dec_mark + digits[-power:]

        else:
            out = "0" + dec_mark + "0" * (power - n_sigfig) + digits

    else:
        out = digits + (dec_mark if digits[-1] == "0" and len(digits) > 1 else "")

    return out


def _validate_n_sigfig(n_sigfig: int) -> None:  # pragma: no cover
    """Validates the input for the number of significant figures.

    Args:
        n_sigfig (int): The number of significant figures to validate.

    Raises:
        ValueError: If the length of `n_sigfig` is not 1, or if the value is `None` or less than 1.
        TypeError: If the input for `n_sigfig` is not an integer.

    Returns:
        None
    """
    if isinstance(n_sigfig, (list, tuple)):
        msg = "Any input for `n_sigfig` must be a scalar value."
        raise TypeError(msg)
    if not isinstance(n_sigfig, int):
        msg = "Any input for `n_sigfig` must be an integer."
        raise TypeError(msg)
    if n_sigfig < 1:
        msg = "The value for `n_sigfig` must be greater than or equal to `1`."
        raise ValueError(msg)
