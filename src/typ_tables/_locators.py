"""Module defining styling locators."""

import typing as t
from copy import deepcopy
from dataclasses import dataclass, field

import narwhals as nw
from narwhals.typing import IntoDataFrame

from typ_tables._location import ColumnSelector, RowSelector, resolve_columns, resolve_rows
from typ_tables._style import CellStyle, CellStyleForCell, StyleHolder, TextStyle, TextStyleForCell
from typ_tables.ttypes import Data


@dataclass
class StyledLoc:
    """Base marker for table style locator targets, that have been styled."""


class Loc(t.Protocol):
    """Protocol implemented by all public table style locators.

    Pass a locator to `TypTable.tab_style` to choose which table region receives
    the supplied text and cell styles. Concrete locator classes select regions
    such as the header, body cells, row stub, or row-group labels.
    """

    def _apply_style(
        self,
        data: Data[IntoDataFrame],
        text: TextStyle | None = None,
        cell: CellStyle | None = None,
    ) -> StyledLoc:
        """Apply text/cell styles and return a styled locator.

        Args:
            data: Source data used for resolving selector-driven styles.
            text: Optional text style selector for the target location.
            cell: Optional cell style selector for the target location.

        Returns:
            Styled locator instance for the specific location type.
        """


@dataclass
class StyledLocHeader(StyledLoc):
    """Styled Marker locator selecting the table header region."""

    style: StyleHolder


@dataclass
class LocHeader:
    """Select the table header title and subtitle region.

    This locator targets the heading created by `TypTable.tab_header`, not the
    column-label row. Use `LocColumnLabels` to style column names.
    """

    def _apply_style(
        self,
        data: Data[IntoDataFrame],  # noqa: ARG002
        text: TextStyle | None = None,
        cell: CellStyle | None = None,
    ) -> StyledLocHeader:
        """Build a styled header locator.

        Args:
            data: Source data used for style resolution.
            text: Optional text style selector for header cells.
            cell: Optional cell style selector for header cells.

        Returns:
            Styled header locator with resolved style values.
        """
        text_style_for_cell = text.get_single() if text is not None else TextStyleForCell()
        cell_style_for_cell = cell.get_single() if cell is not None else CellStyleForCell()

        return StyledLocHeader(
            style=StyleHolder(text=text_style_for_cell, cell=cell_style_for_cell)
        )


@dataclass(kw_only=True, frozen=True)
class CellPos:
    """Class representing a cell in a DataFrame."""

    column: str
    row: int


@dataclass
class StyledLocBody(StyledLoc):
    """Styled marker locator selecting the table body region."""

    style: list[StyleHolder]
    columns: ColumnSelector | None = None
    rows: RowSelector | None = None

    def resolve(self, data: Data[IntoDataFrame]) -> list[CellPos]:
        """Resolve which cells in data to apply the style to."""
        columns = resolve_columns(data, self.columns)
        rows = resolve_rows(data, self.rows)

        return [CellPos(column=c, row=r) for r in rows for c in columns]


@dataclass
class LocBody:
    """Select table body cells.

    By default, all body cells are selected. Use `rows`, `columns`, or both to
    limit the style rule to a subset of the body.
    """

    columns: ColumnSelector | None = None
    """Columns to select in the body.

    Accepts any [`ColumnSelector`][typ_tables.ColumnSelector]. `None` selects
    all body columns.
    """
    rows: RowSelector | None = None
    """Rows to select in the body.

    Accepts any [`RowSelector`][typ_tables.RowSelector]. `None` selects all
    body rows.
    """

    def _apply_style(
        self,
        data: Data[IntoDataFrame],
        text: TextStyle | None = None,
        cell: CellStyle | None = None,
    ) -> StyledLocBody:
        """Build a styled body locator.

        Args:
            data: Source data used for row-level style resolution.
            text: Optional text style selector for body rows.
            cell: Optional cell style selector for body rows.

        Returns:
            Styled body locator with per-row style holders.
        """
        n_rows = len(data)
        text_styles_for_cells = (
            text.resolve(data) if text is not None else [TextStyleForCell()] * n_rows
        )
        cell_styles_for_cells = (
            cell.resolve(data) if cell is not None else [CellStyleForCell()] * n_rows
        )
        style_holders = []
        for text_style, cell_style in zip(
            text_styles_for_cells, cell_styles_for_cells, strict=True
        ):
            style_holders.append(StyleHolder(text=text_style, cell=cell_style))

        return StyledLocBody(style=style_holders, columns=self.columns, rows=self.rows)


@dataclass
class StyledLocColumnLabels(StyledLoc):
    """Styled marker locator selecting the table column labels."""

    style: StyleHolder
    columns: ColumnSelector | None = None

    def resolve(self, data: Data[IntoDataFrame]) -> list[str]:
        """Resolve which columns in data to apply the style to."""
        return resolve_columns(data, self.columns)


@dataclass
class LocColumnLabels:
    """Select column-label cells.

    Column-label cells are the header cells that display data column names above
    the body. Use `columns` to style labels for only some data columns.
    """

    columns: ColumnSelector | None = None
    """Columns whose labels should be selected.

    Accepts any [`ColumnSelector`][typ_tables.ColumnSelector]. `None` selects
    all column labels.
    """

    def _apply_style(
        self,
        data: Data[IntoDataFrame],  # noqa: ARG002
        text: TextStyle | None = None,
        cell: CellStyle | None = None,
    ) -> StyledLocColumnLabels:
        """Build a styled column label locator.

        Args:
            data: Source data used for row-level style resolution.
            text: Optional text style selector for body rows.
            cell: Optional cell style selector for body rows.

        Returns:
            Styled column labels locator with per-row style holders.
        """
        text_style_for_cell = text.get_single() if text is not None else TextStyleForCell()
        cell_style_for_cell = cell.get_single() if cell is not None else CellStyleForCell()

        return StyledLocColumnLabels(
            style=StyleHolder(text=text_style_for_cell, cell=cell_style_for_cell),
            columns=self.columns,
        )


@dataclass
class StyledLocStubhead(StyledLoc):
    """Styled marker locator selecting the table stub head."""

    style: StyleHolder


@dataclass
class LocStubhead:
    """Select the stub-head cell.

    The stub head is the top-left header cell above the row-label stub column.
    Its visible label is set with `TypTable.tab_stubhead`.
    """

    def _apply_style(
        self,
        data: Data[IntoDataFrame],  # noqa: ARG002
        text: TextStyle | None = None,
        cell: CellStyle | None = None,
    ) -> StyledLocStubhead:
        """Build a styled stub head locator.

        Args:
            data: Source data used for row-level style resolution.
            text: Optional text style selector for body rows.
            cell: Optional cell style selector for body rows.

        Returns:
            Styled stub head locator with per-row style holders.
        """
        text_style_for_cell = text.get_single() if text is not None else TextStyleForCell()
        cell_style_for_cell = cell.get_single() if cell is not None else CellStyleForCell()

        return StyledLocStubhead(
            style=StyleHolder(text=text_style_for_cell, cell=cell_style_for_cell),
        )


@dataclass
class StyledLocStub(StyledLoc):
    """Styled marker locator selecting the table stub region."""

    style: list[StyleHolder]
    rows: RowSelector | None = None

    def resolve(self, data: Data[IntoDataFrame], rowname_col: str) -> list[CellPos]:
        """Resolve which cells in data to apply the style to."""
        rows = resolve_rows(data, self.rows)

        return [CellPos(column=rowname_col, row=r) for r in rows]


@dataclass
class LocStub:
    """Select row-label cells in the table stub.

    The stub is the left-hand column created from `rowname_col`. By default, all
    stub cells are selected. Use `rows` to limit the style rule to specific row
    labels.
    """

    rows: RowSelector | None = None
    """Rows whose stub cells should be selected.

    Accepts any [`RowSelector`][typ_tables.RowSelector]. `None` selects all
    stub rows.
    """

    def _apply_style(
        self,
        data: Data[IntoDataFrame],
        text: TextStyle | None = None,
        cell: CellStyle | None = None,
    ) -> StyledLocStub:
        """Build a styled stub locator.

        Args:
            data: Source data used for row-level style resolution.
            text: Optional text style selector for stub rows.
            cell: Optional cell style selector for stub rows.

        Returns:
            Styled stub locator with per-row style holders.
        """
        n_rows = len(data)
        text_styles_for_cells = (
            text.resolve(data) if text is not None else [TextStyleForCell()] * n_rows
        )
        cell_styles_for_cells = (
            cell.resolve(data) if cell is not None else [CellStyleForCell()] * n_rows
        )
        style_holders = []
        for text_style, cell_style in zip(
            text_styles_for_cells, cell_styles_for_cells, strict=True
        ):
            style_holders.append(StyleHolder(text=text_style, cell=cell_style))

        return StyledLocStub(style=style_holders, rows=self.rows)


Groups = list[str]


@dataclass
class StyledLocRowGroup(StyledLoc):
    """Styled Marker locator selecting the table row groups."""

    style: StyleHolder
    group: str | list[str] | None = None

    def resolve(self, data: Data[IntoDataFrame], group_key: str) -> Groups:
        """Resolve which cells in data to apply the style to."""
        unique_values = [
            str(v) for v in data.select(nw.col(group_key).unique())[group_key].to_list()
        ]
        if self.group is None:
            groups = unique_values
        elif isinstance(self.group, list):
            groups = [u for u in unique_values if u in self.group]
        else:
            groups = [u for u in unique_values if u == self.group]

        return groups


@dataclass
class LocRowGroup:
    """Select row-group label cells.

    Row-group labels are created from `groupname_col`. By default, all row-group
    labels are selected. Use `group` to limit styling to one or more group
    labels.
    """

    group: str | list[str] | None = None
    """Row-group label or labels to select.

    `None` selects every row group. A string selects the matching group label.
    A list selects all matching labels in the list.
    """

    def _apply_style(
        self,
        data: Data[IntoDataFrame],  # noqa: ARG002
        text: TextStyle | None = None,
        cell: CellStyle | None = None,
    ) -> StyledLocRowGroup:
        """Build a styled row-group locator.

        Args:
            data: Source data used for style resolution.
            text: Optional text style selector for row-group labels.
            cell: Optional cell style selector for row-group labels.

        Returns:
            Styled row-group locator with resolved style values.
        """
        text_style_for_cell = text.get_single() if text is not None else TextStyleForCell()
        cell_style_for_cell = cell.get_single() if cell is not None else CellStyleForCell()

        return StyledLocRowGroup(
            style=StyleHolder(text=text_style_for_cell, cell=cell_style_for_cell),
            group=self.group,
        )


@dataclass
class StyleForGroups:
    """Style mapping for a set of row-group identifiers."""

    groups: Groups
    style: StyleHolder


@dataclass
class RowGroupStyles:
    """Container for row-group style mappings and style resolution."""

    styles: list[StyleForGroups] = field(default_factory=list)

    def append(self, groups: Groups, style: StyleHolder) -> None:
        """Add a style assignment for one or more row groups.

        Args:
            groups: Row-group identifiers to associate with `style`.
            style: Style to apply when a group identifier matches.
        """
        self.styles.append(StyleForGroups(groups, style))

    def get_style(self, group_id: str, default: StyleHolder) -> StyleHolder:
        """Resolve the merged style for a given row-group identifier.

        Args:
            group_id: Row-group identifier to resolve.
            default: Default row group style.

        Returns:
            Combined style from all matching assignments.
        """
        group_cell_style = deepcopy(default)
        for style_for_groups in self.styles:
            if group_id in style_for_groups.groups:
                group_cell_style = group_cell_style | style_for_groups.style

        return group_cell_style


@dataclass
class StyledLocSpanner(StyledLoc):
    """Styled marker locator selecting the table spanner region."""

    style: StyleHolder
    spanner_ids: list[str] | None = None


@dataclass
class LocSpanner:
    """Select spanners in the table header.

    Spanners are the labels above one or more column labels.
    """

    spanner_ids: list[str] | None = None
    """Spanner IDs to target. The default `None` means all spanners will be targeted."""

    def _apply_style(
        self,
        data: Data[IntoDataFrame],  # noqa: ARG002
        text: TextStyle | None = None,
        cell: CellStyle | None = None,
    ) -> StyledLocSpanner:
        """Build a styled spanner locator.

        Args:
            data: Source data used for row-level style resolution.
            text: Optional text style selector for stub rows.
            cell: Optional cell style selector for stub rows.

        Returns:
            Styled stub locator with per-row style holders.
        """
        text_style_for_cell = text.get_single() if text is not None else TextStyleForCell()
        cell_style_for_cell = cell.get_single() if cell is not None else CellStyleForCell()

        return StyledLocSpanner(
            style=StyleHolder(text=text_style_for_cell, cell=cell_style_for_cell),
            spanner_ids=self.spanner_ids,
        )
