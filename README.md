# typ-tables

Inspired by
[great_tables](https://posit-dev.github.io/great-tables/articles/intro.html), a
way to turn DataFrames into Typst tables.

```python
import polars as pl
from typ_tables import TypTable

df = pl.DataFrame(
    {
        "string": ["a", "b", "c"],
        "int": [10, 10000, 1000000],
        "float": [0.000001, 0.1368753, 163985.8374],
    }
)

table = TypTable(df)
result = table.to_typst()
```

Gives you:

```typ
#table(
  columns: 3,
  table.header(
    [string], [int], [float]
  ),
  [a], [10], [1e-06],
  [b], [10000], [0.1368753],
  [c], [1000000], [163985.8374],
)
```