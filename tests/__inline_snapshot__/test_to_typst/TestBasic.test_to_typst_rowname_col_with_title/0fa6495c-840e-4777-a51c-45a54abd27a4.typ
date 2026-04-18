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
      [Title Here],
    ),
  ),
  table.vline(x: 1, start: 2),
table.header([], [int], [float]),
  [a], [10], [1e-06],
  [b], [10000], [0.1368753],
  [c], [1000000], [163985.8374],
)
