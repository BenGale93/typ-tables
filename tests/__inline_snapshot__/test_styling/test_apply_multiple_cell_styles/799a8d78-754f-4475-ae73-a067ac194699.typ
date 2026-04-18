#table(
  columns: 3,
  stroke: (x, y) => (
    bottom: if y < 2 { 1.2pt } else { 0.6pt },
    left: none,
    right: none,
    top: none
  ),
  align: (auto, auto, auto),
  
  table.header(
    table.cell(
      colspan: 3,
      align: center,
      stroke: (top: 1.2pt, bottom: 1.2pt),
      [Table Header],
    ),
  ),
  table.header([string], [int], [float]),
  table.cell(
  colspan: 1,
  inset: 1pt,
  [a],
), [10], [nan],
  table.cell(
  colspan: 1,
  align: right,
  [b],
), [10000], [1e-06],
  table.cell(
  colspan: 1,
  fill: red,
  [c],
), [1000000], [0.1368753],
  table.cell(
  colspan: 1,
  stroke: 2pt + blue,
  [random\-letters],
), [568282638583], [163985.8374],
  table.cell(
  colspan: 1,
  stroke: (bottom: 1pt + red),
  [None],
), [None], [None],
)
