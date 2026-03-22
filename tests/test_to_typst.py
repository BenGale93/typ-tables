import polars as pl
from inline_snapshot import external

from typ_tables import TypTable


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
