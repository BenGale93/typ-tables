#table(
  columns: 3,
  column-gutter: (),
  row-gutter: (),
  stroke: none,
  align: (auto, auto, auto),
  inset: 0% + 5pt,
  table.header(
    table.cell(
      stroke: (bottom: 1.2pt),
      [],
    ),
    table.cell(
      stroke: (bottom: 1.2pt),
      [active],
    ),
    table.cell(
      stroke: (bottom: 1.2pt),
      [verified],
    ),
  ),
  table.cell(
    colspan: 1,
    stroke: (right: 1pt, bottom: 0.6pt),
    [Alice],
  ),
  table.cell(
    colspan: 1,
    stroke: (bottom: 0.6pt),
    [#sym.checkmark],
  ),
  table.cell(
    colspan: 1,
    stroke: (bottom: 0.6pt),
    [#sym.circle],
  ),
  table.cell(
    colspan: 1,
    stroke: (right: 1pt, bottom: 0.6pt),
    [Bob],
  ),
  table.cell(
    colspan: 1,
    stroke: (bottom: 0.6pt),
    [#sym.crossmark],
  ),
  table.cell(
    colspan: 1,
    stroke: (bottom: 0.6pt),
    [#sym.circle.filled],
  ),
  table.cell(
    colspan: 1,
    stroke: (right: 1pt, bottom: 0.6pt),
    [Charlie],
  ),
  table.cell(
    colspan: 1,
    stroke: (bottom: 0.6pt),
    [#sym.checkmark],
  ),
  table.cell(
    colspan: 1,
    stroke: (bottom: 0.6pt),
    [#sym.circle.filled],
  ),
)
