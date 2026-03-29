import polars as pl
import pytest
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

    def test_to_typst_format_float_with_missing(self, table_check, basic_data) -> None:
        table = TypTable(basic_data).fmt_number().sub_missing(missing_text="Missing")
        result = table.to_typst()

        assert result == external("uuid:f7450830-7a1b-440f-bc59-221a534372a5.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

        from_pandas_table = (
            TypTable(basic_data.to_pandas()).fmt_number().sub_missing(missing_text="Missing")
        )
        pandas_result = from_pandas_table.to_typst()

        assert pandas_result == external("uuid:4e42ced7-d53a-44bc-b9e2-266b334abed2.typ")

        warnings = table_check(pandas_result)

        assert len(warnings) == 0


class TestFString:
    def test_add_text(self, table_check):
        df = pl.DataFrame(
            {
                "string": ["a", "b", "c", None],
                "int": [10, 10000, 1000000, None],
            }
        )

        table = TypTable(df).fmt(f_string="^{}*", columns="string")
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

        table = TypTable(df).fmt(f_string="^{}*", columns="string").fmt(f_string="_{}_")
        result = table.to_typst()

        assert result == external("uuid:ca688b19-cd8a-442a-9fcc-94b32eff3b79.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({}, external("uuid:default-numeric.typ")),
        ({"rows": [0]}, external("uuid:just-top-row.typ")),
        ({"decimals": 5}, external("uuid:five-decimals.typ")),
        ({"n_sigfig": 3}, external("uuid:three-sigfig.typ")),
        ({"drop_trailing_zeros": True}, external("uuid:drop-trailing-zeros.typ")),
        (
            {"drop_trailing_dec_mark": False, "decimals": 0},
            external("uuid:drop-trailing-dec-mark.typ"),
        ),
        ({"use_seps": False}, external("uuid:no-separators.typ")),
        ({"accounting": True}, external("uuid:accounting-floats.typ")),
        ({"scale_by": 10}, external("uuid:scale-by-ten.typ")),
        ({"compact": True}, external("uuid:compact-numbers.typ")),
        ({"pattern": "${x}"}, external("uuid:dollar-pattern.typ")),
        ({"dec_mark": ",", "sep_mark": "."}, external("uuid:use-different-marks.typ")),
        ({"force_sign": True}, external("uuid:force-sign-symbol.typ")),
        ({"compact": True, "n_sigfig": 3}, external("uuid:compact-sigfigs.typ")),
        ({"use_seps": False, "n_sigfig": 3}, external("uuid:no-seps-sigfigs.typ")),
    ],
)
def test_numeric(table_check, args, result):
    df = pl.DataFrame(
        {
            "float": [
                0.0,
                100.0000001,
                1.3572354,
                1.0,
                10000000,
                1e20,
                0.0005009,
                None,
                -10.0000001,
                -1.3572354,
                -1.0,
                -10000000,
                float("NaN"),
                float("inf"),
                float("-inf"),
            ],
        }
    )

    table = TypTable(df).fmt_number(**args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_numeric_string_column(table_check):
    df = pl.DataFrame({"string": ["stuff", "1.2653"]})

    table = TypTable(df).fmt_number()
    typst_table = table.to_typst()

    assert typst_table == external("uuid:38852fc1-fc60-42d1-b559-054d076d00dc.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0
