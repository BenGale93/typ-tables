"""Module defining styling locators."""

from dataclasses import dataclass

from typ_tables.location import ColumnSelector, RowSelector, resolve_columns, resolve_rows
from typ_tables.ttypes import Data


@dataclass
class Loc:
    """Base marker for table style locator targets.

    This class is used as a common type for location-specific style selectors.
    Subclasses identify concrete table regions (for example, header cells).
    """


@dataclass
class LocHeader(Loc):
    """Marker locator selecting the table header region.

    Instances of this locator are used when applying styles intended for
    header cells.
    """


@dataclass(kw_only=True)
class CellPos:
    """Class representing a cell in a DataFrame."""

    column: str
    row: int


@dataclass
class LocBody(Loc):
    """Marker locator selecting the table body region."""

    columns: ColumnSelector | None = None
    rows: RowSelector | None = None

    def resolve(self, data: Data) -> list[CellPos]:
        """Resolve which cells in data to apply the style to."""
        columns = resolve_columns(data, self.columns)
        rows = resolve_rows(data, self.rows)

        return [CellPos(column=c, row=r) for r in rows for c in columns]


@dataclass
class LocStub(Loc):
    """Marker locator selecting the table stub region."""

    rows: RowSelector | None = None

    def resolve(self, data: Data, rowname_col: str) -> list[CellPos]:
        """Resolve which cells in data to apply the style to."""
        rows = resolve_rows(data, self.rows)

        return [CellPos(column=rowname_col, row=r) for r in rows]
