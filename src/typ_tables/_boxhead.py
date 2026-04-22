"""Module containing functionality related to the column headers."""

import typing as t
import warnings
from dataclasses import dataclass

from typ_tables import _constants, _escape, ttypes

ColType = t.Literal["default", "stub", "row_group", "hidden"]


@dataclass
class ColInfo:
    """Container for information about each column."""

    var: str
    col_type: ColType
    column_label: str | _escape.Typst | None = None
    column_align: ttypes.Alignment | ttypes.Auto = "auto"
    column_width: str | None = None

    @property
    def name(self) -> str:
        """Return the name of the column the table should use."""
        return _escape.escape_value(self.column_label or self.var)


class Boxhead(list[ColInfo]):
    """Represents the boxhead of the table."""

    def __len__(self) -> int:
        """Number of columns the boxhead will render to."""
        return len(self.get_stub_and_default_columns())

    def set_cols_hidden(self, col_names: t.Iterable[str]) -> None:
        """Sets the columns as hidden."""
        for col in self:
            if col.var in col_names:
                col.col_type = "hidden"

    def set_cols_align(self, col_names: t.Iterable[str], align: ttypes.Alignment) -> None:
        """Sets the alignment of the given columns."""
        for col in self:
            if col.col_type == "row_group":
                warnings.warn(
                    "Setting alignment on the row group column, this will do nothing.", stacklevel=2
                )
                continue
            if col.var in col_names:
                col.column_align = align

    def set_cols_label(self, col_labels: dict[str, str | _escape.Typst]) -> None:
        """Sets the labels of the columns using the given map."""
        for col in self:
            new_label = col_labels.get(col.var)
            if new_label is not None:
                col.column_label = new_label

    def get_group_column_name(self) -> str | None:
        """Gets the default columns."""
        row_group_cols = self._get_columns_of_type("row_group")
        if len(row_group_cols) == 0:
            return None
        return row_group_cols[0].var

    def get_default_columns(self) -> list[ColInfo]:
        """Gets the default columns."""
        return self._get_columns_of_type("default")

    def get_stub_and_default_columns(self) -> list[ColInfo]:
        """Gets the stub and then default columns."""
        return [*self._get_columns_of_type("stub"), *self.get_default_columns()]

    def _get_columns_of_type(self, col_type: ColType) -> list[ColInfo]:
        return [c for c in self if c.col_type == col_type]

    @classmethod
    def from_data(
        cls, data: ttypes.Data, rowname_col: str | None, groupname_col: str | None
    ) -> t.Self:
        """Creates boxhead from the given data."""
        boxhead = cls([])
        for name in data.columns:
            if name == _constants.ROW_INDEX:
                continue
            if name == rowname_col:
                col_type = "stub"
            elif name == groupname_col:
                col_type = "row_group"
            else:
                col_type = "default"
            col_info = ColInfo(var=name, col_type=col_type, column_align="auto")
            boxhead.append(col_info)
        return boxhead
