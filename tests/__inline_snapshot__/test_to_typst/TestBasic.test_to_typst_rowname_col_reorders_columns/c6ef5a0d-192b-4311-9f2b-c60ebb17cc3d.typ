#table(
  columns: 3,
  stroke: (x, y) => (
    bottom: if y < 1 { 1.2pt } else { 0.6pt },
    left: none,
    right: none,
    top: none
  ),
  align: (auto, auto, auto),
  table.header([], [int], [float]),
  table.cell(
  colspan: 1,
  stroke: (right: 1pt),
  [a],
), [10], [1e-06],
  table.cell(
  colspan: 1,
  stroke: (right: 1pt),
  [b],
), [10000], [0.1368753],
  table.cell(
  colspan: 1,
  stroke: (right: 1pt),
  [c],
), [1000000], [163985.8374],
)
