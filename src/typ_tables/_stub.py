"""Module containing functionality related to the left hand side of the table."""

import typing as t
from dataclasses import dataclass, field

import narwhals as nw

from typ_tables import _constants, ttypes

if t.TYPE_CHECKING:
    from typ_tables._boxhead import Boxhead


@dataclass
class RowInfo:
    """Container class for row information."""

    rownum_i: int
    group_id: str | None = None
    rowname: str | None = None
    group_label: str | None = None
    built: bool = False


@dataclass
class GroupRowInfo:
    """Container class for grouping row information."""

    group_id: str
    group_label: str | None = None
    indices: list[int] = field(default_factory=list)
    summary_row_side: str | None = None

    @property
    def name(self) -> str:
        """Return the name of the group row."""
        return self.group_label if self.group_label is not None else self.group_id


class GroupRows(list[GroupRowInfo]):
    """List of grouping rows."""

    @classmethod
    def from_data(cls, data: ttypes.Data, group_key: str) -> t.Self:
        """Create an instance from the underlying data."""
        group_map: dict[t.Any, list[int]] = {}
        unique_values = data.select(nw.col(group_key).unique())
        for group in unique_values[group_key]:
            row_indices = data.filter(nw.col(group_key) == nw.lit(group))[
                _constants.ROW_INDEX
            ].to_list()
            group_map[group] = row_indices

        return cls(
            [
                GroupRowInfo(group_id=str(group_id), indices=ind)
                for group_id, ind in group_map.items()
            ]
        )

    def reorder(self, group_ids: list[str]) -> t.Self:
        """Reorder the group rows to match the group_ids."""
        current_order = {grp.group_id: i for i, grp in enumerate(self)}

        reordered = [self[current_order[g]] for g in group_ids]

        return self.__class__(reordered)

    def indices_map(self, n: int) -> list[tuple[int, GroupRowInfo | None]]:
        """Return pairs of row index, group label for all rows in data.

        Note that when no groupings exist, n is used to return from range(n).
        In this case, None is used to indicate there is no grouping.
        """
        return (
            [(ii, None) for ii in range(n)]
            if not self
            else [(ind, info) for info in self for ind in info.indices]
        )


class Stub:
    """Container for row information and labels, along with grouping information.

    This class handles the following:

      * Creating row and grouping information from data.
      * Determining row order for final presentation.

    Note that the order of entries in .group_rows determines final rendering order.
    When .group_rows is empty, the original data order is used.
    """

    rows: list[RowInfo]
    group_rows: GroupRows

    def __init__(self, rows: list[RowInfo], group_rows: GroupRows) -> None:
        """Initialise the stub with the given rows and grouping rows."""
        self.rows = rows.copy()
        self.group_rows = group_rows

    @classmethod
    def from_data(
        cls, data: ttypes.Data, rowname_col: str | None = None, groupname_col: str | None = None
    ) -> t.Self:
        """Create an instance from the underlying data."""
        # Obtain a list of row indices from the data and initialize
        # the `_stub` from that
        n_rows = len(data)
        row_indices = list(range(n_rows))

        group_id = data[groupname_col].to_list() if groupname_col is not None else [None] * n_rows

        row_names = data[rowname_col].to_list() if rowname_col is not None else [None] * n_rows

        # Obtain the column names from the data and initialize the
        # `_stub` from that
        row_info = [RowInfo(*i) for i in zip(row_indices, group_id, row_names, strict=False)]

        # create groups, and ensure they're ordered by first observed
        group_names = list(
            {row.group_id: True for row in row_info if row.group_id is not None}.keys()
        )
        if groupname_col is None:
            group_rows = GroupRows([])
        else:
            group_rows = GroupRows.from_data(data, group_key=groupname_col).reorder(group_names)

        return cls(row_info, group_rows)

    def group_indices_map(self) -> list[tuple[int, GroupRowInfo | None]]:
        return self.group_rows.indices_map(len(self.rows))

    def update_group_row_labels(self, data: ttypes.Data, boxhead: "Boxhead") -> None:
        """Updates the group row labels based on the formatted data."""
        rowgroup_var = boxhead.get_group_column_name()
        if rowgroup_var is None:
            return

        for group_row in self.group_rows:
            first_index = group_row.indices[0]
            cell_content = data.item(row=first_index, column=rowgroup_var)
            group_row.group_label = str(cell_content)
