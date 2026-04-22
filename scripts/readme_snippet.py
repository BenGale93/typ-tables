from pathlib import Path  # noqa: D100, INP001

import polars as pl
from PIL import Image
from typst import compile_with_warnings

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

png, warn = compile_with_warnings(result.encode(), format="png")

png_path = Path("docs/images/readme_snippet.png")

png_path.write_bytes(png)

with Image.open(png_path) as im:
    new_im = im.crop((120, 130, 460, 300))

    new_im.save(png_path)
