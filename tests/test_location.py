import narwhals as nw
import pandas as pd
import polars as pl
import pytest
from narwhals import selectors as ncs
from polars.exceptions import DuplicateError

from typ_tables import TypTable, _location
from typ_tables._constants import ROW_INDEX


@pytest.fixture
# pyrefly: ignore [bad-specialization]
def col_data_polars() -> nw.DataFrame[pl.DataFrame]:
    # pyrefly: ignore [no-matching-overload]
    return nw.from_native(pl.DataFrame({"a": [], "b": [], "c": []}), eager_only=True)


@pytest.fixture
# pyrefly: ignore [bad-specialization]
def col_data_pandas() -> nw.DataFrame[pd.DataFrame]:
    # pyrefly: ignore [no-matching-overload]
    return nw.from_native(pd.DataFrame({"a": [], "b": [], "c": []}), eager_only=True)


class TestResolveColumns:
    def test_resolve_cols_polars_none(self, col_data_polars):
        assert _location.resolve_columns(col_data_polars, None) == ["a", "b", "c"]

    def test_resolve_cols_polars_expr(self, col_data_polars):
        assert _location.resolve_columns(col_data_polars, ncs.matches("[ab]")) == ["a", "b"]

    def test_resolve_cols_polars_int(self, col_data_polars):
        assert _location.resolve_columns(col_data_polars, -1) == ["c"]

    def test_resolve_cols_polars_positive_int(self, col_data_polars):
        assert _location.resolve_columns(col_data_polars, 1) == ["b"]

    def test_resolve_cols_pandas_list(self, col_data_pandas):
        assert _location.resolve_columns(col_data_pandas, ["a", "c"]) == ["a", "c"]

    def test_resolve_cols_pandas_str(self, col_data_pandas):
        assert _location.resolve_columns(col_data_pandas, "a") == ["a"]

    def test_resolve_cols_pandas_int_list(self, col_data_pandas):
        assert _location.resolve_columns(col_data_pandas, [0, -1]) == ["a", "c"]


SOURCE_COLUMNS = ["product", "region", "revenue", "margin", "units"]


@pytest.fixture(params=["polars", "pandas"])
def indexed_data(column_selector_data, request):
    """A frame with the internal row index prepended, as `TypTable` stores it."""
    native = column_selector_data if request.param == "polars" else column_selector_data.to_pandas()
    return nw.from_native(native, eager_only=True).with_row_index(ROW_INDEX)


@pytest.fixture
def polars_indexed_data(column_selector_data):
    return nw.from_native(column_selector_data, eager_only=True).with_row_index(ROW_INDEX)


class TestResolveColumnsWithRowIndex:
    """Integer selectors must ignore the internal `__row_index` column."""

    def test_positive_int_is_source_relative(self, indexed_data):
        assert _location.resolve_columns(indexed_data, 0) == ["product"]
        assert _location.resolve_columns(indexed_data, 1) == ["region"]
        assert _location.resolve_columns(indexed_data, 2) == ["revenue"]
        assert _location.resolve_columns(indexed_data, 4) == ["units"]

    def test_negative_int_is_source_relative(self, indexed_data):
        assert _location.resolve_columns(indexed_data, -1) == ["units"]
        assert _location.resolve_columns(indexed_data, -5) == ["product"]

    def test_int_list_is_source_relative(self, indexed_data):
        assert _location.resolve_columns(indexed_data, [0, 2]) == ["product", "revenue"]

    def test_mixed_names_and_ints(self, indexed_data):
        # pyrefly: ignore [bad-argument-type]
        assert _location.resolve_columns(indexed_data, ["product", 2]) == ["product", "revenue"]

    def test_none_selects_every_source_column(self, indexed_data):
        assert _location.resolve_columns(indexed_data, None) == SOURCE_COLUMNS

    def test_row_index_is_never_selected(self, indexed_data):
        selectors = [0, None, list(range(len(SOURCE_COLUMNS)))]
        for selector in selectors:
            assert ROW_INDEX not in _location.resolve_columns(indexed_data, selector)

    def test_positive_int_out_of_range(self, indexed_data):
        with pytest.raises(IndexError):
            _location.resolve_columns(indexed_data, len(SOURCE_COLUMNS))

    def test_negative_int_out_of_range(self, indexed_data):
        with pytest.raises(IndexError):
            _location.resolve_columns(indexed_data, -len(SOURCE_COLUMNS) - 1)

    def test_genuine_duplicate_raises(self, polars_indexed_data):
        with pytest.raises(DuplicateError):
            # pyrefly: ignore [bad-argument-type]
            _location.resolve_columns(polars_indexed_data, [1, "region"])

    def test_stub_and_group_positions_are_source_order(self):
        df = pl.DataFrame(
            {
                "group": ["a", "a", "b"],
                "fruit": ["orange", "lemon", "strawberry"],
                "count": [1, 2, 3],
                "price": [1.0, 2.0, 3.0],
            }
        )

        # pyrefly: ignore [bad-argument-type]
        table = TypTable(df, rowname_col="fruit", groupname_col="group")

        assert _location.resolve_columns(table._df, 0) == ["group"]
        assert _location.resolve_columns(table._df, 1) == ["fruit"]
        assert _location.resolve_columns(table._df, 2) == ["count"]
        assert _location.resolve_columns(table._df, 3) == ["price"]


@pytest.fixture
# pyrefly: ignore [bad-specialization]
def row_data() -> nw.DataFrame[pl.DataFrame]:
    # pyrefly: ignore [no-matching-overload]
    return nw.from_native(pl.DataFrame({"data": [1, 2, 3, 4, 5]}), eager_only=True)


class TestResolveRows:
    def test_resolve_rows_none(self, row_data):
        assert _location.resolve_rows(row_data, None) == [0, 1, 2, 3, 4]

    def test_resolve_rows_expr(self, row_data):
        assert _location.resolve_rows(row_data, (nw.col("data") < 3)) == [0, 1]

    def test_resolve_rows_int(self, row_data):
        assert _location.resolve_rows(row_data, 1) == [1]

    def test_resolve_rows_list_int(self, row_data):
        assert _location.resolve_rows(row_data, [1, 3]) == [1, 3]

    def test_resolve_rows_negative_int(self, row_data):
        assert _location.resolve_rows(row_data, -1) == [4]
        assert _location.resolve_rows(row_data, -5) == [0]

    def test_resolve_rows_negative_int_list(self, row_data):
        assert _location.resolve_rows(row_data, [0, -1]) == [0, 4]

    def test_resolve_rows_positive_out_of_range(self, row_data):
        with pytest.raises(IndexError):
            _location.resolve_rows(row_data, 5)

    def test_resolve_rows_negative_out_of_range(self, row_data):
        with pytest.raises(IndexError):
            _location.resolve_rows(row_data, -6)
