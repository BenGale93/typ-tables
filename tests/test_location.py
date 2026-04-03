import narwhals as nw
import pandas as pd
import polars as pl
import pytest
from narwhals import selectors as ncs

from typ_tables import location


@pytest.fixture
def col_data_polars() -> nw.DataFrame:
    return nw.from_native(pl.DataFrame({"a": [], "b": [], "c": []}), eager_only=True)


@pytest.fixture
def col_data_pandas() -> nw.DataFrame:
    return nw.from_native(pd.DataFrame({"a": [], "b": [], "c": []}), eager_only=True)


class TestResolveColumns:
    def test_resolve_cols_polars_none(self, col_data_polars):
        assert location.resolve_columns(col_data_polars, None) == ["a", "b", "c"]

    def test_resolve_cols_polars_expr(self, col_data_polars):
        assert location.resolve_columns(col_data_polars, ncs.matches("[ab]")) == ["a", "b"]

    def test_resolve_cols_polars_int(self, col_data_polars):
        assert location.resolve_columns(col_data_polars, -1) == ["c"]

    def test_resolve_cols_pandas_list(self, col_data_pandas):
        assert location.resolve_columns(col_data_pandas, ["a", "c"]) == ["a", "c"]

    def test_resolve_cols_pandas_str(self, col_data_pandas):
        assert location.resolve_columns(col_data_pandas, "a") == ["a"]

    def test_resolve_cols_pandas_int_list(self, col_data_pandas):
        assert location.resolve_columns(col_data_pandas, [0, -1]) == ["a", "c"]


@pytest.fixture
def row_data() -> nw.DataFrame:
    return nw.from_native(pl.DataFrame({"data": [1, 2, 3, 4, 5]}), eager_only=True)


class TestResolveRows:
    def test_resolve_rows_none(self, row_data):
        assert location.resolve_rows(row_data, None) == [0, 1, 2, 3, 4]

    def test_resolve_rows_expr(self, row_data):
        assert location.resolve_rows(row_data, (nw.col("data") < 3)) == [0, 1]

    def test_resolve_rows_int(self, row_data):
        assert location.resolve_rows(row_data, 1) == [1]

    def test_resolve_rows_list_int(self, row_data):
        assert location.resolve_rows(row_data, [1, 3]) == [1, 3]
