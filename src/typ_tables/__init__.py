"""Package for creating Typst Tables from DataFrames."""

import typing as t
from dataclasses import dataclass
from functools import cached_property
from string import Template
from textwrap import indent

import narwhals as nw
from narwhals.typing import IntoDataFrame

from typ_tables import ttypes
from typ_tables.boxhead import Boxhead, ColInfo
from typ_tables.constants import ROW_INDEX
from typ_tables.escape import Typst, escape_value
from typ_tables.formats import Formatter, FString, Numeric, SubMissing, fmt
from typ_tables.location import ColumnSelector, RowSelector, resolve_columns

HEADER_STROKE = "1.2pt"

TITLE_TEMPLATE = Template(
    f"""table.hline(stroke: {HEADER_STROKE}),
    table.header(
    table.cell(
      colspan: $n_col,
      align: center,
      [
        == $title_contents
      ]
    )
  ),
  table.hline(stroke: {HEADER_STROKE}),
  """
)


@dataclass(frozen=True)
class Heading:
    """Container class that holds the title and subtitle."""

    _title: str | Typst | None = None
    _subtitle: str | Typst | None = None

    @cached_property
    def title(self) -> str | Typst | None:
        """The escaped title text."""
        if self._title is None:
            return self._title
        return escape_value(self._title)

    @cached_property
    def subtitle(self) -> str | Typst | None:
        """The escaped subtitle text."""
        if self._subtitle is None:
            return self._subtitle
        return escape_value(self._subtitle)

    def to_typst(self, n_col: int) -> str:
        """Converts the heading into a Typst table header block."""
        if not self.title:
            return ""
        if not self.subtitle:
            title_contents = self.title
        else:
            title_contents = f"{self.title} \\\n        {self.subtitle}"

        return TITLE_TEMPLATE.substitute(n_col=n_col, title_contents=title_contents)


@dataclass(frozen=True)
class Figure:
    """Container class that holds the figure arguments."""

    _caption: str | Typst | None = None

    @cached_property
    def caption(self) -> str | Typst | None:
        """The escaped subtitle text."""
        if self._caption is None:
            return self._caption
        return escape_value(self._caption)

    def add_figure_args(self, table_str: str) -> str:
        """Adds a figure wrapper to the table string, if required."""
        if caption := self.caption:
            table_str = table_str.removeprefix("#")
            table_str = indent(table_str, "  ").rstrip()
            table_str = f"#figure(\n{table_str},\n  caption: [{caption}],\n)"

        return table_str


@dataclass(kw_only=True)
class TypData:
    """Class that holds all the formatters, stylers etc."""

    boxhead: Boxhead
    formats: list[Formatter]
    substitute: list[Formatter]
    heading: Heading
    figure: Figure

    @classmethod
    def from_data(cls, df: ttypes.Data) -> t.Self:
        """Initialise based on the given dataset."""
        return cls(
            boxhead=Boxhead.from_data(df),
            formats=[],
            substitute=[],
            heading=Heading(),
            figure=Figure(),
        )

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
        n_col = len(columns)

        formatted_title = self.heading.to_typst(n_col)

        return (
            f"{formatted_title}table.header(\n    {header}\n  ),"
            f"\ntable.hline(stroke: {HEADER_STROKE})"
        )

    def body(self, data: ttypes.Data, columns: list[ColInfo]) -> str:
        """Returns the body of the table."""
        rows = []
        for row_content in data.iter_rows(named=True):
            desired_content = [row_content[col.var] for col in columns]
            row = " ".join(f"[{escape_value(content)}]," for content in desired_content)
            rows.extend((row, "table.hline(stroke: 0.6pt),"))

        return "\n  ".join(rows)


TABLE_TEMPLATE = Template("""#table(
  columns: $columns,
  stroke: none,
  align: $alignment,
  $header,
  $body
)
""")


def create_table_string(original_data: ttypes.Data, typ: TypData) -> str:
    """Creates the final Typst table."""
    data = typ.format_df(original_data).drop(ROW_INDEX)

    final_columns = typ.boxhead.final_columns()

    columns = typ.columns(final_columns)
    alignment = typ.alignment(final_columns)
    header = typ.header(final_columns)
    body = typ.body(data, final_columns)

    table_str = TABLE_TEMPLATE.substitute(
        columns=columns,
        alignment=alignment,
        header=header,
        body=body,
    )
    return typ.figure.add_figure_args(table_str)


class TypTable:
    """A Table to format into a Typst table."""

    def __init__(self, df: IntoDataFrame) -> None:
        """Initialise with the DataFrame to visualise as a typst table.."""
        self._df = nw.from_native(df, eager_only=True).with_row_index(ROW_INDEX)
        self._typ_data = TypData.from_data(self._df)

    def to_typst(self) -> str:
        """Convert the table to a Typst string."""
        return create_table_string(self._df, self._typ_data)

    # Modifying parts of a Table Methods ----
    def tab_header(self, title: str | Typst, subtitle: str | Typst | None = None) -> t.Self:
        """Add a table header."""
        self._typ_data.heading = Heading(title, subtitle)
        return self

    def tab_figure(self, caption: str | Typst | None = None) -> t.Self:
        """Add a figure wrapper."""
        self._typ_data.figure = Figure(caption)
        return self

    # Formatting Methods ----
    def sub_missing(
        self,
        columns: ColumnSelector | None = None,
        rows: RowSelector | None = None,
        *,
        missing_text: str = "",
    ) -> t.Self:
        """Substitutes Null and NaN values with the given missing text."""
        self._typ_data.substitute.append(
            fmt(self._df, SubMissing(missing_text=missing_text), columns, rows)
        )
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

    # Modifying Columns Methods ----
    def cols_align(
        self, align: ttypes.Alignment = "left", columns: ColumnSelector | None = None
    ) -> t.Self:
        """Align the columns to the given direction."""
        columns_to_align = resolve_columns(self._df, columns)
        self._typ_data.boxhead.set_cols_align(columns_to_align, align)
        return self

    def cols_hide(self, columns: ColumnSelector | None = None) -> t.Self:
        """Hide the columns in the final table."""
        columns_to_hide = resolve_columns(self._df, columns)
        self._typ_data.boxhead.set_cols_hidden(columns_to_hide)
        return self

    def cols_label(
        self, cases: dict[str, str | Typst] | None = None, **kwargs: str | Typst
    ) -> t.Self:
        """Relabel one or more columns."""
        cases = cases | kwargs if cases else kwargs
        self._typ_data.boxhead.set_cols_label(cases)
        return self

    def cols_label_with(
        self, fn: t.Callable[[str], str | Typst], columns: ColumnSelector | None = None
    ) -> t.Self:
        """Relabel one or more columns using a function."""
        columns_to_relabel = resolve_columns(self._df, columns)
        new_labels = {col: fn(col) for col in columns_to_relabel}
        self._typ_data.boxhead.set_cols_label(new_labels)
        return self
