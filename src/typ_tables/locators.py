"""Module defining styling locators."""

import typing as t
from copy import deepcopy
from dataclasses import dataclass, field

import narwhals as nw

from typ_tables.location import ColumnSelector, RowSelector, resolve_columns, resolve_rows
from typ_tables.style import CellStyle, StyleHolder, TextStyle
from typ_tables.ttypes import Data


@dataclass
class StyledLoc:
    """Base marker for table style locator targets, that have been styled."""


class Loc(t.Protocol):
    """Base marker for table style locator targets.

    This class is used as a common type for location-specific style selectors.
    Subclasses identify concrete table regions (for example, header cells).
    """

    def _apply_style(
        self,
        data: Data,
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
    """Marker locator selecting the table header region."""

    def _apply_style(
        self,
        data: Data,  # noqa: ARG002
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
        text_style_for_cell = text.get_single() if text is not None else None
        cell_style_for_cell = cell.get_single() if cell is not None else None

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

    def resolve(self, data: Data) -> list[CellPos]:
        """Resolve which cells in data to apply the style to."""
        columns = resolve_columns(data, self.columns)
        rows = resolve_rows(data, self.rows)

        return [CellPos(column=c, row=r) for r in rows for c in columns]


@dataclass
class LocBody:
    """Marker locator selecting the table body region."""

    columns: ColumnSelector | None = None
    rows: RowSelector | None = None

    def _apply_style(
        self,
        data: Data,
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
        text_styles_for_cells = text.resolve(data) if text is not None else [None] * n_rows
        cell_styles_for_cells = cell.resolve(data) if cell is not None else [None] * n_rows
        style_holders = []
        for text_style, cell_style in zip(
            text_styles_for_cells, cell_styles_for_cells, strict=True
        ):
            style_holders.append(StyleHolder(text=text_style, cell=cell_style))

        return StyledLocBody(style=style_holders, columns=self.columns, rows=self.rows)


@dataclass
class StyledLocStub(StyledLoc):
    """Styled marker locator selecting the table stub region."""

    style: list[StyleHolder]
    rows: RowSelector | None = None

    def resolve(self, data: Data, rowname_col: str) -> list[CellPos]:
        """Resolve which cells in data to apply the style to."""
        rows = resolve_rows(data, self.rows)

        return [CellPos(column=rowname_col, row=r) for r in rows]


@dataclass
class LocStub:
    """Marker locator selecting the table stub region."""

    rows: RowSelector | None = None

    def _apply_style(
        self,
        data: Data,
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
        text_styles_for_cells = text.resolve(data) if text is not None else [None] * n_rows
        cell_styles_for_cells = cell.resolve(data) if cell is not None else [None] * n_rows
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

    def resolve(self, data: Data, group_key: str) -> Groups:
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
    """Marker locator selecting the table row groups."""

    group: str | list[str] | None = None

    def _apply_style(
        self,
        data: Data,  # noqa: ARG002
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
        text_style_for_cell = text.get_single() if text is not None else None
        cell_style_for_cell = cell.get_single() if cell is not None else None

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
