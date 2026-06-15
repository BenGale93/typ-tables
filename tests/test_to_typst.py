import narwhals as nw
import polars as pl
import pytest
from inline_snapshot import external
from narwhals import selectors as ncs
from narwhals.exceptions import ColumnNotFoundError

from typ_tables import TypTable, locators, style
from typ_tables._escape import Typst


class TestBasic:
    def test_to_typst_empty(self) -> None:
        df = pl.DataFrame({})

        with pytest.raises(ValueError, match=r"Data must have at least one column."):
            # pyrefly: ignore [bad-argument-type]
            TypTable(df)

    def test_to_typst_string_int_float(self, table_check) -> None:
        df = pl.DataFrame(
            {
                "string": ["a", "b", "c"],
                "int": [10, 10000, 1000000],
                "float": [0.000001, 0.1368753, 163985.8374],
            }
        )

        # pyrefly: ignore [bad-argument-type]
        table = TypTable(df)
        result = table.to_typst()

        assert result == external("uuid:dfe29286-a9ca-477b-be00-4ffd55201fc1.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_to_typst_escaped(self, table_check) -> None:
        df = pl.DataFrame(
            {
                "= Header": [
                    "#a",
                    "Stuff #Here",
                    "That's a lot of $",
                    "Stuff\\Or",
                    "A <label>",
                    "@reference",
                    "Higher~Lower",
                    "yes_no_maybe",
                    "hello^squared",
                    "Stuff {Other}",
                    "More (brackets)",
                    "*bold*",
                    "hello*star",
                    "- list",
                ],
            }
        )

        # pyrefly: ignore [bad-argument-type]
        table = TypTable(df)
        result = table.to_typst()

        assert result == external("uuid:f944eeb4-ed3d-44aa-ad20-0e29e69356cc.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_to_typst_rowname_col_reorders_columns(self, table_check) -> None:
        df = pl.DataFrame(
            {
                "int": [10, 10000, 1000000],
                "float": [0.000001, 0.1368753, 163985.8374],
                "string": ["a", "b", "c"],
            }
        )

        # pyrefly: ignore [bad-argument-type]
        table = TypTable(df, rowname_col="string")
        result = table.to_typst()

        assert result == external("uuid:c6ef5a0d-192b-4311-9f2b-c60ebb17cc3d.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_to_typst_groupname_col(self, table_check, group_data) -> None:
        table = TypTable(group_data, rowname_col="fruit", groupname_col="group")
        result = table.to_typst()

        assert result == external("uuid:3929626d-bdef-4d46-a714-4f1317e59368.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_to_typst_rowname_col_with_title(self, table_check) -> None:
        df = pl.DataFrame(
            {
                "int": [10, 10000, 1000000],
                "float": [0.000001, 0.1368753, 163985.8374],
                "string": ["a", "b", "c"],
            }
        )

        # pyrefly: ignore [bad-argument-type]
        table = TypTable(df, rowname_col="string").tab_header(title="Title Here")
        result = table.to_typst()

        assert result == external("uuid:0fa6495c-840e-4777-a51c-45a54abd27a4.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_to_typst_rowname_col_with_stubhead(self, table_check) -> None:
        df = pl.DataFrame(
            {
                "int": [10, 10000, 1000000],
                "float": [0.000001, 0.1368753, 163985.8374],
                "string": ["a", "b", "c"],
            }
        )

        # pyrefly: ignore [bad-argument-type]
        table = TypTable(df, rowname_col="string").tab_stubhead(label="Test")
        result = table.to_typst()

        assert result == external("uuid:5a710293-3fba-423e-a890-1e7cfcc0c0c6.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_to_typst_format_header(self, table_check) -> None:
        df = pl.DataFrame(
            {
                "int": [10, 10000, 1000000],
                "float": [0.000001, 0.1368753, 163985.8374],
                "string": ["a", "b", "c"],
            }
        )

        table = (
            # pyrefly: ignore [bad-argument-type]
            TypTable(df)
            .tab_style(
                cell=style.CellStyle(align="right", inset=style.Sides(bottom="20pt")),
                text=style.TextStyle(size="15pt", fill="blue"),
                locator=locators.LocHeader(),
            )
            .tab_header("Test Header")
        )
        result = table.to_typst()

        assert result == external("uuid:80b276c0-46d7-48d4-98a6-10588ca067f0.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_with_id(self, table_check, basic_data):
        table = TypTable(basic_data).with_id("test")
        result = table.to_typst()

        assert result == external("uuid:c2754f0b-c027-4f0e-9699-85101d338c26.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestPipe:
    def test_pipe_applies_styling(self, table_check, basic_data):
        def colour_max(tbl: TypTable, columns: list[str]) -> TypTable:
            for column in columns:
                tbl = tbl.tab_style(
                    cell=style.CellStyle(fill="red"),
                    locator=locators.LocBody(
                        columns=column, rows=(nw.col(column) == nw.col(column).max())
                    ),
                )
            return tbl

        table = TypTable(basic_data).pipe(colour_max, ["int", "float"])
        result = table.to_typst()

        assert result == external("uuid:c0eafe10-e482-472d-abb3-f109130918db.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestAlignColumns:
    def test_align_numeric_columns_right(self, table_check, basic_data):
        table = TypTable(basic_data).cols_align(align="right", columns=ncs.numeric())
        result = table.to_typst()

        assert result == external("uuid:560ef812-0edd-4fc6-bb68-5c1f626a4662.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestHideColumns:
    def test_hide_given_columns(self, table_check, basic_data):
        table = TypTable(basic_data).cols_hide("string")
        result = table.to_typst()

        assert result == external("uuid:23b96023-753e-4f75-8646-d315756f2cfd.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestMoveColumns:
    @staticmethod
    def _assert_labels_in_order(result: str, labels: list[str]) -> None:
        label_positions = [result.index(f"[{label}]") for label in labels]

        assert label_positions == sorted(label_positions)

    def test_move_single_column(self, table_check, basic_data):
        table = TypTable(basic_data).cols_move("float", after="string")
        result = table.to_typst()

        assert result == external("uuid:81197461-2706-41c2-b8a5-ccada0dbbd52.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_move_multiple_columns(self, table_check, basic_data):
        table = TypTable(basic_data).cols_move(["string", "int"], after="float")
        result = table.to_typst()

        assert result == external("uuid:04e22e70-6836-48af-bf96-5012136db122.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_move_after_column_cannot_be_moved(self, basic_data):
        with pytest.raises(
            ValueError,
            match=(
                r"Cannot move columns \['string', 'int'\] after 'string' because 'string' is one "
                r"of the columns being moved\. Choose an `after` column that is not included in "
                r"`columns`\."
            ),
        ):
            TypTable(basic_data).cols_move(["string", "int"], after="string")

    def test_move_with_stub_and_group_columns(self, table_check):
        df = pl.DataFrame(
            {
                "group": ["citrus", "citrus", "berry"],
                "fruit": ["orange", "lemon", "strawberry"],
                "count": [12, 8, 24],
                "price": [1.25, 0.8, 3.5],
            }
        )

        # pyrefly: ignore [bad-argument-type]
        table = TypTable(df, rowname_col="fruit", groupname_col="group").cols_move(
            "price", after="fruit"
        )
        result = table.to_typst()

        self._assert_labels_in_order(result, ["price", "count"])
        assert "[citrus]" in result
        assert "[berry]" in result

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_move_with_selector(self, table_check):
        df = pl.DataFrame(
            {
                "int": [1, 2],
                "float": [1.5, 2.5],
                "string": ["a", "b"],
            }
        )

        # pyrefly: ignore [bad-argument-type]
        table = TypTable(df).cols_move(ncs.numeric(), after="string")
        result = table.to_typst()

        self._assert_labels_in_order(result, ["string", "int", "float"])

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_move_with_column_index(self, table_check, basic_data):
        table = TypTable(basic_data).cols_move(2, after="string")
        result = table.to_typst()

        self._assert_labels_in_order(result, ["string", "float", "int"])

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_move_hidden_column(self, table_check, basic_data):
        table = TypTable(basic_data).cols_hide("int").cols_move("int", after="float")
        result = table.to_typst()

        assert "[int]" not in result
        self._assert_labels_in_order(result, ["string", "float"])

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_move_after_hidden_column(self, table_check, basic_data):
        table = TypTable(basic_data).cols_hide("int").cols_move("string", after="int")
        result = table.to_typst()

        assert "[int]" not in result
        self._assert_labels_in_order(result, ["string", "float"])

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_move_unknown_column(self, basic_data):
        with pytest.raises(ColumnNotFoundError, match=r"missing"):
            TypTable(basic_data).cols_move("missing", after="string")

    def test_move_after_unknown_column(self, basic_data):
        with pytest.raises(ColumnNotFoundError, match=r"missing"):
            TypTable(basic_data).cols_move("float", after="missing")


class TestLabelColumns:
    def test_label_with_string(self, table_check, basic_data):
        table = TypTable(basic_data).cols_label(cases={"string": "String"}, int="Integer")
        result = table.to_typst()

        assert result == external("uuid:ab19ec62-2064-42f5-9b21-2e9a681e828a.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_label_with_raw_typst(self, table_check, basic_data):
        table = TypTable(basic_data).cols_label(
            cases={
                "string": Typst("#strong[String]"),
            },
            int=Typst("#underline[Integer]"),
            float=Typst("$pi r^2$"),
        )
        result = table.to_typst()

        assert result == external("uuid:10644c46-4d17-402c-b326-1aef158b9111.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestLabelColumnsWith:
    def test_label_upper(self, table_check, basic_data):
        table = TypTable(basic_data).cols_label_with(str.upper)
        result = table.to_typst()

        assert result == external("uuid:d2909bac-35bc-4711-80a1-47e641781530.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_label_with_raw_typst_func(self, table_check, basic_data):
        table = TypTable(basic_data).cols_label_with(
            lambda x: Typst(f"#underline[{x}]"), columns=ncs.numeric()
        )
        result = table.to_typst()

        assert result == external("uuid:b4b1d349-8c99-488d-9bde-a553cb59dff6.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestEdgeCases:
    def test_group_column_with_align_set(self, table_check, group_data):
        table = TypTable(group_data, rowname_col="fruit", groupname_col="group")

        with pytest.warns(
            UserWarning, match=r"Setting alignment on the row group column, this will do nothing."
        ):
            table = table.cols_align("right", columns="group")
        result = table.to_typst()

        assert result == external("uuid:7b3effea-cf1a-4eb4-bd9f-77e626389c12.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_group_column_no_rowname_col(self, group_data):
        with pytest.raises(ValueError, match=r"If groupname_col is provided, so must rowname_col."):
            _ = TypTable(group_data, groupname_col="group")

    def test_group_column_with_stubhead(self, table_check, group_data):
        table = TypTable(group_data, rowname_col="fruit", groupname_col="group")

        table = table.tab_stubhead("Fruits")
        result = table.to_typst()

        assert result == external("uuid:e00d6285-8d9c-4ce6-8eb5-a9cce90e5f67.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_group_column_with_bottom_row_stroke_styled(self, table_check, group_data):
        table = TypTable(group_data, rowname_col="fruit", groupname_col="group")

        table = table.tab_style(
            cell=style.CellStyle(stroke={"bottom": "1pt + red"}),
            locator=locators.LocStub(rows=3),
        )
        result = table.to_typst()

        assert result == external("uuid:1b1f2aa9-97bf-44ce-96ba-87f304d3ae6a.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_column_label_with_underscore(self, table_check):
        df = pl.DataFrame({"test_name": ["stuff", "more_stuff"]})

        # pyrefly: ignore [bad-argument-type]
        table = TypTable(df)

        result = table.to_typst()

        assert result == external("uuid:ebeb174f-9dfd-4dcf-800d-71d00af6e936.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestTabOptions:
    def test_hide_column_labels(self, table_check, basic_data):
        table = TypTable(basic_data).tab_options(column_labels_hidden=True)
        result = table.to_typst()

        assert result == external("uuid:5c79abae-d40d-406c-a0ca-3ca65710925e.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_hide_column_labels_with_header(self, table_check, basic_data):
        table = (
            TypTable(basic_data).tab_options(column_labels_hidden=True).tab_header("Title header")
        )
        result = table.to_typst()

        assert result == external("uuid:a8715af7-60ce-44db-99a4-55524f3ea27f.typ")

        warnings = table_check(result)

        assert len(warnings) == 0
