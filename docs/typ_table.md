# TypTable Full API

`TypTable` is the main builder for turning DataFrame-like data into Typst table
markup. After construction, its methods configure the table by adding labels,
formatting rules, styling rules, column operations, and table-level options.

Most public methods return the current table instance (`Self`). This makes the
API fluent: each call updates the table configuration and passes the same object
to the next call. Call `to_typst()` at the end when you want the rendered Typst
string.

```python
from typ_tables import TypTable, locators, style

typst = (
    TypTable(df, rowname_col="name")
    .tab_header("Sales by Product", subtitle="2026")
    .fmt_currency(columns="revenue", currency="USD")
    .tab_style(
        locator=locators.LocBody(columns="revenue"),
        cell=style.CellStyle(align="right"),
    )
    .to_typst()
)
```

## Table Creation and Rendering

::: typ_tables.TypTable
    options:
      members:
        - __init__
        - to_typst

## Modifying the Table

::: typ_tables.TypTable.tab_header

::: typ_tables.TypTable.tab_figure

::: typ_tables.TypTable.tab_stubhead

## Styling the Table

::: typ_tables.TypTable.tab_style

## Formatting Cell Contents

::: typ_tables.TypTable.sub_missing

::: typ_tables.TypTable.fmt

::: typ_tables.TypTable.fmt_number

::: typ_tables.TypTable.fmt_integer

::: typ_tables.TypTable.fmt_percentage

::: typ_tables.TypTable.fmt_scientific

::: typ_tables.TypTable.fmt_engineering

::: typ_tables.TypTable.fmt_currency

::: typ_tables.TypTable.fmt_date

::: typ_tables.TypTable.fmt_time

::: typ_tables.TypTable.fmt_datetime

::: typ_tables.TypTable.fmt_tf

::: typ_tables.TypTable.fmt_bytes

## Modifying Columns

::: typ_tables.TypTable.cols_align

::: typ_tables.TypTable.cols_hide

::: typ_tables.TypTable.cols_label

::: typ_tables.TypTable.cols_label_with

## Table Options

::: typ_tables.TypTable.set_table_inset

::: typ_tables.TypTable.set_table_stroke

::: typ_tables.TypTable.set_gutter

::: typ_tables.TypTable.clear_defaults


## Pipeline

::: typ_tables.TypTable.pipe
