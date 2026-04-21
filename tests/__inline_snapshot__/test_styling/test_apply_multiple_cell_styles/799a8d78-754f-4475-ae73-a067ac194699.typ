#table(
  columns: 3,
  stroke: none,
  align: (auto, auto, auto),
  
  table.header(
    table.cell(
      colspan: 3,
      align: center,
      stroke: (top: 1.2pt, bottom: 1.2pt),
      [Table Header],
    ),
  ),
  table.header(table.cell(
  stroke: (bottom: 1.2pt),
  [string],
), table.cell(
  stroke: (bottom: 1.2pt),
  [int],
), table.cell(
  stroke: (bottom: 1.2pt),
  [float],
),),
  table.cell(
  colspan: 1,
  inset: 1pt,
  stroke: (bottom: 0.6pt),
  [a],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [10],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [nan],
),
  table.cell(
  colspan: 1,
  align: right,
  stroke: (bottom: 0.6pt),
  [b],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [10000],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [1e-06],
),
  table.cell(
  colspan: 1,
  fill: red,
  stroke: (bottom: 0.6pt),
  [c],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [1000000],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [0.1368753],
),
  table.cell(
  colspan: 1,
  stroke: 2pt + blue,
  [random\-letters],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [568282638583],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [163985.8374],
),
  table.cell(
  colspan: 1,
  stroke: (bottom: 1pt + red),
  [None],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [None],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [None],
),
)
