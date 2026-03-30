#table(
  columns: 3,
  stroke: none,
  align: (auto, auto, auto),
  table.hline(stroke: 1.2pt),
    table.header(
    table.cell(
      colspan: 3,
      align: center,
      [
        == Title Here
      ]
    )
  ),
  table.hline(stroke: 1.2pt),
  table.vline(x: 1, start: 2),
table.header(
    [], [int], [float]
  ),
table.hline(stroke: 1.2pt),
  [a], [10], [1e-06],
  table.hline(stroke: 0.6pt),
  [b], [10000], [0.1368753],
  table.hline(stroke: 0.6pt),
  [c], [1000000], [163985.8374],
  table.hline(stroke: 0.6pt),
)
