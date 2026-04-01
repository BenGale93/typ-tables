#table(
  columns: 3,
  stroke: none,
  align: (auto, auto, auto),
  table.hline(stroke: 1.2pt),
  table.header(
    table.cell(
      colspan: 3,
      inset: (bottom: 20pt),
      align: right,
      text(
        size: 15pt,
        fill: blue,
      )[Test Header],
    ),
  ),
  table.hline(stroke: 1.2pt),
  table.header([int], [float], [string]),
  table.hline(stroke: 1.2pt),
  [10], [1e-06], [a],
  table.hline(stroke: 0.6pt),
  [10000], [0.1368753], [b],
  table.hline(stroke: 0.6pt),
  [1000000], [163985.8374], [c],
  table.hline(stroke: 0.6pt),
)
