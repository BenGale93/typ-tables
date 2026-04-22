#table(
  columns: 3,
  column-gutter: (),
  row-gutter: (),
  stroke: (x, y) => if y == 0 { (bottom: 0.7pt + black) },
  align: (auto, auto, auto),
  inset: 0% + 5pt,
  
  table.header(
    table.cell(
      colspan: 3,
      [Test Header],
    ),
  ),
  table.header([string], [int], [float],),
  [a], [10], [nan],
  [b], [10000], [1e-06],
  [c], [1000000], [0.1368753],
  [random\-letters], [568282638583], [163985.8374],
  [None], [None], [None],
)
