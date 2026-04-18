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
      [\_Title Here\_],
    ),
  ),
  table.header([string], [int], [float]),
  [a], [10], [nan],
  [b], [10000], [1e-06],
  [c], [1000000], [0.1368753],
  [random\-letters], [568282638583], [163985.8374],
  [None], [None], [None],
)
