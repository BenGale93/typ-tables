"""Package for creating Typst Tables from DataFrames."""

import typing as t
import warnings
from dataclasses import dataclass, field
from functools import cached_property
from string import Template
from textwrap import indent

import narwhals as nw
from narwhals.typing import IntoDataFrame

from typ_tables import locators, ttypes, utils
from typ_tables.boxhead import Boxhead
from typ_tables.constants import ROW_INDEX
from typ_tables.escape import Typst, escape_value
from typ_tables.formats import Formatter, FString, Numeric, SubMissing, fmt
from typ_tables.location import ColumnSelector, RowSelector, resolve_columns
from typ_tables.stub import Stub
from typ_tables.style import CellStyle, CellStyleForCell, StyleHolder, TextStyle

HEADER_STROKE = "1.2pt"

TITLE_TEMPLATE = Template(
    f"""table.hline(stroke: {HEADER_STROKE}),
  table.header(
$cell_block
  ),
  table.hline(stroke: {HEADER_STROKE}),
  """
)


@dataclass(frozen=True)
class Heading:
    """Table heading metadata rendered above the main header row.

    Attributes:
        _title: Optional heading title text or raw Typst.
        _subtitle: Optional heading subtitle text or raw Typst.
    """

    DEFAULT_STYLE = StyleHolder(cell=CellStyleForCell(align="center"))

    _title: str | Typst | None = None
    _subtitle: str | Typst | None = None

    @cached_property
    def title(self) -> str | Typst | None:
        """Return the escaped title text."""
        if self._title is None:
            return self._title
        return escape_value(self._title)

    @cached_property
    def subtitle(self) -> str | Typst | None:
        """Return the escaped subtitle text."""
        if self._subtitle is None:
            return self._subtitle
        return escape_value(self._subtitle)

    def to_typst(self, n_col: int, styles: StyleHolder) -> str:
        """Render heading content as Typst header rows.

        Args:
            n_col: Number of table columns to span.
            styles: Additional styles applied to the heading cell.

        Returns:
            A Typst string for the heading block, or an empty string when no
            title is set.
        """
        if not self.title:
            return ""
        if not self.subtitle:
            title_contents = self.title
        else:
            title_contents = Typst(
                f"== {escape_value(self.title)} \\\n  {escape_value(self.subtitle)}"
            )

        cell_block = (self.DEFAULT_STYLE | styles).to_typst(title_contents, n_col)
        cell_block = indent(cell_block, " " * 4)

        return TITLE_TEMPLATE.substitute(title_contents=title_contents, cell_block=cell_block)


@dataclass(frozen=True)
class Figure:
    """Figure metadata used to optionally wrap the table in `#figure`.

    Attributes:
        _caption: Optional figure caption text or raw Typst.
    """

    _caption: str | Typst | None = None

    @cached_property
    def caption(self) -> str | Typst | None:
        """Return the escaped figure caption text."""
        if self._caption is None:
            return self._caption
        return escape_value(self._caption)

    def add_figure_args(self, table_str: str) -> str:
        """Wrap a Typst table in a figure block when a caption is set.

        Args:
            table_str: Typst table string beginning with `#table`.

        Returns:
            The original table string when no caption is present, otherwise a
            `#figure(...)` wrapper containing the table and caption.
        """
        if caption := self.caption:
            table_str = table_str.removeprefix("#")
            table_str = indent(table_str, "  ").rstrip()
            table_str = f"#figure(\n{table_str},\n  caption: [{caption}],\n)"

        return table_str


@dataclass(kw_only=True)
class TypData:
    """Internal container with table structure, formatting, and styling state.

    Attributes:
        boxhead: Column definitions and presentation metadata.
        stub: Row stub and grouping metadata.
        formats: Ordered value formatters.
        substitute: Ordered substitution formatters.
        heading: Heading metadata.
        figure: Figure metadata.
        styles: Style rules keyed by locators.
        stubhead: Optional label for the stub header cell.
    """

    boxhead: Boxhead
    stub: Stub
    formats: list[Formatter]
    substitute: list[Formatter]
    heading: Heading
    figure: Figure
    styles: list[locators.StyledLoc] = field(default_factory=list)
    stubhead: str | Typst | None = None

    @classmethod
    def from_data(
        cls, df: ttypes.Data, rowname_col: str | None, groupname_col: str | None
    ) -> t.Self:
        """Build `TypData` initialized from a source dataset.

        Args:
            df: Source DataFrame with row index column already attached.
            rowname_col: Optional column used as the stub row label.
            groupname_col: Optional column used for row grouping.

        Returns:
            A `TypData` instance with default formatting, figure, and styles.
        """
        stub = Stub.from_data(df, rowname_col=rowname_col, groupname_col=groupname_col)
        boxhead = Boxhead.from_data(df, rowname_col, groupname_col)
        return cls(
            boxhead=boxhead,
            stub=stub,
            formats=[],
            substitute=[],
            heading=Heading(),
            figure=Figure(),
        )

    def format_df(self, df: ttypes.Data) -> ttypes.Data:
        """Apply all registered formatters to a dataset in order.

        Args:
            df: DataFrame to format.

        Returns:
            The formatted DataFrame.
        """
        new_df = df
        for f in self.formats:
            new_df = f.fmt(new_df)
        for f in self.substitute:
            new_df = f.fmt(new_df)
        return new_df

    def alignment(self) -> str:
        """Return Typst alignment tuple for visible table columns.

        Returns:
            A Typst tuple expression like `"(left, right, right)"`.
        """
        alignment_elements = [
            col.column_align for col in self.boxhead.get_stub_and_default_columns()
        ]
        joined_alignments = ", ".join(alignment_elements)
        return f"({joined_alignments})"

    def columns(self) -> str:
        """Return the number of visible table columns as a string.

        Returns:
            Column count represented as a string for Typst templates.
        """
        return str(len(self.boxhead))

    def header(self) -> str:
        """Render table header rows, including optional title and stub divider.

        Returns:
            Typst header block containing heading rows, column labels, and
            header rules.
        """
        columns = self.boxhead.get_stub_and_default_columns()
        headers = []
        for col in columns:
            if col.col_type == "stub":
                header_cell = f"[{self.stubhead}]" if self.stubhead else "[]"
            else:
                header_cell = f"[{col.name}]"
            headers.append(header_cell)

        header = ", ".join(headers)

        n_col = len(columns)

        header_style = StyleHolder()
        for style_info in self.styles:
            if isinstance(style_info, locators.StyledLocHeader):
                header_style = header_style | style_info.style

        formatted_title = self.heading.to_typst(n_col, header_style)

        if columns[0].col_type == "stub":
            start_num = 2 if formatted_title else 1
            vline = f"table.vline(x: 1, start: {start_num}),\n"
        else:
            vline = ""

        return (
            f"{formatted_title}{vline}table.header({header}),\n"
            f"  table.hline(stroke: {HEADER_STROKE})"
        )

    def body(self, data: ttypes.Data, original_data: ttypes.Data) -> str:
        """Render Typst rows for table body data.

        Args:
            data: Formatted data with table row index intact.
            original_data: Unformatted data.

        Returns:
            Typst string containing data rows and horizontal rules, including
            optional group heading rows.
        """
        columns = self.boxhead.get_stub_and_default_columns()
        n_cols = len(columns)
        rows = []

        body_styles = []
        stub_styles = []
        row_group_styles = locators.RowGroupStyles()
        for style_info in self.styles:
            if isinstance(style_info, locators.StyledLocBody):
                cell_pos = style_info.resolve(data)
                body_styles.append(utils.StylePosition(style=style_info.style, positions=cell_pos))

            if isinstance(style_info, locators.StyledLocStub):
                cell_pos = style_info.resolve(data, columns[0].var)
                stub_styles.append(utils.StylePosition(style=style_info.style, positions=cell_pos))

            if isinstance(style_info, locators.StyledLocRowGroup):
                row_group_col = self.boxhead.get_group_column_name()
                if row_group_col is None:
                    warnings.warn(
                        "Row-group style locator was used but no row-group was set.", stacklevel=2
                    )
                    continue
                group_values = style_info.resolve(original_data, row_group_col)
                row_group_styles.append(group_values, style_info.style)

        prev_group_info = None
        ordered_index = self.stub.group_indices_map()
        for i, group_info in ordered_index:
            if group_info is not None and group_info is not prev_group_info:
                group_cell_style = row_group_styles.get_style(group_info.group_id)
                cell_str = group_cell_style.to_typst(group_info.name, colspan=n_cols)
                group_row = f"table.hline(stroke: 1pt),\n {cell_str}\n table.hline(stroke : 1pt),\n"
                rows.append(group_row)
                prev_group_info = group_info

            body_cells = []
            for col in columns:
                if col.col_type == "stub":
                    cell_style = utils.find_styles(col.var, i, stub_styles)
                else:
                    cell_style = utils.find_styles(col.var, i, body_styles)
                cell_content = data[i][col.var].item()
                cell_str = cell_style.to_typst(cell_content, 1)
                body_cells.append(cell_str)

            row = " ".join(body_cells)
            rows.extend((row, "table.hline(stroke: 0.6pt),"))

        return "\n  ".join(rows)


TABLE_TEMPLATE = Template("""#table(
  columns: $columns,
  stroke: none,
  align: $alignment,
  $header,
  $body
)
""")


def create_table_string(original_data: ttypes.Data, typ: TypData) -> str:
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
    header = typ.header()
    body = typ.body(data, original_data)

    table_str = TABLE_TEMPLATE.substitute(
        columns=columns,
        alignment=alignment,
        header=header,
        body=body,
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
        return create_table_string(self._df, self._typ_data)

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
