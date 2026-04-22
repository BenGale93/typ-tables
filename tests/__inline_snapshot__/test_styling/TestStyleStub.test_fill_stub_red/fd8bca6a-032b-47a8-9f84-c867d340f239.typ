#table(
  columns: 2,
  column-gutter: (),
  row-gutter: (),
  stroke: none,
  align: (auto, auto),
  inset: 0% + 5pt,
  
  table.header(
    table.cell(
      colspan: 2,
      align: center,
      stroke: (top: 1.2pt, bottom: 1.2pt),
      [Table Header],
    ),
  ),
  table.header(table.cell(
  stroke: (bottom: 1.2pt),
  [],
), table.cell(
  stroke: (bottom: 1.2pt),
  [count],
),),
  table.cell(
  colspan: 2,
  stroke: (bottom: 1pt),
  [group\_a],
),
  table.cell(
  colspan: 1,
  stroke: (right: 1pt, bottom: 0.6pt),
  text(
    fill: red,
  )[apple],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [10],
),
  table.cell(
  colspan: 1,
  stroke: (right: 1pt, bottom: 0.6pt),
  text(
    fill: red,
  )[banana],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [3],
),
  table.cell(
  colspan: 2,
  stroke: (bottom: 1pt),
  [group\_b],
),
  table.cell(
  colspan: 1,
  stroke: (right: 1pt, bottom: 0.6pt),
  text(
    fill: red,
  )[pear],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [73],
),
  table.cell(
  colspan: 1,
  stroke: (right: 1pt, bottom: 0.6pt),
  text(
    fill: red,
  )[kiwi],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [477],
),
)
