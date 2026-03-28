"""Package for creating Typst Tables from DataFrames."""

import typing as t
from dataclasses import dataclass

import narwhals as nw
from narwhals.typing import IntoDataFrame

from typ_tables import ttypes
from typ_tables.boxhead import Boxhead, ColInfo
from typ_tables.constants import ROW_INDEX
from typ_tables.escape import Typst, escape_value
from typ_tables.formats import Formatter, FString, Numeric, SubMissing, fmt
from typ_tables.location import ColumnSelector, RowSelector, resolve_columns


@dataclass(kw_only=True)
class TypData:
    """Class that holds all the formatters, stylers etc."""

    boxhead: Boxhead
    formats: list[Formatter]
    substitute: list[Formatter]

    @classmethod
    def from_data(cls, df: ttypes.Data) -> t.Self:
        """Initialise based on the given dataset."""
        return cls(boxhead=Boxhead.from_data(df), formats=[], substitute=[])

    def format_df(self, df: ttypes.Data) -> ttypes.Data:
        """Format the given dataset."""
        new_df = df
        for f in self.formats:
            new_df = f.fmt(new_df)
        for f in self.substitute:
            new_df = f.fmt(new_df)
        return new_df

    def alignment(self, columns: list[ColInfo]) -> str:
        """Returns the alignment of each column."""
        alignment_elements = [col.column_align for col in columns]
        joined_alignments = ", ".join(alignment_elements)
        return f"({joined_alignments})"

    def columns(self, columns: list[ColInfo]) -> str:
        """Return the width of the columns."""
        return str(len(columns))

    def header(self, columns: list[ColInfo]) -> str:
        """Returns the header element."""
        header = ", ".join(f"[{col.name}]" for col in columns)
        return f"table.header(\n    {header}\n  )"

    def body(self, data: ttypes.Data, columns: list[ColInfo]) -> str:
        """Returns the body of the table."""
        rows = []
        for row_content in data.iter_rows(named=True):
            desired_content = [row_content[col.var] for col in columns]
            row = " ".join(f"[{escape_value(content)}]," for content in desired_content)
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

    final_columns = typ.boxhead.final_columns()

    columns = typ.columns(final_columns)
    alignment = typ.alignment(final_columns)
    header = typ.header(final_columns)
    body = typ.body(data, final_columns)

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
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        missing_text: str = "",
    ) -> t.Self:
        """Substitutes Null and NaN values with the given missing text."""
        self._typ_data.substitute.append(fmt(self._df, SubMissing(missing_text=missing_text), columns, rows))
        return self

    def fmt(
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        f_string: str,
    ) -> t.Self:
        """Set a column format with a narwhals style f-string.

        Note:
            Currently only accepts 1 placeholder.
        """
        self._typ_data.formats.append(fmt(self._df, FString(f_string), columns, rows))
        return self

    def fmt_number(  # noqa: PLR0913
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        decimals: int = 2,
        n_sigfig: int | None = None,
        drop_trailing_zeros: bool = False,
        drop_trailing_dec_mark: bool = True,
        use_seps: bool = True,
        accounting: bool = False,
        scale_by: float = 1,
        compact: bool = False,
        pattern: str = "{x}",
        dec_mark: str = ".",
        sep_mark: str = ",",
        force_sign: bool = False,
    ) -> t.Self:
        """Format numeric values."""
        self._typ_data.formats.append(
            fmt(
                self._df,
                Numeric(
                    decimals=decimals,
                    n_sigfig=n_sigfig,
                    drop_trailing_zeros=drop_trailing_zeros,
                    drop_trailing_dec_mark=drop_trailing_dec_mark,
                    use_seps=use_seps,
                    accounting=accounting,
                    scale_by=scale_by,
                    compact=compact,
                    pattern=pattern,
                    dec_mark=dec_mark,
                    sep_mark=sep_mark,
                    force_sign=force_sign,
                ),
                columns,
                rows,
            )
        )
        return self

    def cols_align(self, align: ttypes.Alignment = "left", columns: ColumnSelector | None = None) -> t.Self:
        """Align the columns to the given direction."""
        columns_to_align = resolve_columns(self._df, columns)
        self._typ_data.boxhead.set_cols_align(columns_to_align, align)
        return self

    def cols_hide(self, columns: ColumnSelector | None = None) -> t.Self:
        """Hide the columns in the final table."""
        columns_to_hide = resolve_columns(self._df, columns)
        self._typ_data.boxhead.set_cols_hidden(columns_to_hide)
        return self

    def cols_label(self, cases: dict[str, str | Typst] | None = None, **kwargs: str | Typst) -> t.Self:
        """Relabel one or more columns."""
        cases = cases | kwargs if cases else kwargs
        self._typ_data.boxhead.set_cols_label(cases)
        return self

    def cols_label_with(self, fn: t.Callable[[str], str | Typst], columns: ColumnSelector | None = None) -> t.Self:
        """Relabel one or more columns using a function."""
        columns_to_relabel = resolve_columns(self._df, columns)
        new_labels = {col: fn(col) for col in columns_to_relabel}
        self._typ_data.boxhead.set_cols_label(new_labels)
        return self
