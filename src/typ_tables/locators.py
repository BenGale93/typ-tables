"""Module defining styling locators."""

import typing as t
from dataclasses import dataclass

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
    ) -> StyledLoc: ...


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
        text_style_for_cell = text.get_single() if text is not None else None
        cell_style_for_cell = cell.get_single() if cell is not None else None

        return StyledLocHeader(
            style=StyleHolder(text=text_style_for_cell, cell=cell_style_for_cell)
        )


@dataclass(kw_only=True)
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
        n_rows = len(data)
        text_styles_for_cells = text.resolve(data) if text is not None else [None] * n_rows
        cell_styles_for_cells = cell.resolve(data) if cell is not None else [None] * n_rows
        style_holders = []
        for text_style, cell_style in zip(
            text_styles_for_cells, cell_styles_for_cells, strict=True
        ):
            style_holders.append(StyleHolder(text=text_style, cell=cell_style))

        return StyledLocStub(style=style_holders, rows=self.rows)
