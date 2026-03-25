"""Package for creating Typst Tables from DataFrames."""

import typing as t
from dataclasses import dataclass

import narwhals as nw
from narwhals.typing import IntoDataFrame

from typ_tables import ttypes
from typ_tables.constants import ROW_INDEX
from typ_tables.escape import escape_value
from typ_tables.formats import Formatter, FString, SubMissing, fmt
from typ_tables.location import ColumnSelector, RowSelector


@dataclass(kw_only=True)
class TypData:
    """Class that holds all the formatters, stylers etc."""

    formats: list[Formatter]
    substitute: list[Formatter]

    @classmethod
    def from_data(cls, _df: ttypes.Data) -> t.Self:
        """Initialise based on the given dataset."""
        return cls(formats=[], substitute=[])

    def format_df(self, df: ttypes.Data) -> ttypes.Data:
        """Format the given dataset."""
        new_df = df
        for f in self.formats:
            new_df = f.fmt(new_df)
        for f in self.substitute:
            new_df = f.fmt(new_df)
        return new_df


class TypTable:
    """A Table to format into a Typst table."""

    def __init__(self, df: IntoDataFrame) -> None:
        """Initialise with the DataFrame to visualise as a typst table.."""
        self._df = nw.from_native(df, eager_only=True).with_row_index(ROW_INDEX)
        self._typ_data = TypData.from_data(self._df)

    def to_typst(self) -> str:
        """Convert the table to a Typst string."""
        new_df = self._typ_data.format_df(self._df).drop(ROW_INDEX)
        num_columns = len(new_df.columns)
        header = ", ".join(f"[{escape_value(name)}]" for name in new_df.columns)
        rows = []
        for row_content in new_df.iter_rows():
            row = " ".join(f"[{escape_value(content)}]," for content in row_content)
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

    def sub_missing(
        self, missing_text: str = "", columns: ColumnSelector | None = None, rows: RowSelector | None = None
    ) -> t.Self:
        """Substitutes Null and NaN values with the given missing text."""
        self._typ_data.substitute.append(fmt(self._df, SubMissing(missing_text=missing_text), columns, rows))
        return self

    def fmt(self, f_string: str, columns: ColumnSelector | None = None, rows: RowSelector | None = None) -> t.Self:
        """Set a column format with a narwhals style f-string.

        Note:
            Currently only accepts 1 placeholder.
        """
        self._typ_data.formats.append(fmt(self._df, FString(f_string), columns, rows))
        return self
