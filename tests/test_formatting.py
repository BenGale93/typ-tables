import polars as pl
from inline_snapshot import external
from narwhals import selectors as ncs

from typ_tables import TypTable


class TestSubMissing:
    def test_to_typst_string_int_float_with_missing(self, table_check, basic_data) -> None:
        table = TypTable(basic_data).sub_missing(missing_text="Missing")
        result = table.to_typst()

        assert result == external("uuid:e8d0edad-ae47-441a-940a-82555cbed295.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_to_typst_missing_two_variants(self, table_check, basic_data) -> None:
        table = (
            TypTable(basic_data)
            .sub_missing(missing_text="Missing", columns=ncs.numeric())
            .sub_missing(missing_text="-", columns="string")
        )
        result = table.to_typst()

        assert result == external("uuid:6ca1530f-c719-4a20-becf-0fb230fe14ec.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestFString:
    def test_add_text(self, table_check):
        df = pl.DataFrame(
            {
                "string": ["a", "b", "c", None],
                "int": [10, 10000, 1000000, None],
            }
        )

        table = TypTable(df).fmt("^{}*", columns="string")
        result = table.to_typst()

        assert result == external("uuid:38194acd-2a5c-49dc-950b-86b6defddd49.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_add_text_twice(self, table_check):
        df = pl.DataFrame(
            {
                "string": ["a", "b", "c", None],
                "int": [10, 10000, 1000000, None],
            }
        )

        table = TypTable(df).fmt("^{}*", columns="string").fmt("_{}_")
        result = table.to_typst()

        assert result == external("uuid:ca688b19-cd8a-442a-9fcc-94b32eff3b79.typ")

        warnings = table_check(result)

        assert len(warnings) == 0
