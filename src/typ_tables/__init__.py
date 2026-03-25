"""Package for creating Typst Tables from DataFrames."""

import typing as t
from dataclasses import dataclass

import narwhals as nw
from narwhals.typing import IntoDataFrame

from typ_tables import ttypes
from typ_tables.constants import ROW_INDEX
from typ_tables.escape import escape_value
from typ_tables.formats import Formatter, FString, SubMissing, fmt
from typ_tables.location import ColumnSelector, RowSelector, resolve_columns


@dataclass(kw_only=True)
class TypData:
    """Class that holds all the formatters, stylers etc."""

    align: dict[str, ttypes.Auto | ttypes.Alignment]
    formats: list[Formatter]
    substitute: list[Formatter]

    @classmethod
    def from_data(cls, _df: ttypes.Data) -> t.Self:
        """Initialise based on the given dataset."""
        return cls(align={}, formats=[], substitute=[])

    def format_df(self, df: ttypes.Data) -> ttypes.Data:
        """Format the given dataset."""
        new_df = df
        for f in self.formats:
            new_df = f.fmt(new_df)
        for f in self.substitute:
            new_df = f.fmt(new_df)
        return new_df

    def alignment(self, columns: list[str]) -> str:
        """Returns the alignment of each column."""
        alignment_elements = [self.align.get(col, "auto") for col in columns]
        joined_alignments = ", ".join(alignment_elements)
        return f"({joined_alignments})"

    def columns(self, columns: list[str]) -> str:
        """Return the width of the columns."""
        return str(len(columns))

    def header(self, columns: list[str]) -> str:
        """Returns the header element."""
        header = ", ".join(f"[{escape_value(name)}]" for name in columns)
        return f"table.header(\n    {header}\n  )"

    def body(self, data: ttypes.Data) -> str:
        """Returns the body of the table."""
        rows = []
        for row_content in data.iter_rows():
            row = " ".join(f"[{escape_value(content)}]," for content in row_content)
            rows.append(row)

        return "\n  ".join(rows)


@dataclass
class TableElements:
    """Container class for the elements of a Typst table."""

    columns: str
    alignment: str
    header: str
    body: str


def create_elements(original_data: ttypes.Data, typ: TypData) -> TableElements:
    """Creates the elements of the Typst table."""
    data = typ.format_df(original_data).drop(ROW_INDEX)

    columns = typ.columns(data.columns)
    alignment = typ.alignment(data.columns)
    header = typ.header(data.columns)
    body = typ.body(data)

    return TableElements(
        columns=columns,
        alignment=alignment,
        header=header,
        body=body,
    )


class TypTable:
    """A Table to format into a Typst table."""

    def __init__(self, df: IntoDataFrame) -> None:
        """Initialise with the DataFrame to visualise as a typst table.."""
        self._df = nw.from_native(df, eager_only=True).with_row_index(ROW_INDEX)
        self._typ_data = TypData.from_data(self._df)

    def to_typst(self) -> str:
        """Convert the table to a Typst string."""
        typ_element = create_elements(self._df, self._typ_data)

        return f"""#table(
  columns: {typ_element.columns},
  align: {typ_element.alignment},
  {typ_element.header},
  {typ_element.body}
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

    def cols_align(self, align: ttypes.Alignment = "left", columns: ColumnSelector | None = None) -> t.Self:
        for col in resolve_columns(self._df, columns):
            self._typ_data.align[col] = align
        return self
