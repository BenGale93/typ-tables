"""Module for resolving which cells to apply formatters, stylers etc. to."""

import narwhals as nw
from narwhals import selectors as ncs
from narwhals.typing import IntoDataFrame

from typ_tables import ttypes
from typ_tables._constants import ROW_INDEX

ColumnSelector = ncs.Selector | list[str] | str | list[int] | int
"""A Type alias for all the types that can be used to select columns.

A ColumnSelector can be either:
    - A [Narwhals Selector](https://narwhals-dev.github.io/narwhals/api-reference/selectors/)
    - A list of column names.
    - A column name.
    - A list of column indices.
    - A column index.
"""
RowSelector = nw.Expr | list[int] | int
"""A Type alias for all the types that can be used to select rows.

A RowSelector can be either:
    - A [Narwhals Expression](https://narwhals-dev.github.io/narwhals/api-reference/dataframe/#narwhals.dataframe.DataFrame.filter)
        that filters a DataFrame.
    - A list of row indices.
    - A row index.

Row indices are zero-based positions into the source data. Negative indices
select from the end (`-1` is the last row), matching column selection. An index
outside the valid range raises `IndexError`.
"""


def resolve_columns(
    data: ttypes.Data[IntoDataFrame], selector: ColumnSelector | None = None
) -> list[str]:
    """Resolve the column names and positions based on the selection expression."""
    source_columns = [col for col in data.columns if col != ROW_INDEX]

    if isinstance(selector, int):
        selector = [selector]

    if isinstance(selector, list):
        new_selector = [source_columns[s] if isinstance(s, int) else s for s in selector]
    elif selector is None:
        new_selector = nw.all()
    else:
        new_selector = selector

    sub_data = data.select(new_selector)
    return [col for col in sub_data.columns if col != ROW_INDEX]


def resolve_rows(
    data: ttypes.Data[IntoDataFrame], selector: RowSelector | None = None
) -> list[int]:
    """Resolve the rows the selector expression is selecting."""
    if isinstance(selector, int):
        selector = [selector]
    if isinstance(selector, list):
        n_rows = len(data)
        resolved_rows = []
        for index in selector:
            position = index + n_rows if index < 0 else index
            if not 0 <= position < n_rows:
                msg = f"Row index {index} is out of range: the table has {n_rows} rows."
                raise IndexError(msg)
            resolved_rows.append(position)
        return resolved_rows
    if selector is None:
        return data.with_row_index()["index"].to_list()
    return data.with_row_index().filter(selector)["index"].to_list()
