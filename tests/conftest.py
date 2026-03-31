import typing as t
from pathlib import Path

import polars as pl
import pytest
import typst
from inline_snapshot import Format, TextDiff, register_format
from typst import TypstWarning


@register_format
class TypstFormat(TextDiff, Format[str]):
    "Stores strings in `.typ` files."

    suffix = ".typ"
    priority = 10

    def is_format_for(self, value: object) -> bool:
        return isinstance(value, str)

    def encode(self, value: str, path: Path) -> None:
        with path.open("w", encoding="utf-8", newline="\n") as f:
            f.write(value)

    def decode(self, path: Path) -> str:
        with path.open("r", encoding="utf-8", newline="\n") as f:
            return f.read()


@pytest.fixture
def table_check(
    tmp_path: Path, request: pytest.FixtureRequest
) -> t.Callable[[str], list[TypstWarning]]:
    def compile_with_warnings(result: str) -> list[TypstWarning]:
        pdf_bytes, warnings = typst.compile_with_warnings(result.encode())

        (tmp_path / f"{request.node.name}.pdf").write_bytes(pdf_bytes)

        return warnings

    return compile_with_warnings


@pytest.fixture
def basic_data() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "string": ["a", "b", "c", "random-letters", None],
            "int": [10, 10000, 1000000, 568282638583, None],
            "float": [float("NaN"), 0.000001, 0.1368753, 163985.8374, None],
        }
    )


@pytest.fixture
def group_data() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "group": ["group_a", "group_b", "group_a", "group_b"],
            "fruit": ["apple", "pear", "banana", "kiwi"],
            "count": [10, 73, 3, 477],
        }
    )
