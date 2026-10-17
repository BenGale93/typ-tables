# typ-tables

[![CI](https://github.com/BenGale93/typ-tables/actions/workflows/ci.yml/badge.svg)](https://github.com/BenGale93/typ-tables/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/typ-tables)](https://pypi.org/project/typ-tables/)
[![Python versions](https://img.shields.io/pypi/pyversions/typ-tables)](https://pypi.org/project/typ-tables/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/BenGale93/typ-tables/blob/master/LICENSE)

Inspired by great-tables, a way to turn DataFrames into Typst tables.

To install, run `uv add typ-tables`

Tables that look like

![rendered table](https://bengale93.github.io/typ-tables/images/readme_snippet.png)

Created using the following Python script:

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
result: str = table.to_typst()
```

To include the table in your Typst report you can write the resulting Typst
string to a file and include it.

```typst
#include "table.typ"
```

## Documentation

For more, check out the
[documentation](https://bengale93.github.io/typ-tables/). The
[great_tables](https://posit-dev.github.io/great-tables/articles/intro.html)
documentation is also useful as many of the examples work in `typ-tables`.
