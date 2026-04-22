"""Module for resolving which cells to apply formatters, stylers etc. to."""

from contextlib import suppress

import narwhals as nw
from narwhals import selectors as ncs

from typ_tables import ttypes
from typ_tables._constants import ROW_INDEX

ColumnSelector = ncs.Selector | list[str] | str | list[int] | int
RowSelector = nw.Expr | list[int] | int


def resolve_columns(data: ttypes.Data, selector: ColumnSelector | None = None) -> list[str]:
    """Resolve the column names and positions based on the selection expression."""
    if isinstance(selector, int):
        selector = [selector]

    if isinstance(selector, list):
        new_selector = []
        for s in selector:
            if isinstance(s, int):
                new_selector.append(data.columns[s])
            else:
                new_selector.append(s)
    elif selector is None:
        new_selector = nw.all()
    else:
        new_selector = selector

    sub_data = data.select(new_selector)

    columns = sub_data.columns
    with suppress(ValueError):
        columns.remove(ROW_INDEX)
    return columns


def resolve_rows(data: ttypes.Data, selector: RowSelector | None = None) -> list[int]:
    """Resolve the rows the selector expression is selecting."""
    if isinstance(selector, int):
        return [selector]
    if isinstance(selector, list):
        return selector
    if selector is None:
        return data.with_row_index()["index"].to_list()
    return data.with_row_index().filter(selector)["index"].to_list()
