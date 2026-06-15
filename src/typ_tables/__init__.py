"""Package for creating Typst Tables from DataFrames."""

import typing as t
from dataclasses import replace

import narwhals as nw
from narwhals.typing import IntoDataFrame

from typ_tables import locators, ttypes
from typ_tables._constants import ROW_INDEX
from typ_tables._escape import Typst
from typ_tables._formats import (
    Bytes,
    Currency,
    Date,
    Datetime,
    Engineering,
    FString,
    Integer,
    Numeric,
    Percentage,
    Scientific,
    SubMissing,
    Tf,
    Time,
    fmt,
)
from typ_tables._gutter import GutterContainer
from typ_tables._location import ColumnSelector, RowSelector, resolve_columns
from typ_tables._rendering import Table
from typ_tables._spanners import Spanner
from typ_tables._typ_data import Heading, TypData
from typ_tables._utils import OrderedSet
from typ_tables.style import CellStyle, Sides, TextStyle


def _create_table_string(original_data: ttypes.Data[IntoDataFrame], typ: TypData) -> str:
    """Render a complete Typst table string from data and table state.

    Args:
        original_data: Source data with internal row index column.
        typ: Table state containing formatting, labels, and style rules.

    Returns:
        A complete Typst table string, optionally wrapped in `#figure`.
    """
    data = typ.format_df(original_data).drop(ROW_INDEX)
    typ.stub.update_group_row_labels(data, typ.boxhead)

    typst_table = Table(
        columns=typ.columns(),
        row_gutter=typ.gutters.row.value,
        column_gutter=typ.gutters.column.value,
        stroke=typ.stroke,
        alignment=typ.alignment(),
        inset=typ.inset,
        headers=typ.header(data),
        footer=typ.footer(),
        body=typ.body(data, original_data),
    )

    return typ.figure.to_typst(typst_table).render()


P = t.ParamSpec("P")


class TypTable:
    """Build a Typst table from a DataFrame-like object.

    `TypTable` stores the source data plus table configuration such as
    formatting rules, labels, styling, row stubs, row groups, and Typst table
    options. Input data is normalized with Narwhals, so any eager DataFrame-like
    object supported by Narwhals can be used.
    """

    def __init__(
        self, df: IntoDataFrame, rowname_col: str | None = None, groupname_col: str | None = None
    ) -> None:
        """Initialize a `TypTable` from a DataFrame-like object.

        Args:
            df: Input DataFrame supported by Narwhals.
            rowname_col: Optional column used as row labels (stub column).
            groupname_col: Optional column used to group rows.

        Raises:
            ValueError: If `df` has zero columns.
            ValueError: If `groupname_col` is set without `rowname_col`.
        """
        if not len(df.columns):
            msg = "Data must have at least one column."
            raise ValueError(msg)
        if rowname_col is None and groupname_col is not None:
            msg = "If groupname_col is provided, so must rowname_col."
            raise ValueError(msg)
        self._df = nw.from_native(df, eager_only=True).with_row_index(ROW_INDEX)
        self._typ_data = TypData.from_data(self._df, rowname_col, groupname_col)

    def to_typst(self) -> str:
        """Render the configured table as Typst markup.

        Returns:
            Complete Typst string representing the table.
        """
        return _create_table_string(self._df, self._typ_data)

    def pipe(
        self, func: t.Callable[t.Concatenate[t.Self, P], t.Self], *args: P.args, **kwargs: P.kwargs
    ) -> t.Self:
        """Method to apply a function on a TypTable object in a method call chain.

        Args:
            func: A function that takes a TypTable as the first argument, and then any number
                of positional or keyword arguments. It then returns a TypTable object.
            *args: The optional positional arguments that func needs.
            **kwargs: The optional keyword arguments that func needs.

        Example:
            ```python
            def colour_max(tbl: TypTable, columns: list[str]) -> TypTable:
                for column in columns:
                    tbl = tbl.tab_style(
                        cell=style.CellStyle(fill="red"),
                        locator=locators.LocBody(
                            columns=column, rows=(nw.col(column) == nw.col(column).max())
                        ),
                    )
                return tbl


            TypTable(data).pipe(colour_max, ["column_a", "column_b"])
            ```

        Returns:
            The current table instance for chaining.
        """
        return func(self, *args, **kwargs)

    # Modifying parts of a Table Methods ----
    def tab_header(self, title: str | Typst, subtitle: str | Typst | None = None) -> t.Self:
        """Set table title and optional subtitle.

        The header is rendered above the column-label row and spans the full
        table width. This method changes only that title/subtitle region; it
        does not change column labels, row labels, or body cells.

        Args:
            title: Title text or raw Typst.
            subtitle: Optional subtitle text or raw Typst.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.heading = Heading(title, subtitle)
        return self

    def tab_figure(self, caption: str | Typst | None = None) -> t.Self:
        """Configure an optional figure caption wrapper around the table.

        When `caption` is provided, the rendered Typst table is wrapped in a
        Typst figure and the caption is attached to that figure. Passing `None`
        disables the figure wrapper and leaves the table itself unchanged.

        Args:
            caption: Caption text or raw Typst. `None` disables wrapping.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.figure = replace(self._typ_data.figure, _caption=caption)
        return self

    def tab_stubhead(self, label: str | Typst) -> t.Self:
        """Set the label shown in the stub header cell.

        The stub head is the top-left header cell above the row-label stub
        column. This method changes only that stub-head label; it does not
        rename row labels or data columns. The cell is only visible when the
        table has a stub column.

        Args:
            label: Stub header label text or raw Typst.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.stubhead = label
        return self

    def tab_footer(self, note: str | Typst) -> t.Self:
        """Add a note to the table footer.

        Footer notes are rendered below the table body in a single footer cell
        that spans the full table width. Repeated calls append additional notes
        to the same footer, separated by Typst line breaks.

        Args:
            note: Footer note text or raw Typst.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.footer_notes.append(note)
        return self

    def tab_style(
        self, locator: locators.Loc, text: TextStyle | None = None, cell: CellStyle | None = None
    ) -> t.Self:
        """Add style rules for a specific table region.

        Locators define which table region receives the supplied text style,
        cell style, or both. Use `LocHeader` for the title/subtitle region,
        `LocColumnLabels` for column names, `LocStub` for row labels,
        `LocStubhead` for the top-left stub label, `LocBody` for data cells,
        and `LocRowGroup` for row-group labels.

        Args:
            locator: Target region selector (for example `locators.LocHeader`).
            text: Optional text-level style settings.
            cell: Optional cell-level style settings.

        Returns:
            The current table instance for chaining.
        """
        styled_loc = locator._apply_style(self._df, text, cell)

        self._typ_data.styles.append(styled_loc)
        return self

    def tab_spanner(  # noqa: PLR0913
        self,
        label: str | Typst,
        columns: ColumnSelector | None = None,
        spanners: str | list[str] | None = None,
        level: int | None = None,
        id_: str | None = None,
        gather: bool = True,  # noqa: FBT001, FBT002
    ) -> t.Self:
        """Add a column spanner above selected columns or existing spanners.

        A spanner is a header cell that spans multiple columns. Select columns
        directly with `columns`, or select existing spanners by ID with
        `spanners` to create a higher-level grouped header. When `level` is not
        provided, the spanner is placed on the lowest level that does not
        overlap existing spanners.

        Args:
            label: Spanner label text or raw Typst.
            columns: Optional selector for columns to include in the spanner.
            spanners: Optional existing spanner ID or IDs whose columns should
                be included in the new spanner.
            level: Optional zero-based spanner level. If provided, overlapping
                spanners on that level have the new spanner's columns removed.
            id_: Optional unique identifier for the spanner. Defaults to
                `str(label)`.
            gather: Whether to move directly selected columns next to the first
                selected column when adding a bottom-level spanner.

        Raises:
            NotImplementedError: If neither `columns` nor `spanners` is provided.
            ValueError: If `level` is negative, `id_` duplicates an existing
                spanner ID, or a referenced spanner ID does not exist.
            ColumnNotFoundError: If `columns` references unknown columns.

        Returns:
            The current table instance for chaining.
        """
        selected_columns: list[str] = [] if columns is None else resolve_columns(self._df, columns)

        if isinstance(spanners, str):
            spanners = [spanners]
        selected_spanners: list[str] = [] if spanners is None else spanners

        if not len(selected_columns) and not len(selected_spanners):
            msg = "columns/spanners must be specified."
            raise NotImplementedError(msg)

        spanner_column_names = self._typ_data.spanners.get_columns(selected_spanners).as_list()

        column_names = OrderedSet([*selected_columns, *spanner_column_names]).as_list()

        spanner = Spanner.from_data(label=label, spanning=column_names, id_=id_)

        level = self._typ_data.spanners.add_spanner(spanner, level=level)

        if gather and not len(spanner_column_names) and level == 0 and len(column_names) > 1:
            return self.cols_move(column_names[1:], column_names[0])

        return self

    # Formatting Methods ----
    def sub_missing(
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        missing_text: str = "",
    ) -> t.Self:
        """Replace null-like values in selected cells.

        Args:
            columns: Optional column selector limiting where substitution applies.
            rows: Optional row selector limiting where substitution applies.
            missing_text: Replacement text used for missing values.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.substitute.append(
            fmt(self._df, SubMissing(missing_text=missing_text), columns, rows)
        )
        return self

    def fmt(
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        f_string: str,
    ) -> t.Self:
        """Format selected values with a Narwhals-style f-string.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            f_string: Format string used to render each selected value.

        Returns:
            The current table instance for chaining.

        Note:
            Currently only accepts 1 placeholder.
        """
        self._typ_data.formats.append(fmt(self._df, FString(f_string), columns, rows))
        return self

    def fmt_number(  # noqa: PLR0913
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        decimals: int = 2,
        n_sigfig: int | None = None,
        drop_trailing_zeros: bool = False,
        drop_trailing_dec_mark: bool = True,
        use_seps: bool = True,
        accounting: bool = False,
        scale_by: float = 1,
        compact: bool = False,
        pattern: str = "{x}",
        dec_mark: str = ".",
        sep_mark: str = ",",
        force_sign: bool = False,
    ) -> t.Self:
        """Format selected numeric values with configurable numeric rules.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            decimals: Number of decimal places.
            n_sigfig: Optional number of significant figures.
            drop_trailing_zeros: Whether to remove trailing zero digits.
            drop_trailing_dec_mark: Whether to remove dangling decimal marks.
            use_seps: Whether to include thousands separators.
            accounting: Whether to use accounting-style negatives.
            scale_by: Multiplicative scaling factor before formatting.
            compact: Whether to compact large numbers (for example, `1K`).
            pattern: Output pattern containing `{x}` placeholder.
            dec_mark: Decimal mark character.
            sep_mark: Thousands separator character.
            force_sign: Whether to always show explicit sign symbols.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Numeric(
                    decimals=decimals,
                    n_sigfig=n_sigfig,
                    drop_trailing_zeros=drop_trailing_zeros,
                    drop_trailing_dec_mark=drop_trailing_dec_mark,
                    use_seps=use_seps,
                    accounting=accounting,
                    scale_by=scale_by,
                    compact=compact,
                    pattern=pattern,
                    dec_mark=dec_mark,
                    sep_mark=sep_mark,
                    force_sign=force_sign,
                ),
                columns,
                rows,
            )
        )
        return self

    def fmt_integer(  # noqa: PLR0913
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        use_seps: bool = True,
        accounting: bool = False,
        scale_by: float = 1,
        compact: bool = False,
        pattern: str = "{x}",
        sep_mark: str = ",",
        force_sign: bool = False,
    ) -> t.Self:
        """Format selected integer values with configurable integer rules.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            use_seps: Whether to include thousands separators.
            accounting: Whether to use accounting-style negatives.
            scale_by: Multiplicative scaling factor before formatting.
            compact: Whether to compact large numbers (for example, `1K`).
            pattern: Output pattern containing `{x}` placeholder.
            sep_mark: Thousands separator character.
            force_sign: Whether to always show explicit sign symbols.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Integer(
                    use_seps=use_seps,
                    accounting=accounting,
                    scale_by=scale_by,
                    compact=compact,
                    pattern=pattern,
                    sep_mark=sep_mark,
                    force_sign=force_sign,
                ),
                columns,
                rows,
            )
        )
        return self

    def fmt_percentage(  # noqa: PLR0913
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        decimals: int = 2,
        drop_trailing_zeros: bool = False,
        drop_trailing_dec_mark: bool = True,
        scale_values: bool = True,
        use_seps: bool = True,
        accounting: bool = False,
        pattern: str = "{x}",
        dec_mark: str = ".",
        sep_mark: str = ",",
        force_sign: bool = False,
        placement: ttypes.Placement = "right",
        incl_space: bool = False,
    ) -> t.Self:
        """Format selected numeric values as percentages.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            decimals: Number of decimal places.
            drop_trailing_zeros: Whether to remove trailing zero digits.
            drop_trailing_dec_mark: Whether to remove dangling decimal marks.
            scale_values: Should the values be scaled through multiplication by 100?
            use_seps: Whether to include thousands separators.
            accounting: Whether to use accounting-style negatives.
            pattern: Output pattern containing `{x}` placeholder.
            sep_mark: Thousands separator character.
            dec_mark: Decimal mark character.
            force_sign: Whether to always show explicit sign symbols.
            placement: Where to place the percent sign. Can be `left` or `right`.
            incl_space: An option for whether to include a space between the
                value and the percent sign.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Percentage(
                    decimals=decimals,
                    drop_trailing_zeros=drop_trailing_zeros,
                    drop_trailing_dec_mark=drop_trailing_dec_mark,
                    scale_values=scale_values,
                    use_seps=use_seps,
                    accounting=accounting,
                    pattern=pattern,
                    sep_mark=sep_mark,
                    dec_mark=dec_mark,
                    force_sign=force_sign,
                    placement=placement,
                    incl_space=incl_space,
                ),
                columns,
                rows,
            )
        )
        return self

    def fmt_scientific(  # noqa: PLR0913
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        decimals: int = 2,
        n_sigfig: int | None = None,
        drop_trailing_zeros: bool = False,
        drop_trailing_dec_mark: bool = True,
        scale_by: float = 1,
        pattern: str = "{x}",
        sep_mark: str = ",",
        dec_mark: str = ".",
        force_sign_m: bool = False,
        force_sign_n: bool = False,
    ) -> t.Self:
        """Format selected numeric values in scientific notation.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            decimals: Number of decimal places.
            n_sigfig: Optional number of significant figures.
            drop_trailing_zeros: Whether to remove trailing zero digits.
            drop_trailing_dec_mark: Whether to remove dangling decimal marks.
            scale_by: Multiplicative scaling factor before formatting.
            pattern: Output pattern containing `{x}` placeholder.
            sep_mark: Thousands separator character.
            dec_mark: Decimal mark character.
            force_sign_m: Should the plus sign be shown for positive values of
                the mantissa (first component)?
            force_sign_n: Should the plus sign be shown for positive values of
                the exponent (second component)?

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Scientific(
                    decimals=decimals,
                    n_sigfig=n_sigfig,
                    drop_trailing_zeros=drop_trailing_zeros,
                    drop_trailing_dec_mark=drop_trailing_dec_mark,
                    scale_by=scale_by,
                    pattern=pattern,
                    sep_mark=sep_mark,
                    dec_mark=dec_mark,
                    force_sign_m=force_sign_m,
                    force_sign_n=force_sign_n,
                ),
                columns,
                rows,
            )
        )
        return self

    def fmt_engineering(  # noqa: PLR0913
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        decimals: int = 2,
        n_sigfig: int | None = None,
        drop_trailing_zeros: bool = False,
        drop_trailing_dec_mark: bool = True,
        scale_by: float = 1,
        pattern: str = "{x}",
        sep_mark: str = ",",
        dec_mark: str = ".",
        force_sign_m: bool = False,
        force_sign_n: bool = False,
    ) -> t.Self:
        """Format selected numeric values with engineering notation.

        Engineering notation is like scientific notation, but the exponent is
        always a multiple of 3. This makes it convenient for expressing values
        in SI units, such as `1.23E3` for thousands or `1.23E6` for millions.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            decimals: Number of decimal places.
            n_sigfig: Optional number of significant figures.
            drop_trailing_zeros: Whether to remove trailing zero digits.
            drop_trailing_dec_mark: Whether to remove dangling decimal marks.
            scale_by: Multiplicative scaling factor before formatting.
            pattern: Output pattern containing `{x}` placeholder.
            sep_mark: Thousands separator character.
            dec_mark: Decimal mark character.
            force_sign_m: Should the plus sign be shown for positive values of
                the mantissa (first component)?
            force_sign_n: Should the plus sign be shown for positive values of
                the exponent (second component)?

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Engineering(
                    decimals=decimals,
                    n_sigfig=n_sigfig,
                    drop_trailing_zeros=drop_trailing_zeros,
                    drop_trailing_dec_mark=drop_trailing_dec_mark,
                    scale_by=scale_by,
                    pattern=pattern,
                    sep_mark=sep_mark,
                    dec_mark=dec_mark,
                    force_sign_m=force_sign_m,
                    force_sign_n=force_sign_n,
                ),
                columns,
                rows,
            )
        )
        return self

    def fmt_currency(  # noqa: PLR0913
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        currency: str,
        use_subunits: bool = True,
        decimals: int = 2,
        drop_trailing_dec_mark: bool = True,
        use_seps: bool = True,
        accounting: bool = False,
        scale_by: float = 1,
        compact: bool = False,
        pattern: str = "{x}",
        sep_mark: str = ",",
        dec_mark: str = ".",
        force_sign: bool = False,
        placement: ttypes.Placement = "left",
        incl_space: bool = False,
    ) -> t.Self:
        """Format selected numeric values as currency.

        Currency symbols are resolved from the supplied three-letter currency
        code. Numeric formatting options follow the same conventions as
        `fmt_number`.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            currency: The currency to use for the numeric value.
                This input can be supplied as a 3-letter currency code.
            use_subunits: An option for whether the subunits portion of
                a currency value should be displayed.
            decimals: Number of decimal places.
            drop_trailing_dec_mark: Whether to remove dangling decimal marks.
            use_seps: Whether to include thousands separators.
            accounting: Whether to use accounting style, which wraps negative
                numbers in parentheses instead of using a minus sign.
            scale_by: Multiplicative scaling factor before formatting.
            compact: Whether to compact large numbers (for example, `1K`).
            pattern: Output pattern containing `{x}` placeholder.
            sep_mark: Thousands separator character.
            dec_mark: Decimal mark character.
            force_sign: Whether to always show explicit sign symbols.
            placement: Where to place the currency sign. Can be `left` or `right`.
            incl_space: An option for whether to include a space between the
                value and the currency sign.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Currency(
                    currency=currency,
                    use_subunits=use_subunits,
                    decimals=decimals,
                    drop_trailing_dec_mark=drop_trailing_dec_mark,
                    use_seps=use_seps,
                    accounting=accounting,
                    scale_by=scale_by,
                    compact=compact,
                    pattern=pattern,
                    sep_mark=sep_mark,
                    dec_mark=dec_mark,
                    force_sign=force_sign,
                    placement=placement,
                    incl_space=incl_space,
                ),
                columns,
                rows,
            )
        )
        return self

    def fmt_date(
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        date_style: ttypes.DateStyle = "iso",
        pattern: str = "{x}",
    ) -> t.Self:
        """Format selected date values with configurable date rules.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            date_style: The date style to use for formatting.
            pattern: Output pattern containing `{x}` placeholder.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Date(date_style=date_style, pattern=pattern),
                columns,
                rows,
            )
        )
        return self

    def fmt_time(
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        time_style: ttypes.TimeStyle = "iso",
        pattern: str = "{x}",
    ) -> t.Self:
        """Format selected time values with configurable time rules.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            time_style: The time style to use for formatting.
            pattern: Output pattern containing `{x}` placeholder.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Time(time_style=time_style, pattern=pattern),
                columns,
                rows,
            )
        )
        return self

    def fmt_datetime(  # noqa: PLR0913
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        date_style: ttypes.DateStyle = "iso",
        time_style: ttypes.TimeStyle = "iso",
        format_str: str | None = None,
        sep: str = " ",
        pattern: str = "{x}",
    ) -> t.Self:
        """Format selected datetime values with configurable date and time rules.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            date_style: The date style to use for formatting.
            time_style: The time style to use for formatting.
            format_str: Optional strftime format string.
                If provided, date_style and time_style are ignored.
            sep: Separator between date and time components.
            pattern: Output pattern containing `{x}` placeholder.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Datetime(
                    date_style=date_style,
                    time_style=time_style,
                    format_str=format_str,
                    sep=sep,
                    pattern=pattern,
                ),
                columns,
                rows,
            )
        )
        return self

    def fmt_tf(  # noqa: PLR0913
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        tf_style: ttypes.TfStyle = "true-false",
        pattern: str = "{x}",
        true_val: str | None = None,
        false_val: str | None = None,
        na_val: str | None = None,
    ) -> t.Self:
        """Format selected boolean values with configurable True/False rules.

        There can be times where boolean values are useful in a display table. You might want to
        express a 'yes' or 'no', a 'true' or 'false', or, perhaps use pairings of complementary
        symbols that make sense in a table. The `fmt_tf()` method has a set of `tf_style=` presets
        that can be used to quickly map `True`/`False` values to strings, or, symbols like up/down
        or left/right arrows and open/closed shapes.

        While the presets are nice, you can provide your own mappings through the `true_val=` and
        `false_val=` arguments. For extra customization, you can also handle missing values with
        the `na_val=` option.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            tf_style: The `True`/`False` mapping style to use. By default this is the short name
                `"true-false"` which corresponds to the words `"true"` and `"false"`. Two other
                `tf_style=` values produce words: `"yes-no"` and `"up-down"`. The remaining options
                involve pairs of symbols (e.g., `"check-mark"` displays a check mark for `True`
                and an ✗ symbol for `False`).
            pattern: A formatting pattern that allows for decoration of the formatted value. The
                formatted value is represented by the `{x}` (which can be used multiple times, if
                needed) and all other characters will be interpreted as string literals.
            true_val: While the choice of a `tf_style=` will typically supply the `true_val=` and
                `false_val=` text, we could override this and supply text for any `True` values.
                This doesn't need to be used in conjunction with `false_val=`.
            false_val: While the choice of a `tf_style=` will typically supply the `true_val=` and
                `false_val=` text, we could override this and supply text for any `False` values.
                This doesn't need to be used in conjunction with `true_val=`.
            na_val: None of the `tf_style` presets will replace any missing values encountered in
                the targeted cells. While we always have the option to use `sub_missing()` for NA
                replacement, we have the opportunity handle missing values here with the `na_val=`
                option.

        Returns:
            The current table instance for chaining.

        Note:
            Formatting with the `tf_style=` argument:

            We need to supply a preset `tf_style=` value. The following table provides a listing
            of all `tf_style=` values and their output `True` and `False` values.

            |    | TF Style        | Output                              |
            |----|-----------------|-------------------------------------|
            | 1  | `"true-false"`  | `"true"` / `"false"`               |
            | 2  | `"yes-no"`      | `"yes"` / `"no"`                   |
            | 3  | `"up-down"`     | `"up"` / `"down"`                  |
            | 4  | `"check-mark"`  | `#sym.checkmark` / `#sym.crossmark`         |
            | 5  | `"circles"`     | `#sym.circle.filled` / `#sym.circle`|
            | 6  | `"squares"`     | `#sym.square.filled` / `#sym.square`|
            | 7  | `"diamonds"`    | `#sym.diamond.filled` / `#sym.diamond`|
            | 8  | `"arrows"`      | `#sym.arrow.t` / `#sym.arrow.b` |
            | 9  | `"triangles"`   | `#sym.triangle.filled.t` / `#sym.triangle.filled.b`|
            | 10 | `"triangles-lr"`| `#sym.triangle.filled.r` / `#sym.triangle.filled.l`|
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Tf(
                    tf_style=tf_style,
                    pattern=pattern,
                    true_val=true_val,
                    false_val=false_val,
                    na_val=na_val,
                ),
                columns,
                rows,
            )
        )
        return self

    def fmt_bytes(  # noqa: PLR0913
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        standard: ttypes.BytesStyle = "decimal",
        decimals: int = 1,
        n_sigfig: int | None = None,
        drop_trailing_zeros: bool = True,
        drop_trailing_dec_mark: bool = True,
        use_seps: bool = True,
        pattern: str = "{x}",
        sep_mark: str = ",",
        dec_mark: str = ".",
        force_sign: bool = False,
        incl_space: bool = True,
    ) -> t.Self:
        """Format selected numeric values as bytes with human-readable units.

        With numeric values in a table, we can transform those to values of bytes with human
        readable units. The `fmt_bytes()` method allows for the formatting of byte sizes to
        either of two common representations: (1) with decimal units (powers of 1000, examples
        being `"kB"` and `"MB"`), and (2) with binary units (powers of 1024, examples being
        `"KiB"` and `"MiB"). It is assumed the input numeric values represent the number of
        bytes and automatic truncation of values will occur. The numeric values will be scaled
        to be in the range of 1 to <1000 and then decorated with the correct unit symbol
        according to the standard chosen.

        Args:
            columns: Optional column selector limiting where formatting applies.
            rows: Optional row selector limiting where formatting applies.
            standard: The form of expressing large byte sizes is divided between: (1) decimal
                units (powers of 1000; e.g., `"kB"` and `"MB"`), and (2) binary units (powers of
                1024; e.g., `"KiB"` and `"MiB"`). The default is to use decimal units with the
                `"decimal"` option. The alternative is to use binary units with the `"binary"`
                option.
            decimals: This corresponds to the exact number of decimal places to use. A value
                such as `2.34` can, for example, be formatted with `0` decimal places and it
                would result in `"2"`. With `4` decimal places, the formatted value becomes
                `"2.3400"`. The trailing zeros can be removed with `drop_trailing_zeros=True`.
            n_sigfig: Optional number of significant figures.
            drop_trailing_zeros: A boolean value that allows for removal of trailing zeros
                (those redundant zeros after the decimal mark).
            drop_trailing_dec_mark: A boolean value that determines whether decimal marks
                should always appear even if there are no decimal digits to display after
                formatting (e.g., `23` becomes `23.` if `False`). By default trailing decimal
                marks are not shown.
            use_seps: The `use_seps` option allows for the use of digit group separators.
                The type of digit group separator is set by `sep_mark`.
            pattern: A formatting pattern that allows for decoration of the formatted value.
                The formatted value is represented by the `{x}` (which can be used multiple
                times, if needed) and all other characters will be interpreted as string literals.
            sep_mark: The string to use as a separator between groups of digits. For example,
                using `sep_mark=","` with a value of `1000` would result in a formatted value
                of `"1,000"`.
            dec_mark: The string to be used as the decimal mark. For example, using
                `dec_mark=","` with the value `0.152` would result in a formatted value of
                `"0,152"`.
            force_sign: Should the positive sign be shown for positive values (effectively
                showing a sign for all values except zero)? If so, use `True` for this option.
                The default is `False`, where only negative numbers will display a minus sign.
            incl_space: An option for whether to include a space between the value and the
                unit symbol. The default is to include a space character.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.formats.append(
            fmt(
                self._df,
                Bytes(
                    standard=standard,
                    decimals=decimals,
                    n_sigfig=n_sigfig,
                    drop_trailing_zeros=drop_trailing_zeros,
                    drop_trailing_dec_mark=drop_trailing_dec_mark,
                    use_seps=use_seps,
                    pattern=pattern,
                    sep_mark=sep_mark,
                    dec_mark=dec_mark,
                    force_sign=force_sign,
                    incl_space=incl_space,
                ),
                columns,
                rows,
            )
        )
        return self

    # Modifying Columns Methods ----
    def cols_align(
        self, align: ttypes.Alignment = "left", columns: ColumnSelector | None = None
    ) -> t.Self:
        """Set text alignment for selected columns.

        Alignment applies to both column-label cells and body cells for the
        selected columns. It does not affect unselected columns, row-group
        labels, or the table title/subtitle.

        Args:
            align: Target alignment value.
            columns: Optional column selector; defaults to all columns.

        Returns:
            The current table instance for chaining.
        """
        columns_to_align = resolve_columns(self._df, columns)
        self._typ_data.boxhead.set_cols_align(columns_to_align, align)
        return self

    def cols_hide(self, columns: ColumnSelector | None = None) -> t.Self:
        """Hide selected columns from the rendered output.

        Hidden columns are omitted completely, including their column labels and
        body cells. The source data is not modified, so later calls can still
        refer to hidden columns by their original names.

        Args:
            columns: Optional column selector; defaults to all columns.

        Returns:
            The current table instance for chaining.
        """
        columns_to_hide = resolve_columns(self._df, columns)
        self._typ_data.boxhead.set_cols_hidden(columns_to_hide)
        return self

    def cols_label(
        self, cases: dict[str, str | Typst] | None = None, **kwargs: str | Typst
    ) -> t.Self:
        """Set explicit labels for one or more columns.

        Labels replace the displayed column names without changing the source
        data or the selectors used by later calls. This method changes only
        column-label text; it does not format body values.

        Args:
            cases: Optional mapping of column names to new labels.
            **kwargs: Additional column-to-label mappings.

        Returns:
            The current table instance for chaining.
        """
        cases = cases | kwargs if cases else kwargs
        self._typ_data.boxhead.set_cols_label(cases)
        return self

    def cols_label_with(
        self, fn: t.Callable[[str], str | Typst], columns: ColumnSelector | None = None
    ) -> t.Self:
        """Relabel selected columns using a mapping function.

        The function receives each selected source column name and returns the
        label to display. This method changes only the visible column labels;
        source column names and body values are unchanged.

        Args:
            fn: Function receiving current column name and returning new label.
            columns: Optional column selector; defaults to all columns.

        Returns:
            The current table instance for chaining.
        """
        columns_to_relabel = resolve_columns(self._df, columns)
        new_labels = {col: fn(col) for col in columns_to_relabel}
        self._typ_data.boxhead.set_cols_label(new_labels)
        return self

    def cols_move(self, columns: ColumnSelector, after: str) -> t.Self:
        """Move one or more columns after another column.

        The selected columns are removed from their current positions and
        inserted immediately after `after`. When multiple columns are selected,
        their relative order is preserved. Column selectors are resolved against
        the user-visible table columns, so integer selectors do not count the
        internal row index column.

        Args:
            columns: Column selector identifying the columns to move.
            after: Name of the column that the selected columns should follow.

        Raises:
            ValueError: If `after` is one of the columns being moved.
            ColumnNotFoundError: If `columns` or `after` reference unknown columns.

        Returns:
            The current table instance for chaining.
        """
        all_columns = [col.var for col in self._typ_data.boxhead]
        column_data = self._df.select(all_columns)

        columns_to_move = resolve_columns(column_data, columns)
        column_after = resolve_columns(column_data, after)[0]

        if column_after in columns_to_move:
            msg = (
                f"Cannot move columns {columns_to_move!r} after {column_after!r} because "
                f"{column_after!r} is one of the columns being moved. Choose an `after` "
                "column that is not included in `columns`."
            )
            raise ValueError(msg)

        other_columns = [col for col in all_columns if col not in columns_to_move]

        indx = other_columns.index(column_after)

        final_vars = [
            *other_columns[: indx + 1],
            *columns_to_move,
            *other_columns[indx + 1 :],
        ]

        self._typ_data.boxhead = self._typ_data.boxhead.reorder(final_vars)

        return self

    # Table option methods ----
    def set_table_inset(
        self, inset: str | Sides[ttypes.Relative] | dict[str, ttypes.Relative]
    ) -> t.Self:
        """Set default padding for every table cell.

        This controls table-level cell inset. Region-specific `CellStyle`
        rules can still override inset for targeted cells.

        Args:
            inset: Typst inset value, per-side `Sides`, or dictionary accepted
                by `Sides`.

        Returns:
            The current table instance for chaining.
        """
        if isinstance(inset, dict):
            inset = Sides(**inset)
        self._typ_data.inset = inset
        return self

    def set_table_stroke(self, stroke: str) -> t.Self:
        """Set the table-level stroke.

        This controls the default stroke passed to Typst's `table` function.
        Region-specific cell styles can still override strokes for targeted
        cells.

        Args:
            stroke: Raw Typst stroke expression.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.stroke = stroke
        return self

    def set_gutter(
        self,
        gutter: ttypes.Gutter | None = None,
        row_gutter: ttypes.Gutter | None = None,
        column_gutter: ttypes.Gutter | None = None,
    ) -> t.Self:
        """Set spacing between rows and columns.

        `gutter` sets Typst's general table gutter. `row_gutter` and
        `column_gutter` override spacing in one direction.

        Args:
            gutter: Default row and column gutter.
            row_gutter: Row-only gutter override.
            column_gutter: Column-only gutter override.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.gutters.gutter = GutterContainer(gutter)
        self._typ_data.gutters.row_gutter = GutterContainer(row_gutter)
        self._typ_data.gutters.column_gutter = GutterContainer(column_gutter)

        return self

    def clear_defaults(self) -> t.Self:
        """Clear all typ-tables default styling.

        This removes typ-tables' opinionated default styles and resets the
        table-level stroke to Typst's default-style baseline.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.default_styles.clear()
        self._typ_data.stroke = "1pt + black"
        return self

    def with_id(self, id: str | None = None) -> t.Self:  # noqa: A002
        """Set the id for this table.

        Args:
            id: The label to add to the table figure. By default it will be left blank.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.figure = replace(self._typ_data.figure, _id=id)
        return self

    def tab_options(self, *, column_labels_hidden: bool = False) -> t.Self:
        """Modify the table output options.

        Args:
            column_labels_hidden: An option to hide the column labels.
        """
        options = locals()
        del options["self"]
        self._typ_data.tab_options = replace(self._typ_data.tab_options, **options)
        return self


__all__ = [
    "ColumnSelector",
    "RowSelector",
    "TypTable",
    "Typst",
]
