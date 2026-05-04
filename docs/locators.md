# Locator API

Locators describe which part of a table a style rule should target. Pass a
locator to `TypTable.tab_style` with a text style, cell style, or both:

```python
from narwhals import selectors as ncs

from typ_tables import TypTable, locators, style

table = (
    TypTable(df)
    .tab_style(
        locator=locators.LocBody(columns=ncs.numeric()),
        cell=style.CellStyle(align="right"),
    )
)
```

Some locators select a single table region and need no arguments, such as
`LocHeader` or `LocStubhead`. Others can be narrowed to specific columns, rows,
or row groups. Column-based locators use `ColumnSelector`; row-based locators
use `RowSelector`.

## Selectors

::: typ_tables.ColumnSelector

::: typ_tables.RowSelector

## Locators

::: typ_tables.locators
