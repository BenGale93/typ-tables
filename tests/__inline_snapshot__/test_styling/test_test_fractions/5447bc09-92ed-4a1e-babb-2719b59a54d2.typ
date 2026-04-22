#table(
  columns: 1,
  column-gutter: (),
  row-gutter: (),
  stroke: none,
  align: (auto),
  inset: 0% + 5pt,
  
  table.header(
    table.cell(
      colspan: 1,
      align: center,
      stroke: (top: 1.2pt, bottom: 1.2pt),
      [Table Header],
    ),
  ),
  table.header(table.cell(
  stroke: (bottom: 1.2pt),
  [Fractions],
),),
  table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  text(
    fractions: true,
  )[1\/2],
),
  table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  text(
    fractions: true,
  )[1\/3],
),
)
