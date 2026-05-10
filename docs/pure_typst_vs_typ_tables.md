# Typ-Tables vs Pure Typst

Typst can load CSV files directly with `#csv` or JSON files with `#json`. So
you might be asking, why bother with `typ-table`? This explainer aims to
persuade you that `typ-tables` is more ergonomic when you are already
summarising the data in Python anyway.

## Data Preparation

Suppose the source data is transaction-level sales data and the report needs a
summary by region and customer segment. The data prep belongs in Python
regardless:

```python
from pathlib import Path

import polars as pl


sales = pl.DataFrame(
    {
        "region": ["North", "North", "North", "South", "South", "South"],
        "segment": ["Retail", "Retail", "Enterprise", "Retail", "Enterprise", "Enterprise"],
        "orders": [42, 35, 18, 31, 24, 29],
        "revenue": [12_600, 10_850, 21_400, 9_920, 28_600, 33_350],
        "cost": [7_900, 6_820, 13_200, 6_300, 16_700, 19_100],
    }
)

summary = (
    sales.group_by(["region", "segment"])
    .agg(
        pl.sum("orders"),
        pl.sum("revenue"),
        pl.sum("cost"),
    )
    .with_columns(
        avg_order=pl.col("revenue") / pl.col("orders"),
        margin=(pl.col("revenue") - pl.col("cost")) / pl.col("revenue"),
    )
    .sort(["region", "revenue"], descending=[False, True])
)
```

With `typ-tables`, the remaining code transforms the DataFrame into a Typst
table string. Formatting, labels, row grouping, and data-dependent styling stay
beside the DataFrame that created the result:

```python
import narwhals as nw

from typ_tables import Typst, TypTable, locators, style

margin_threshold = 0.4

typst = (
    TypTable(summary, rowname_col="segment", groupname_col="region")
    .tab_header("Sales Summary", subtitle="Grouped by region and segment")
    .tab_stubhead(Typst("*Segment*"))
    .cols_label_with(
        lambda x: Typst("*" + x.title().replace("_", ". ") + "*"),
    )
    .cols_hide("cost")
    .fmt_currency(columns=["revenue", "avg_order"], currency="USD", decimals=0)
    .fmt_percentage(columns="margin", decimals=1)
    .tab_style(
        locator=locators.LocBody(columns="margin", rows=nw.col("margin") >= margin_threshold),
        text=style.TextStyle(weight="bold"),
        cell=style.CellStyle(fill="rgb(232, 246, 239)"),
    )
    .to_typst()
)

Path("sales-summary.typ").write_text(typst)
```

Then the Typst document only needs to include the generated table:

```typst
#include "sales-summary.typ"
```

On the other hand, if the presentation logic is done in Typst, we first need to
save the CSV:

```python
summary.write_csv("sales-summary.csv")
```

Then load and format it in the Typst document:

```typst
#let data = csv("sales-summary.csv", row-type: dictionary)

#let currency(val) = "$" + str(calc.round(float(val)))
#let percent(val) = str(calc.round(float(val) * 100, digits: 1)) + "%"

#table(
  columns: (auto, auto, auto, auto, auto),
  inset: 5pt,
  align: (left, right, right, right, right),
  table.header(
    table.cell(colspan: 5, align: center)[
      #set text(1.2em)
      *Sales Summary* \
      #text(0.8em, weight: "regular")[Grouped by region and segment]
    ],
    [*Segment*], [*Orders*], [*Revenue*], [*Avg. order*], [*Margin*],
  ),
  ..{
    let last-region = none
    let rows = ()
    for row in data {
      if row.region != last-region {
        rows.push(table.cell(colspan: 5)[#row.region])
        last-region = row.region
      }

      let m = float(row.margin)
      let highlight = m >= 0.4

      rows.push([#row.segment])
      rows.push([#row.orders])
      rows.push([#currency(row.revenue)])
      rows.push([#currency(row.avg_order)])
      rows.push(table.cell(fill: if highlight { rgb("#e8f6ef") })[
        #if highlight { strong(percent(row.margin)) } else { percent(row.margin) }
      ])
    }
    rows
  },
)

```

## Ergonomics

Which approach you find most ergonomic will probably depend on whether you are
a better Python or Typst programmer. That being said...

### Advantages of Typ-Tables

**Code Locality**

With Python, the code preparing, formatting, and styling the data is all in one
place. If the data changes at all, you only have to update the Python script
rather than a Python export script and Typst script.

**Declarative API**

The fluent API used by `typ-tables` allows you to describe _what_ you want and
the library handles the how. In Typst you need to write the logic for how to
build the table including defining the helper functions. Of course, if
`typ-tables` doesn't support the formatting or styling you need, this doesn't
help.

**Expressions**

Conditional styling and formatting can be done using expressions rather than
manual if else logic. Expressions can be constructed programmatically so
complex selection logic can easily be used.

[Narwhal column
selectors](https://narwhals-dev.github.io/narwhals/api-reference/selectors/)
are particularly powerful.

**Helpers**

- Row grouping is handled automatically using `typ-tables`, no manual tracking.
- Easily transform column labels programmatically.
- Full power of the Python standard library and ecosystem.

### Disadvantages of Typ-Tables

**Stringy Types**

Many of the types used for styling are just strings. So you won't know if the
stroke you defined is valid Typst until the snippet produced by `typ-tables`
has been compiled. Whereas if you a using a Typst LSP, you will know
straight away.

This is something we hope to improve in the future.

**No Instant Preview**

If you notice an issue with the style, you need to re-run the Python and then
recompile the PDF.

**Context Awareness**

In Typst, you can reference any global variables directly and if you want to
change the name you can use the LSP to do so. With Python, you have to be
careful to reference the global correctly and then keep them in sync.

## Summary

If you are already doing a bunch of data crunching in Python `typ-tables` might
work well for you. If you already have clean data you just want to present in
your report, it is probably overkill.
