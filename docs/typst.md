# Raw Typst Markup

Typ-tables escapes plain string values before placing them in the generated
Typst output. This keeps ordinary text safe: characters such as `_`, `#`, `$`,
and `[` are displayed literally instead of being interpreted as Typst syntax.

Use `Typst` when you intentionally want to pass raw Typst markup through to the
rendered table.

```python
from typ_tables import TypTable, Typst


table = (
    TypTable(df)
    .tab_header(Typst("#strong[Quarterly Results]"))
    .tab_figure(caption=Typst("[#emph[Source:] internal reporting]"))
    .cols_label(revenue=Typst("Revenue #text(size: 0.75em)[USD]"))
)
```

Only wrap trusted Typst markup. `Typst` bypasses escaping, so invalid Typst will
be emitted as-is and may cause Typst compilation errors.

Common places that accept `Typst` include:

- `TypTable.tab_header()` for titles and subtitles.
- `TypTable.tab_figure()` for captions.
- `TypTable.tab_stubhead()` for the stub-head label.
- `TypTable.cols_label()` and `TypTable.cols_label_with()` for column labels.

::: typ_tables.Typst
