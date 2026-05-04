# Style API

Styles define how selected table cells are rendered. Use them with
`TypTable.tab_style` and a locator from `typ_tables.locators`:

```python
from narwhals import selectors as ncs

from typ_tables import TypTable, locators, style

table = (
    TypTable(df)
    .tab_style(
        locator=locators.LocBody(columns=ncs.numeric()),
        text=style.TextStyle(weight="bold"),
        cell=style.CellStyle(align="right"),
    )
)
```

`TextStyle` controls the content inside a cell, such as font size, weight, and
text fill. `CellStyle` controls the table cell container, such as alignment,
inset, background fill, and borders. `Sides` is a helper for properties that can
vary by side, such as cell inset or stroke.

Style values are written as Typst-compatible strings and are passed through to
the generated Typst. For body and stub locators, style fields can also be lists
or Narwhals expressions so each row can resolve to a different value. For
single-region locators, such as `LocHeader` and `LocStubhead`, style fields must
be scalar values.

## Styling Types

::: typ_tables.ttypes.Alignment

::: typ_tables.ttypes.Auto

::: typ_tables.ttypes.Relative

::: typ_tables.style.Fill

::: typ_tables.style.Length

::: typ_tables.style.Stroke

::: typ_tables.style.FontStyle

::: typ_tables.style.FontWeight

::: typ_tables.style.Sides
    options:
      members:
        - rest
        - x
        - y
        - top
        - right
        - left
        - bottom

::: typ_tables.style.Inset

::: typ_tables.style.FullStroke

## Style Containers

::: typ_tables.style.TextStyle
    options:
      members:
        - font
        - style
        - weight
        - stretch
        - size
        - fill
        - stroke
        - tracking
        - spacing
        - fractions

::: typ_tables.style.CellStyle
    options:
      members:
        - inset
        - align
        - fill
        - stroke
