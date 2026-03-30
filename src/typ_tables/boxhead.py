"""Module containing functionality related to the column headers."""

import typing as t
from dataclasses import dataclass

from typ_tables import constants, escape, ttypes

ColType = t.Literal["default", "stub", "row_group", "hidden"]


@dataclass
class ColInfo:
    """Container for information about each column."""

    var: str
    col_type: ColType
    column_label: str | escape.Typst | None = None
    column_align: ttypes.Alignment | ttypes.Auto = "auto"
    column_width: str | None = None

    @property
    def name(self) -> str:
        """Return the name of the column the table should use."""
        return escape.escape_value(self.column_label or self.var)


class Boxhead(list[ColInfo]):
    """Represents the boxhead of the table."""

    def set_stub_cols(self, rowname_col: str | None, groupname_col: str | None) -> None:
        """Sets the columns in the boxhead that will be in the stub."""
        for col in self:
            if col.var == rowname_col:
                col.col_type = "stub"
            elif col.var == groupname_col:
                col.col_type = "row_group"
            elif col.col_type in {"stub", "row_group"}:
                col.col_type = "default"

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

    def set_cols_label(self, col_labels: dict[str, str | escape.Typst]) -> None:
        """Sets the labels of the columns using the given map."""
        for col in self:
            new_label = col_labels.get(col.var)
            if new_label is not None:
                col.column_label = new_label

    def final_columns(self) -> list[ColInfo]:
        """Get the final order of the columns."""
        return [
            *self._get_columns_of_type("row_group"),
            *self._get_columns_of_type("stub"),
            *self._get_columns_of_type("default"),
        ]

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
