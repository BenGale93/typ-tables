"""Module containing functionality related to the column headers."""

import typing as t
from dataclasses import dataclass

from typ_tables import constants, ttypes

ColType = t.Literal["default", "stub", "row_group", "hidden"]


@dataclass
class ColInfo:
    """Container for information about each column."""

    var: str
    col_type: ColType
    column_label: str | None = None
    column_align: ttypes.Alignment | ttypes.Auto = "auto"
    column_width: str | None = None

    @property
    def name(self) -> str:
        """Return the name of the column the table should use."""
        return self.column_label or self.var


class Boxhead(list[ColInfo]):
    """Represents the boxhead of the table."""

    def set_cols_hidden(self, col_names: t.Iterable[str]) -> None:
        """Sets the columns as hidden."""
        for col in self:
            if col.var in col_names:
                col.col_type = "hidden"

    def set_cols_align(self, col_names: t.Iterable[str], align: ttypes.Alignment) -> None:
        """Sets the alignment of the given columns."""
        for col in self:
            if col.var in col_names:
                col.column_align = align

    def final_columns(self) -> list[ColInfo]:
        """Get the final order of the columns."""
        return [*self._get_columns_of_type("default")]

    def _get_columns_of_type(self, col_type: ColType) -> list[ColInfo]:
        return [c for c in self if c.col_type == col_type]

    @classmethod
    def from_data(cls, data: ttypes.Data) -> t.Self:
        """Creates boxhead from the given data."""
        boxhead = cls([])
        for name in data.columns:
            if name == constants.ROW_INDEX:
                continue
            col_info = ColInfo(var=name, col_type="default", column_align="auto")
            boxhead.append(col_info)
        return boxhead
