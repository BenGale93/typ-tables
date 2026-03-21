"""Package for creating Typst Tables from DataFrames."""

import re

import narwhals as nw
from narwhals.typing import IntoDataFrame

ESCAPE_PATTERN = re.compile(r"([\\#*_`$<>@\[\]=+\-/~])")


def _escape(value: object) -> str:
    """Escape special characters."""
    if not isinstance(value, str):
        return str(value)

    return ESCAPE_PATTERN.sub(r"\\\1", value)


class TypTable:
    """A Table to format into a Typst table."""

    def __init__(self, df: IntoDataFrame) -> None:
        """Initialise with the DataFrame to visualise as a typst table.."""
        self._df = nw.from_native(df, eager_only=True)

    def to_typst(self) -> str:
        """Convert the table to a Typst string."""
        num_columns = len(self._df.columns)
        header = ", ".join(f"[{_escape(name)}]" for name in self._df.columns)
        rows = []
        for row_content in self._df.iter_rows():
            row = " ".join(f"[{_escape(content)}]," for content in row_content)
            rows.append(row)

        row_str = "\n  ".join(rows)
        return f"""#table(
  columns: {num_columns},
  table.header(
    {header}
  ),
  {row_str}
)
"""
