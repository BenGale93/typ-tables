---
name: typ-tables
description: Use when creating, formatting, styling, or troubleshooting Typst tables with the Python typ-tables library, including TypTable workflows, column and row selectors, locators, formatting methods, raw Typst labels, and generated Typst output.
---

# typ-tables

Use `typ-tables` to turn DataFrame-like data into Typst table markup. The
library is builder-oriented: create a `TypTable`, chain configuration methods,
then call `to_typst()` to get a Typst string.

## Basic Workflow

```python
import polars as pl

from typ_tables import TypTable

df = pl.DataFrame(
    {
        "product": ["Apples", "Bananas", "Pears"],
        "revenue": [1200.5, 950.0, 1432.25],
        "margin": [0.42, 0.38, 0.45],
        "units": [105, 98, 121],
    }
)

typst = (
    TypTable(df, rowname_col="product")
    .tab_header("Sales by Product", subtitle="2026")
    .tab_stubhead("Product")
    .cols_label(revenue="Revenue", margin="Margin", units="Units")
    .fmt_currency(columns="revenue", currency="USD")
    .fmt_percentage(columns="margin", decimals=1)
    .fmt_integer(columns="units")
    .to_typst()
)
```

Write the resulting string to a `.typ` file and include it from Typst:

```typst
#include "table.typ"
```

## Imports

Use the public API unless repository code or docs show a need for internals:

```python
import narwhals as nw
from narwhals import selectors as ncs

from typ_tables import Sides, TypTable, Typst, locators, style
```

`TypTable` accepts eager DataFrame-like objects supported by Narwhals, such as
Polars or pandas. Use `rowname_col=` for row labels. Use `groupname_col=` only
when `rowname_col=` is also supplied.

## Column And Row Selection

Many methods accept `columns=` and some accept `rows=`.

- Columns can be selected by source column name, integer position, list, or
  Narwhals selector such as `ncs.numeric()`.
- Rows can be selected by integer position, list of positions, or Narwhals
  expression such as `nw.col("margin") > 0.4`.
- Selectors use source column names, not labels produced by `cols_label()`.
- Row expressions are evaluated against the original data before display
  formatting.

```python
table = (
    TypTable(df, rowname_col="product")
    .fmt_number(columns=ncs.numeric(), decimals=2)
    .fmt_number(columns="revenue", rows=nw.col("margin") > 0.4, decimals=0)
)
```

## Formatting Values

Prefer the specialized `fmt_*` method for the data type:

- `fmt_number()`, `fmt_integer()`, `fmt_percentage()`
- `fmt_currency(currency="USD")`
- `fmt_scientific()`, `fmt_engineering()`, `fmt_bytes()`
- `fmt_date()`, `fmt_time()`, `fmt_datetime()`
- `fmt_tf()` for booleans
- `fmt(f_string="{x}")` for simple custom f-string formatting
- `sub_missing(missing_text="")` for missing-value replacement

Apply formatting before or after labels and styles as convenient; the builder
stores rules and renders them at `to_typst()`.

## Labels, Headers, Footers, And Spanners

Common table structure methods:

- `tab_header(title, subtitle=None)` for title/subtitle.
- `tab_figure(caption=...)` to wrap the table in a Typst figure.
- `with_id("label")` to add an id to the figure.
- `tab_footer(note)` to append footer notes.
- `tab_stubhead(label)` to label the row-label stub column.
- `cols_label({...}, **kwargs)` to set display labels.
- `cols_label_with(fn, columns=None)` to relabel selected columns.
- `cols_hide(columns)` to omit columns from output while keeping them usable in selectors.
- `cols_align(align, columns=None)` for column label and body alignment.
- `cols_move(columns, after="column_name")` to reorder visible table columns.
- `tab_spanner(label, columns=[...], id_=...)` for grouped column headers.
- `tab_spanner(label, spanners=[...])` to build a higher-level spanner.
- `tab_spanner_delim(delim=".")` to derive spanners from delimited column names.

Set `gather=False` on `tab_spanner()` when preserving column order matters.
Set `id_` when duplicate spanner labels are needed or later spanner references
must be unambiguous.

## Styling

Use `tab_style(locator=..., text=..., cell=...)`. Locators choose the table
region; `TextStyle` affects rendered content and `CellStyle` affects the table
cell container.

```python
table = (
    TypTable(df, rowname_col="product")
    .tab_style(
        locator=locators.LocBody(columns=ncs.numeric()),
        cell=style.CellStyle(align="right"),
    )
    .tab_style(
        locator=locators.LocBody(rows=nw.col("margin") > 0.4),
        text=style.TextStyle(weight="bold"),
        cell=style.CellStyle(fill="rgb(240, 248, 255)"),
    )
)
```

Useful locators:

- `LocHeader()` for title/subtitle.
- `LocColumnLabels(columns=None)` for column labels.
- `LocBody(columns=None, rows=None)` for data cells.
- `LocStub(rows=None)` for row labels.
- `LocStubhead()` for the stub head.
- `LocRowGroup(group=None)` for row-group labels.
- `LocSpanner(spanner_ids=None)` for spanner cells.
- `LocFooter()` for footer notes.

Style values are Typst-compatible strings, for example `"right"`,
`"rgb(240, 248, 255)"`, `"0.6pt + gray"`, or `"10pt"`. For body and stub
locators, style fields can also be lists or Narwhals expressions. Single-region
locators, such as `LocHeader()` and `LocStubhead()`, need scalar style values.

Use `Sides(...)` for side-specific inset or stroke values:

```python
table = (
    TypTable(df)
    .set_table_inset(Sides(x="8pt", y="4pt"))
    .tab_style(
        locator=locators.LocHeader(),
        cell=style.CellStyle(stroke=Sides(bottom="0.8pt + black")),
    )
)
```

## Raw Typst

Plain strings are escaped. Wrap trusted Typst markup in `Typst` when you want
the markup to pass through:

```python
table = (
    TypTable(df)
    .tab_header(Typst("#strong[Quarterly Results]"))
    .tab_figure(caption=Typst("[#emph[Source:] internal reporting]"))
    .cols_label(revenue=Typst("Revenue #text(size: 0.75em)[USD]"))
)
```

Use `Typst` only for trusted, valid Typst. Invalid raw markup will be emitted as
is and can break Typst compilation.

## Table Options

Use table options for global layout defaults:

```python
table = (
    TypTable(df)
    .set_table_stroke("0.6pt + gray")
    .set_table_inset("3pt")
    .set_gutter(row_gutter="3pt", column_gutter="10pt")
    .tab_options(column_labels_hidden=False)
)
```

Call `clear_defaults()` before applying custom table options when the desired
output should start from Typst's baseline table styling instead of typ-tables'
defaults.

## Debugging And Validation

- Check generated output with `to_typst()` first; it returns a plain string.
- If Typst compilation fails, inspect any `Typst(...)` raw markup and Typst
  strings used in styles, strokes, labels, captions, or patterns.
- If a selector misses a column, use the original DataFrame column name rather
  than the rendered label.
- If row-group output is needed, construct `TypTable(df, rowname_col=..., groupname_col=...)`.
