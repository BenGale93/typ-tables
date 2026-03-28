import polars as pl
from inline_snapshot import external
from narwhals import selectors as ncs

from typ_tables import TypTable
from typ_tables.escape import Typst


class TestBasic:
    def test_to_typst_string_int_float(self, table_check) -> None:
        df = pl.DataFrame(
            {
                "string": ["a", "b", "c"],
                "int": [10, 10000, 1000000],
                "float": [0.000001, 0.1368753, 163985.8374],
            }
        )

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

        table = TypTable(df)
        result = table.to_typst()

        assert result == external("uuid:f944eeb4-ed3d-44aa-ad20-0e29e69356cc.typ")

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
        table = TypTable(basic_data).cols_label_with(lambda x: Typst(f"#underline[{x}]"), columns=ncs.numeric())
        result = table.to_typst()

        assert result == external("uuid:b4b1d349-8c99-488d-9bde-a553cb59dff6.typ")

        warnings = table_check(result)

        assert len(warnings) == 0
