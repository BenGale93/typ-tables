"""Module for managing the table state."""

import typing as t
import warnings
from dataclasses import dataclass, field
from functools import cached_property

from narwhals.typing import IntoDataFrame, IntoDataFrameT

from typ_tables import _locators, ttypes
from typ_tables._boxhead import Boxhead, ColInfo
from typ_tables._escape import Typst, escape_value
from typ_tables._formats import Formatter
from typ_tables._gutter import Gutters
from typ_tables._rendering import Cell, Content, Figure, Header, Renderable
from typ_tables._spanners import Spanners
from typ_tables._stub import Stub
from typ_tables._style import DefaultStyles, Sides, StyleHolder


@dataclass(frozen=True)
class Heading:
    """Table heading metadata used to build the top header row.

    Attributes:
        _title: Optional heading title text or raw Typst.
        _subtitle: Optional heading subtitle text or raw Typst.
    """

    _title: str | Typst | None = None
    _subtitle: str | Typst | None = None

    @cached_property
    def title(self) -> str | Typst | None:
        """Return title text escaped for use in renderable content."""
        if self._title is None:
            return self._title
        return escape_value(self._title)

    @cached_property
    def subtitle(self) -> str | Typst | None:
        """Return subtitle text escaped for use in renderable content."""
        if self._subtitle is None:
            return self._subtitle
        return escape_value(self._subtitle)

    def to_typst(self, n_col: int, styles: StyleHolder) -> Header | None:
        """Build a renderable heading header.

        Args:
            n_col: Number of table columns to span.
            styles: Additional styles applied to the heading cell.

        Returns:
            A `Header`, or `None` when no title is set.
        """
        if not self.title:
            return None
        if not self.subtitle:
            title_contents = self.title
        else:
            title_contents = Typst(f"== {self.title} \\\n  {self.subtitle}")

        return Header(
            [Cell(Content(title_contents, styles.text), colspan=n_col, cell_style=styles.cell)]
        )


@dataclass(frozen=True)
class FigureArgs:
    """Figure metadata used to wrap the renderable table in `#figure`.

    Attributes:
        _caption: Optional figure caption text or raw Typst.
    """

    _caption: str | Typst | None = None

    @cached_property
    def caption(self) -> str | Typst | None:
        """Return caption text escaped for the renderable figure wrapper."""
        if self._caption is None:
            return self._caption
        return escape_value(self._caption)

    def to_typst(self, body: Renderable) -> Figure:
        """Build a renderable figure around an already-built table body."""
        return Figure(body, caption=self.caption)


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
    figure: FigureArgs
    spanners: Spanners = field(default_factory=Spanners)
    styles: list[_locators.StyledLoc] = field(default_factory=list)
    stubhead: str | Typst = ""
    inset: str | Sides[ttypes.Relative] | None = None
    stroke: str | None = "none"
    gutters: Gutters = field(default_factory=Gutters)

    @classmethod
    def from_data(
        cls, df: ttypes.Data[IntoDataFrame], rowname_col: str | None, groupname_col: str | None
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
            figure=FigureArgs(),
        )

    def format_df(self, df: ttypes.Data[IntoDataFrameT]) -> ttypes.Data[IntoDataFrameT]:
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

    def header(self, original_data: ttypes.Data[IntoDataFrame]) -> list[Header]:
        """Build renderable table header rows.

        Args:
            original_data: Unformatted data.

        Returns:
            Header rows containing optional heading, spanners, and column labels.
        """
        columns = self.boxhead.get_stub_and_default_columns()

        headers: list[Header] = []
        if title_header := self._get_heading(len(columns)):
            headers.append(title_header)
        if spanners := self._get_spanner_headers(columns):
            headers.extend(spanners)
        headers.append(self._get_column_label_header(original_data, columns))

        return headers

    def _get_column_label_header(
        self,
        original_data: ttypes.Data[IntoDataFrame],
        columns: list[ColInfo],
    ) -> Header:
        """Build the header row containing the stub head and column labels."""
        column_label_styles = self._build_column_label_styles(original_data)
        stub_head_style = self._build_stub_head_style()

        return Header(
            [
                self._get_column_label_cell(col, column_label_styles, stub_head_style)
                for col in columns
            ]
        )

    def _build_column_label_styles(
        self, original_data: ttypes.Data[IntoDataFrame]
    ) -> dict[str, StyleHolder]:
        """Collect merged styles for each styled column-label cell."""
        column_label_styles: dict[str, StyleHolder] = {}
        for style_info in self.styles:
            if not isinstance(style_info, _locators.StyledLocColumnLabels):
                continue

            columns_to_style = style_info.resolve(original_data)
            for column_to_style in columns_to_style:
                current_style = column_label_styles.get(
                    column_to_style, self.default_styles.header_cells
                )
                column_label_styles[column_to_style] = current_style | style_info.style

        return column_label_styles

    def _build_stub_head_style(self) -> StyleHolder:
        """Collect the merged style for the stub-head cell."""
        stub_head_style = self.default_styles.stub_header_cell
        for style_info in self.styles:
            if isinstance(style_info, _locators.StyledLocStubhead):
                stub_head_style = stub_head_style | style_info.style

        return stub_head_style

    def _get_column_label_cell(
        self,
        col: ColInfo,
        column_label_styles: dict[str, StyleHolder],
        stub_head_style: StyleHolder,
    ) -> Cell:
        """Build one cell in the column-label header row."""
        if col.col_type == "stub":
            return Cell(
                Content(self.stubhead, text_style=stub_head_style.text),
                cell_style=stub_head_style.cell,
            )

        header_cell_style = column_label_styles.get(col.var, self.default_styles.header_cells)
        return Cell(
            Content(col.name, text_style=header_cell_style.text), cell_style=header_cell_style.cell
        )

    def _get_heading(self, n_col: int) -> Header | None:
        """Build the optional title/subtitle row above the column labels."""
        header_style = self.default_styles.header
        for style_info in self.styles:
            if isinstance(style_info, _locators.StyledLocHeader):
                header_style = header_style | style_info.style

        return self.heading.to_typst(n_col, header_style)

    def _get_spanner_headers(self, columns: list[ColInfo]) -> list[Header]:
        """Build all configured spanner rows above the column labels."""
        spanners = list(reversed(self.spanners.build_spanners([col.var for col in columns])))
        if not spanners:
            return []

        spanner_styles = self._build_spanner_styles()
        return [
            Header(
                [
                    span_cell.to_typst(
                        spanner_styles.get(span_cell.id_, self.default_styles.spanner_cells)
                    )
                    for span_cell in row
                ]
            )
            for row in spanners
        ]

    def _build_spanner_styles(self) -> dict[str | None, StyleHolder]:
        """Collect merged styles keyed by spanner id."""
        spanner_styles: dict[str | None, StyleHolder] = dict.fromkeys(
            self.spanners.get_ids(), self.default_styles.spanner_cells
        )
        for style_info in self.styles:
            if isinstance(style_info, _locators.StyledLocSpanner):
                if style_info.spanner_ids is None:
                    for id_, style in spanner_styles.items():
                        spanner_styles[id_] = style | style_info.style
                else:
                    for spanner_id in style_info.spanner_ids:
                        current_spanner_style = spanner_styles.get(
                            spanner_id, self.default_styles.spanner_cells
                        )
                        spanner_styles[spanner_id] = current_spanner_style | style_info.style

        return spanner_styles

    def body(
        self, data: ttypes.Data[IntoDataFrame], original_data: ttypes.Data[IntoDataFrame]
    ) -> list[list[Cell]]:
        """Build renderable rows for the table body.

        Args:
            data: Formatted data with table row index intact.
            original_data: Unformatted data.

        Returns:
            Rows of renderable table cells.
        """
        columns = self.boxhead.get_stub_and_default_columns()
        n_cols = len(columns)
        cell_styles = self._build_cell_style_index(original_data, columns)
        row_group_styles = self._build_row_group_styles(original_data)

        body_cells = []
        prev_group_info = None
        ordered_index = self.stub.group_indices_map()
        for i, group_info in ordered_index:
            if group_info is not None and group_info is not prev_group_info:
                body_cells.append(self._get_group_row(group_info, n_cols, row_group_styles))
                prev_group_info = group_info

            body_cells.append(self._get_data_row(data, i, columns, cell_styles))

        return body_cells

    def _build_cell_style_index(
        self, data: ttypes.Data[IntoDataFrame], columns: list[ColInfo]
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

    def _build_row_group_styles(
        self, original_data: ttypes.Data[IntoDataFrame]
    ) -> _locators.RowGroupStyles:
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

    def _get_group_row(
        self,
        group_info: t.Any,
        n_cols: int,
        row_group_styles: _locators.RowGroupStyles,
    ) -> list[Cell]:
        """Build a row-group heading row."""
        group_cell_style = row_group_styles.get_style(
            group_info.group_id, self.default_styles.row_group
        )
        return [
            Cell(
                Content(group_info.name, text_style=group_cell_style.text),
                colspan=n_cols,
                cell_style=group_cell_style.cell,
            )
        ]

    def _get_data_row(
        self,
        data: ttypes.Data[IntoDataFrame],
        row_idx: int,
        columns: list[ColInfo],
        cell_styles: dict[_locators.CellPos, StyleHolder],
    ) -> list[Cell]:
        """Build a single data row."""
        body_cells = []
        for col in columns:
            if col.col_type == "stub":
                default_style = self.default_styles.stub_cell
            else:
                default_style = self.default_styles.body_cell
            body_cell_style = default_style | cell_styles.get(
                _locators.CellPos(row=row_idx, column=col.var)
            )
            cell_content = data[row_idx][col.var].item()
            body_cells.append(
                Cell(
                    Content(cell_content, text_style=body_cell_style.text),
                    cell_style=body_cell_style.cell,
                )
            )

        return body_cells
