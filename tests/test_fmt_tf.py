"""Tests for boolean formatting with fmt_tf."""

import polars as pl
import pytest
from inline_snapshot import external

from typ_tables import TypTable


@pytest.mark.parametrize(
    ("args", "result"),
    [
        ({}, external("uuid:default-tf.typ")),
        ({"rows": [0]}, external("uuid:just-top-row-tf.typ")),
        ({"tf_style": "yes-no"}, external("uuid:yes-no-style.typ")),
        ({"tf_style": "up-down"}, external("uuid:up-down-style.typ")),
        ({"tf_style": "check-mark"}, external("uuid:check-mark-style.typ")),
        ({"tf_style": "circles"}, external("uuid:circles-style.typ")),
        ({"tf_style": "squares"}, external("uuid:squares-style.typ")),
        ({"tf_style": "diamonds"}, external("uuid:diamonds-style.typ")),
        ({"tf_style": "arrows"}, external("uuid:arrows-style.typ")),
        ({"tf_style": "triangles"}, external("uuid:triangles-style.typ")),
        ({"tf_style": "triangles-lr"}, external("uuid:triangles-lr-style.typ")),
        ({"pattern": "[{x}]"}, external("uuid:pattern-tf.typ")),
        ({"true_val": "Y", "false_val": "N"}, external("uuid:custom-values.typ")),
        ({"na_val": "N/A"}, external("uuid:na-value.typ")),
        (
            {"true_val": "Y", "false_val": "N", "na_val": "N/A"},
            external("uuid:custom-all-values.typ"),
        ),
    ],
)
def test_fmt_tf(table_check, args, result):
    """Test fmt_tf with various configurations."""
    df = pl.DataFrame(
        {
            "bool": [True, False, True, False, None],
            "other": [1, 2, 3, 4, 5],
        }
    )

    table = TypTable(df).fmt_tf(columns="bool", **args)
    typst_table = table.to_typst()

    assert typst_table == result

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_fmt_tf_multiple_columns(table_check):
    """Test fmt_tf with multiple boolean columns."""
    df = pl.DataFrame(
        {
            "bool1": [True, False, True],
            "bool2": [False, True, False],
            "other": [1, 2, 3],
        }
    )

    table = TypTable(df).fmt_tf(columns=["bool1", "bool2"], tf_style="yes-no")
    typst_table = table.to_typst()

    assert typst_table == external("uuid:multiple-columns-tf.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_fmt_tf_all_boolean_columns(table_check):
    """Test fmt_tf on all boolean columns."""
    df = pl.DataFrame(
        {
            "bool1": [True, False, True],
            "bool2": [False, True, False],
            "bool3": [True, True, False],
        }
    )

    table = TypTable(df).fmt_tf(tf_style="arrows")
    typst_table = table.to_typst()

    assert typst_table == external("uuid:all-boolean-columns-tf.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_fmt_tf_non_boolean_column_raises():
    """Test that fmt_tf raises ValueError for non-boolean values."""
    df = pl.DataFrame(
        {
            "mixed": [True, False, True, None],
        }
    )
    # Manually inject a non-boolean value
    df = df.with_columns(pl.col("mixed").cast(pl.String))
    df = df.with_columns(pl.lit("not_a_bool").alias("mixed"))

    table = TypTable(df).fmt_tf(columns="mixed")

    with pytest.raises(ValueError, match="Expected boolean value or NA"):
        table.to_typst()


def test_fmt_tf_invalid_tf_style():
    """Test that invalid tf_style raises ValueError."""
    df = pl.DataFrame(
        {
            "bool": [True, False],
        }
    )

    table = TypTable(df).fmt_tf(columns="bool", tf_style="invalid-style")  # type: ignore [bad-argument-type]

    with pytest.raises(ValueError, match="Invalid `tf_style`"):
        table.to_typst()


def test_fmt_tf_none_without_na_val(table_check):
    """Test that None values without na_val are handled correctly."""
    df = pl.DataFrame(
        {
            "bool": [True, False, None],
        }
    )

    table = TypTable(df).fmt_tf(columns="bool")
    typst_table = table.to_typst()

    assert typst_table == external("uuid:none-without-na-val.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_fmt_tf_pattern_with_na_val(table_check):
    """Test fmt_tf with pattern and na_val."""
    df = pl.DataFrame(
        {
            "bool": [True, False, None],
        }
    )

    table = TypTable(df).fmt_tf(columns="bool", tf_style="yes-no", pattern="[{x}]", na_val="?")
    typst_table = table.to_typst()

    assert typst_table == external("uuid:pattern-with-na-val.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_fmt_tf_override_true_only(table_check):
    """Test fmt_tf with only true_val override."""
    df = pl.DataFrame(
        {
            "bool": [True, False, True],
        }
    )

    table = TypTable(df).fmt_tf(columns="bool", true_val="PASS")
    typst_table = table.to_typst()

    assert typst_table == external("uuid:override-true-only.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0


def test_fmt_tf_override_false_only(table_check):
    """Test fmt_tf with only false_val override."""
    df = pl.DataFrame(
        {
            "bool": [True, False, True],
        }
    )

    table = TypTable(df).fmt_tf(columns="bool", false_val="FAIL")
    typst_table = table.to_typst()

    assert typst_table == external("uuid:override-false-only.typ")

    warnings = table_check(typst_table)

    assert len(warnings) == 0
