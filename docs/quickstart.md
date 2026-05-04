# Quickstart

`TypTable` builds Typst table markup from DataFrame-like data. The usual
workflow is:

1. Create a `TypTable` from your data.
2. Add labels, formatting, styling, and table options with chained method calls.
3. Call `to_typst()` to render the final Typst string.

Most configuration methods return the current table instance, so calls can be
chained fluently.

## Basic Table

```python
import polars as pl

from typ_tables import TypTable


df = pl.DataFrame(
    {
        "product": ["Apples", "Bananas", "Pears"],
        "region": ["North", "South", "North"],
        "revenue": [1200.5, 950.0, 1432.25],
        "margin": [0.42, 0.38, 0.45],
        "units": [105, 98, 121],
    }
)

typst = (
    TypTable(df, rowname_col="product")
    .tab_header("Sales by Product", subtitle="2026")
    .tab_stubhead("Product")
    .cols_label(
        revenue="Revenue",
        margin="Margin",
        units="Units",
    )
    .fmt_currency(columns="revenue", currency="USD")
    .fmt_percentage(columns="margin", decimals=1)
    .fmt_integer(columns="units")
    .to_typst()
)
```

`typst` is a string containing Typst markup. Write it to a `.typ` file and
include that file from your Typst document.

```typst
#include "table.typ"
```

## Selecting Columns

Many methods accept a `columns` argument. You can select columns by name, index,
list, or Narwhals selector.

```python
from narwhals import selectors as ncs

from typ_tables import TypTable, locators, style


table = TypTable(df, rowname_col="product")

# Select one column by name.
table = table.fmt_currency(columns="revenue", currency="USD")

# Select multiple columns by name.
table = table.cols_label({"revenue": "Revenue", "margin": "Margin"})

# Select one column by position.
table = table.cols_hide(columns=1)

# Select multiple columns by position.
table = table.fmt_number(columns=[2, 3], decimals=2)

# Select columns by dtype using Narwhals selectors.
table = table.tab_style(
    locator=locators.LocBody(columns=ncs.numeric()),
    cell=style.CellStyle(align="right"),
)
```

Column positions refer to the source data columns. Column labels set with
`cols_label()` do not change the source column names used by selectors.

## Selecting Rows

Formatting and body/stub styling methods can also accept a `rows` argument. You
can select rows by index, a list of indices, or a Narwhals expression.

```python
import narwhals as nw

from typ_tables import TypTable, locators, style


table = TypTable(df, rowname_col="product")

# Select one row by position.
table = table.fmt_number(columns="revenue", rows=0, decimals=0)

# Select multiple rows by position.
table = table.fmt_number(columns="revenue", rows=[0, 2], decimals=0)

# Select rows with a Narwhals expression.
table = table.tab_style(
    locator=locators.LocBody(rows=nw.col("margin") > 0.4),
    text=style.TextStyle(weight="bold"),
)
```

Row selectors are evaluated against the original data. This means you can style
or format based on values before formatting changes how those values are shown.

## Combining Row and Column Selectors

Use both `rows` and `columns` when you want to target specific cells.

```python
import narwhals as nw

from typ_tables import TypTable, locators, style


table = (
    TypTable(df, rowname_col="product")
    .tab_style(
        locator=locators.LocBody(
            columns="revenue",
            rows=nw.col("region") == "North",
        ),
        cell=style.CellStyle(fill="rgb(240, 248, 255)"),
    )
)
```

This targets only the `revenue` cells for rows where `region` is `"North"`.

## Table Options

Table options change defaults for the whole rendered Typst table. Use them for
layout-level settings such as cell padding, table stroke, and row/column
gutters. Use `tab_style()` when you need to style a specific table region
instead.

```python
from typ_tables import Sides, TypTable


table = (
    TypTable(df, rowname_col="product")
    .set_table_inset(Sides(x="8pt", y="4pt"))
    .set_table_stroke("0.6pt + gray")
    .set_gutter(row_gutter="3pt", column_gutter="10pt")
)
```

If you want to start from Typst's baseline table styling instead of
typ-tables' defaults, call `clear_defaults()` before applying your own table
options and style rules.

```python
table = (
    TypTable(df)
    .clear_defaults()
    .set_table_stroke("none")
    .set_table_inset("3pt")
)
```
