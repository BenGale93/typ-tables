"""Package for creating Typst Tables from DataFrames."""

import typing as t

import narwhals as nw
from narwhals.typing import IntoDataFrame

from typ_tables import locators, ttypes
from typ_tables._constants import ROW_INDEX
from typ_tables._escape import Typst
from typ_tables._formats import FString, Numeric, SubMissing, fmt
from typ_tables._gutter import GutterContainer
from typ_tables._location import ColumnSelector, RowSelector, resolve_columns
from typ_tables._typ_data import TABLE_TEMPLATE, Figure, Heading, TypData
from typ_tables.style import CellStyle, Sides, TextStyle


def _create_table_string(original_data: ttypes.Data, typ: TypData) -> str:
    """Render a complete Typst table string from data and table state.

    Args:
        original_data: Source data with internal row index column.
        typ: Table state containing formatting, labels, and style rules.

    Returns:
        A complete Typst table string, optionally wrapped in `#figure`.
    """
    data = typ.format_df(original_data).drop(ROW_INDEX)
    typ.stub.update_group_row_labels(data, typ.boxhead)

    columns = typ.columns()
    alignment = typ.alignment()
    header = typ.header(data)
    body = typ.body(data, original_data)

    table_str = TABLE_TEMPLATE.substitute(
        columns=columns,
        alignment=alignment,
        header=header,
        body=body,
        inset=typ.inset,
        stroke=typ.stroke,
        row_gutter=typ.gutters.row,
        column_gutter=typ.gutters.column,
    )
    return typ.figure.add_figure_args(table_str)


class TypTable:
    """User-facing builder for converting DataFrames into Typst tables."""

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

    # Modifying parts of a Table Methods ----
    def tab_header(self, title: str | Typst, subtitle: str | Typst | None = None) -> t.Self:
        """Set table title and optional subtitle.

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

        Args:
            caption: Caption text or raw Typst. `None` disables wrapping.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.figure = Figure(caption)
        return self

    def tab_stubhead(self, label: str | Typst) -> t.Self:
        """Set the label shown in the stub header cell.

        Args:
            label: Stub header label text or raw Typst.

        Returns:
            The current table instance for chaining.
        """
        self._typ_data.stubhead = label
        return self

    def tab_style(
        self, locator: locators.Loc, text: TextStyle | None = None, cell: CellStyle | None = None
    ) -> t.Self:
        """Add style rules for a specific table region.

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

    # Modifying Columns Methods ----
    def cols_align(
        self, align: ttypes.Alignment = "left", columns: ColumnSelector | None = None
    ) -> t.Self:
        """Set text alignment for selected columns.

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

    # Table option methods ----
    def set_table_inset(
        self, inset: str | Sides[ttypes.Relative] | dict[str, ttypes.Relative]
    ) -> t.Self:
        """How much to pad the cells' content for all cells in the table."""
        if isinstance(inset, dict):
            inset = Sides(**inset)
        self._typ_data.inset = inset
        return self

    def set_table_stroke(self, stroke: str) -> t.Self:
        """Set the table level stroke.

        Note:
            Can be a function, the raw string is used within the template.
        """
        self._typ_data.stroke = stroke
        return self

    def set_gutter(
        self,
        gutter: ttypes.Gutter | None = None,
        row_gutter: ttypes.Gutter | None = None,
        column_gutter: ttypes.Gutter | None = None,
    ) -> t.Self:
        """Set the table level gutter parameters."""
        self._typ_data.gutters.gutter = GutterContainer(gutter)
        self._typ_data.gutters.row_gutter = GutterContainer(row_gutter)
        self._typ_data.gutters.column_gutter = GutterContainer(column_gutter)

        return self

    def clear_defaults(self) -> t.Self:
        """Clears all the typ-table default styling."""
        self._typ_data.default_styles.clear()
        self._typ_data.stroke = "1pt + black"
        return self


__all__ = [
    "ColumnSelector",
    "RowSelector",
    "TypTable",
    "Typst",
]
