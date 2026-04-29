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
            "integer": [
                0,
                100,
                1,
                113525,
                10000000,
                100000000000000000,
                993383853,
                None,
                -10,
                -1,
                -0,
                -10000000,
                -868238,
                -342523532,
                None,
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


def test_string_column_fmt_numeric_and_integer(table_check):
    df = pl.DataFrame(
        {
            "string": ["stuff", "more_stuff"],
            "other_string": ["stuff", "more_stuff"],
        }
    )

    table = TypTable(df).fmt_number(columns="string").fmt_integer(columns="other_string")
    typst_table = table.to_typst()

    assert typst_table == external("uuid:fc51b5f6-3c07-4def-b65e-e8c8d0c195bb.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({}, external("uuid:default-integer.typ")),
        ({"rows": [0]}, external("uuid:just-top-row-int.typ")),
        ({"use_seps": False}, external("uuid:no-separators-int.typ")),
        ({"accounting": True}, external("uuid:accounting-int.typ")),
        ({"scale_by": 10}, external("uuid:scale-by-ten-int.typ")),
        ({"compact": True}, external("uuid:compact-numbers-int.typ")),
        ({"pattern": "${x}"}, external("uuid:dollar-pattern-int.typ")),
        ({"force_sign": True}, external("uuid:force-sign-symbol-int.typ")),
    ],
)
def test_integer(table_check, args, result):
    df = pl.DataFrame(
        {
            "float": [
                0.0,
                100.0000001,
                1.69,
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
            "integer": [
                0,
                100,
                1,
                113525,
                10000000,
                100000000000000000,
                993383853,
                None,
                -10,
                -1,
                -0,
                -10000000,
                -868238,
                -342523532,
                None,
            ],
        }
    )

    table = TypTable(df).fmt_integer(**args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({}, external("uuid:default-percentage.typ")),
        ({"rows": [0]}, external("uuid:just-top-row-perc.typ")),
        ({"decimals": 5}, external("uuid:five-decimals-perc.typ")),
        ({"drop_trailing_zeros": True}, external("uuid:drop-trailing-zeros-perc.typ")),
        (
            {"drop_trailing_dec_mark": False, "decimals": 0},
            external("uuid:drop-trailing-dec-mark-perc.typ"),
        ),
        ({"use_seps": False}, external("uuid:no-separators-perc.typ")),
        ({"accounting": True}, external("uuid:accounting-floats-perc.typ")),
        ({"scale_values": True}, external("uuid:scale-values.typ")),
        ({"pattern": "${x}"}, external("uuid:dollar-pattern-perc.typ")),
        ({"dec_mark": ",", "sep_mark": "."}, external("uuid:use-different-marks-perc.typ")),
        ({"force_sign": True}, external("uuid:force-sign-symbol-perc.typ")),
        ({"placement": "left"}, external("uuid:placement-left.typ")),
        ({"incl_space": True}, external("uuid:include-space.typ")),
        ({"force_sign": True, "placement": "left"}, external("uuid:force-sign-and-placement.typ")),
    ],
)
def test_percentage(table_check, args, result):
    df = pl.DataFrame(
        {
            "float": [
                0.0,
                100.0000001,
                1.69,
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

    table = TypTable(df).fmt_percentage(**args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({}, external("uuid:default-scientific.typ")),
        ({"rows": [0]}, external("uuid:just-top-row-sci.typ")),
        ({"decimals": 5}, external("uuid:five-decimals-sci.typ")),
        ({"n_sigfig": 3}, external("uuid:three-sigfig-sci.typ")),
        ({"drop_trailing_zeros": True}, external("uuid:drop-trailing-zeros-sci.typ")),
        (
            {"drop_trailing_dec_mark": False, "decimals": 0},
            external("uuid:drop-trailing-dec-mark-sci.typ"),
        ),
        ({"scale_by": 10}, external("uuid:scale-by-ten-sci.typ")),
        ({"pattern": "${x}"}, external("uuid:dollar-pattern-sci.typ")),
        ({"dec_mark": ",", "sep_mark": "."}, external("uuid:use-different-marks-sci.typ")),
        ({"force_sign_m": True, "force_sign_n": True}, external("uuid:force-sign-sci.typ")),
    ],
)
def test_scientific(table_check, args, result):
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
            "integer": [
                0,
                100,
                1,
                113525,
                10000000,
                100000000000000000,
                993383853,
                None,
                -10,
                -1,
                -0,
                -10000000,
                -868238,
                -342523532,
                None,
            ],
        }
    )

    table = TypTable(df).fmt_scientific(**args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({}, external("uuid:default-engineering.typ")),
        ({"rows": [0]}, external("uuid:just-top-row-eng.typ")),
        ({"decimals": 5}, external("uuid:five-decimals-eng.typ")),
        ({"n_sigfig": 3}, external("uuid:three-sigfig-eng.typ")),
        ({"drop_trailing_zeros": True}, external("uuid:drop-trailing-zeros-eng.typ")),
        (
            {"drop_trailing_dec_mark": False, "decimals": 0},
            external("uuid:drop-trailing-dec-mark-eng.typ"),
        ),
        ({"scale_by": 10}, external("uuid:scale-by-ten-eng.typ")),
        ({"pattern": "${x}"}, external("uuid:dollar-pattern-eng.typ")),
        ({"dec_mark": ",", "sep_mark": "."}, external("uuid:use-different-marks-eng.typ")),
        ({"force_sign_m": True, "force_sign_n": True}, external("uuid:force-sign-eng.typ")),
    ],
)
def test_engineering(table_check, args, result):
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
            "integer": [
                0,
                100,
                1,
                113525,
                10000000,
                100000000000000000,
                993383853,
                None,
                -10,
                -1,
                -0,
                -10000000,
                -868238,
                -342523532,
                None,
            ],
        }
    )

    table = TypTable(df).fmt_engineering(**args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({"currency": "USD"}, external("uuid:default-usd.typ")),
        ({"currency": "GBP"}, external("uuid:default-gbp.typ")),
        ({"currency": "USD", "rows": [0]}, external("uuid:just-top-row-currency.typ")),
        ({"currency": "USD", "decimals": 5}, external("uuid:five-decimals-currency.typ")),
        (
            {"currency": "USD", "drop_trailing_dec_mark": False, "decimals": 0},
            external("uuid:drop-trailing-dec-mark-currency.typ"),
        ),
        ({"currency": "USD", "use_seps": False}, external("uuid:no-separators-currency.typ")),
        ({"currency": "USD", "accounting": True}, external("uuid:accounting-floats-currency.typ")),
        ({"currency": "EUR", "compact": True}, external("uuid:compact-euros.typ")),
        ({"currency": "USD", "scale_by": 10}, external("uuid:scale-by-10-currency.typ")),
        ({"currency": "USD", "pattern": "${x}"}, external("uuid:dollar-pattern-currency.typ")),
        (
            {"currency": "USD", "dec_mark": ",", "sep_mark": "."},
            external("uuid:use-different-marks-currency.typ"),
        ),
        ({"currency": "USD", "force_sign": True}, external("uuid:force-sign-symbol-currency.typ")),
        ({"currency": "USD", "placement": "right"}, external("uuid:placement-currency.typ")),
        ({"currency": "USD", "incl_space": True}, external("uuid:include-currency.typ")),
        (
            {"currency": "USD", "force_sign": True, "placement": "right"},
            external("uuid:force-sign-and-currency.typ"),
        ),
    ],
)
def test_currency(table_check, args, result):
    df = pl.DataFrame(
        {
            "float": [
                0.0,
                100.0000001,
                1.69,
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

    table = TypTable(df).fmt_currency(**args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_currency_bad_code():
    df = pl.DataFrame({"test": [10]})

    table = TypTable(df).fmt_currency(currency="TST")

    with pytest.raises(ValueError, match=r"'TST' is not a recognised"):
        table.to_typst()


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({}, external("uuid:default-bytes.typ")),
        ({"rows": [0]}, external("uuid:just-top-row-bytes.typ")),
        ({"decimals": 5}, external("uuid:five-decimals-bytes.typ")),
        ({"n_sigfig": 3}, external("uuid:three-sigfig-bytes.typ")),
        ({"drop_trailing_zeros": True}, external("uuid:drop-trailing-zeros-bytes.typ")),
        (
            {"drop_trailing_dec_mark": False, "decimals": 0},
            external("uuid:drop-trailing-dec-mark-bytes.typ"),
        ),
        ({"use_seps": False}, external("uuid:no-separators-bytes.typ")),
        ({"pattern": "${x}"}, external("uuid:dollar-pattern-bytes.typ")),
        ({"dec_mark": ",", "sep_mark": "."}, external("uuid:use-different-marks-bytes.typ")),
        ({"force_sign": True}, external("uuid:force-sign-symbol-bytes.typ")),
        ({"standard": "binary"}, external("uuid:binary-standard.typ")),
        ({"incl_space": False}, external("uuid:no-space-bytes.typ")),
        ({"standard": "binary", "decimals": 2}, external("uuid:binary-two-decimals.typ")),
    ],
)
def test_bytes(table_check, args, result):
    df = pl.DataFrame(
        {
            "bytes": [
                0,
                100,
                1000,
                1024,
                1000000,
                1048576,
                1000000000,
                1073741824,
                1000000000000,
                1099511627776,
                None,
                -100,
                -1000,
                -1048576,
            ],
        }
    )

    table = TypTable(df).fmt_bytes(**args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_bytes_special_values(table_check):
    """Test bytes formatter with inf, -inf, and nan values."""
    df = pl.DataFrame(
        {
            "bytes": [
                float("inf"),
                float("-inf"),
                float("nan"),
                1000.0,
            ],
        }
    )

    table = TypTable(df).fmt_bytes()
    typst_table = table.to_typst()

    assert typst_table == external("uuid:bytes-special-values.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0
