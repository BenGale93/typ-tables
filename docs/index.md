# Intro

With Typ-Tables you can easily create tables in Python for
[Typst](https://typst.app/docs/) reports. This library is heavily inspired by
[Great-Tables](https://posit-dev.github.io/great-tables/articles/intro.html).

To install, run `uv add typ-tables`

You can create tables that look like:

![rendered table](./images/readme_snippet.png)

Created using the following Python script:

```python
from pathlib import Path

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
result: str = table.to_typst()
```

To include the table in your Typst report you can write the resulting Typst
string to a file and include it.

```typst
#include "table.typ"
```
