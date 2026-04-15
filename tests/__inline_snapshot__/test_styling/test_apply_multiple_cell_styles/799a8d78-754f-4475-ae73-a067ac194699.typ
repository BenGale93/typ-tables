#table(
  columns: 3,
  stroke: none,
  align: (auto, auto, auto),
  table.hline(stroke: 1.2pt),
  table.header(
    table.cell(
      colspan: 3,
      align: center,
      [Table Header],
    ),
  ),
  table.hline(stroke: 1.2pt),
  table.header([string], [int], [float]),
  table.hline(stroke: 1.2pt),
  table.cell(
  colspan: 1,
  inset: 1pt,
  [a],
), [10], [nan],
  table.hline(stroke: 0.6pt),
  table.cell(
  colspan: 1,
  align: right,
  [b],
), [10000], [1e-06],
  table.hline(stroke: 0.6pt),
  table.cell(
  colspan: 1,
  fill: red,
  [c],
), [1000000], [0.1368753],
  table.hline(stroke: 0.6pt),
  table.cell(
  colspan: 1,
  stroke: 2pt + blue,
  [random\-letters],
), [568282638583], [163985.8374],
  table.hline(stroke: 0.6pt),
  [None], [None], [None],
  table.hline(stroke: 0.6pt),
)
