"""Module for managing the table state."""

import typing as t
import warnings
from dataclasses import dataclass, field
from functools import cached_property
from string import Template
from textwrap import indent

from typ_tables import _locators, ttypes
from typ_tables._boxhead import Boxhead, ColInfo
from typ_tables._escape import Typst, escape_value
from typ_tables._formats import Formatter
from typ_tables._gutter import Gutters
from typ_tables._stub import Stub
from typ_tables._style import DefaultStyles, Sides, StyleHolder

TITLE_TEMPLATE = Template(
    """
  table.header(
$cell_block
  ),
  """
)


@dataclass(frozen=True)
class Heading:
    """Table heading metadata rendered above the main header row.

    Attributes:
        _title: Optional heading title text or raw Typst.
        _subtitle: Optional heading subtitle text or raw Typst.
    """

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

        cell_block = styles.to_typst(title_contents, n_col)
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

    default_styles: DefaultStyles = field(default_factory=DefaultStyles)
    boxhead: Boxhead
    stub: Stub
    formats: list[Formatter]
    substitute: list[Formatter]
    heading: Heading
    figure: Figure
    styles: list[_locators.StyledLoc] = field(default_factory=list)
    stubhead: str | Typst | None = None
    inset: str | Sides = "0% + 5pt"
    stroke: str = "none"
    gutters: Gutters = field(default_factory=Gutters)

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

    def header(self, original_data: ttypes.Data) -> str:
        """Render table header rows, including optional title and stub divider.

        Args:
            original_data: Unformatted data.

        Returns:
            Typst header block containing heading rows, column labels, and
            header rules.
        """
        columns = self.boxhead.get_stub_and_default_columns()

        column_label_stylers: dict[str, StyleHolder] = {}
        stub_head_style = self.default_styles.stub_header_cell
        for style_info in self.styles:
            if isinstance(style_info, _locators.StyledLocColumnLabels):
                columns_to_style = style_info.resolve(original_data)
                for column_to_style in columns_to_style:
                    current_style = column_label_stylers.get(
                        column_to_style, self.default_styles.header_cells
                    )
                    column_label_stylers[column_to_style] = current_style | style_info.style
            elif isinstance(style_info, _locators.StyledLocStubhead):
                stub_head_style = stub_head_style | style_info.style

        headers = []
        for col in columns:
            if col.col_type == "stub":
                header_cell = stub_head_style.to_typst(self.stubhead or "")
            else:
                header_cell_style = column_label_stylers.get(
                    col.var, self.default_styles.header_cells
                )
                header_cell = header_cell_style.to_typst(col.name)
            headers.append(header_cell)

        header = " ".join(headers)

        n_col = len(columns)

        header_style = self.default_styles.header
        for style_info in self.styles:
            if isinstance(style_info, _locators.StyledLocHeader):
                header_style = header_style | style_info.style

        formatted_title = self.heading.to_typst(n_col, header_style)

        return f"{formatted_title}table.header({header})"

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
        cell_styles = self._build_cell_style_index(data, columns)
        row_group_styles = self._build_row_group_styles(original_data)

        prev_group_info = None
        ordered_index = self.stub.group_indices_map()
        for i, group_info in ordered_index:
            if group_info is not None and group_info is not prev_group_info:
                rows.append(self._render_group_row(group_info, n_cols, row_group_styles))
                prev_group_info = group_info

            rows.append(self._render_data_row(data, i, columns, cell_styles))

        return "\n  ".join(rows)

    def _build_cell_style_index(
        self, data: ttypes.Data, columns: list[ColInfo]
    ) -> dict[_locators.CellPos, StyleHolder]:
        """Precompute merged styles for each addressable body cell."""
        styles: dict[_locators.CellPos, StyleHolder] = {}
        stub_column = next((c.var for c in columns if c.col_type == "stub"), None)

        for style_info in self.styles:
            if isinstance(style_info, _locators.StyledLocBody):
                for pos in style_info.resolve(data):
                    if pos.column == stub_column:
                        continue
                    current_style = styles.get(pos, StyleHolder())
                    styles[pos] = current_style | style_info.style[pos.row]

            if isinstance(style_info, _locators.StyledLocStub) and stub_column is not None:
                for pos in style_info.resolve(data, stub_column):
                    current_style = styles.get(pos, StyleHolder())
                    styles[pos] = current_style | style_info.style[pos.row]

        return styles

    def _build_row_group_styles(self, original_data: ttypes.Data) -> _locators.RowGroupStyles:
        """Collect row-group style assignments resolved against source data."""
        row_group_styles = _locators.RowGroupStyles()
        row_group_col = self.boxhead.get_group_column_name()

        for style_info in self.styles:
            if not isinstance(style_info, _locators.StyledLocRowGroup):
                continue
            if row_group_col is None:
                warnings.warn(
                    "Row-group style locator was used but no row-group was set.", stacklevel=2
                )
                continue

            group_values = style_info.resolve(original_data, row_group_col)
            row_group_styles.append(group_values, style_info.style)

        return row_group_styles

    def _render_group_row(
        self,
        group_info: t.Any,
        n_cols: int,
        row_group_styles: _locators.RowGroupStyles,
    ) -> str:
        """Render a row-group heading with top and bottom separator lines."""
        group_cell_style = row_group_styles.get_style(
            group_info.group_id, self.default_styles.row_group
        )
        return group_cell_style.to_typst(group_info.name, colspan=n_cols)

    def _render_data_row(
        self,
        data: ttypes.Data,
        row_idx: int,
        columns: list[ColInfo],
        cell_styles: dict[_locators.CellPos, StyleHolder],
    ) -> str:
        """Render a single data row using precomputed per-cell styles."""
        body_cells = []
        for col in columns:
            if col.col_type == "stub":
                default_style = self.default_styles.stub_cell
            else:
                default_style = self.default_styles.body_cell
            cell_style = default_style | cell_styles.get(
                _locators.CellPos(row=row_idx, column=col.var)
            )
            cell_content = data[row_idx][col.var].item()
            body_cells.append(cell_style.to_typst(cell_content, 1))

        return " ".join(body_cells)


TABLE_TEMPLATE = Template("""#table(
  columns: $columns,
  column-gutter: $column_gutter,
  row-gutter: $row_gutter,
  stroke: $stroke,
  align: $alignment,
  inset: $inset,
  $header,
  $body
)
""")
