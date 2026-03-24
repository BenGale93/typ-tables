"""Module for resolving which cells to apply formatters, stylers etc. to."""

from narwhals import DataFrame, Expr
from narwhals import selectors as ncs
from narwhals.typing import IntoDataFrameT

ColumnSelector = ncs.Selector | list[str] | str | list[int] | int
RowSelector = Expr | list[int] | int


def resolve_columns(data: DataFrame[IntoDataFrameT], selector: ColumnSelector) -> list[tuple[str, int]]:
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
    else:
        new_selector = selector

    sub_data = data.select(new_selector)

    final_columns = sub_data.columns

    col_pos = {k: i for i, k in enumerate(data.columns)}
    return [(col, col_pos[col]) for col in final_columns]


def resolve_rows(data: DataFrame[IntoDataFrameT], selector: RowSelector) -> list[int]:
    """Resolve the rows the selector expression is selecting."""
    if isinstance(selector, int):
        return [selector]
    if isinstance(selector, list):
        return selector
    return data.with_row_index().filter(selector)["index"].to_list()
