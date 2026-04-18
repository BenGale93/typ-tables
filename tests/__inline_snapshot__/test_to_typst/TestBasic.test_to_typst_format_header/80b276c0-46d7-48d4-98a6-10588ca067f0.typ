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
      inset: (bottom: 20pt),
      align: right,
      stroke: (top: 1.2pt, bottom: 1.2pt),
      text(
        size: 15pt,
        fill: blue,
      )[Test Header],
    ),
  ),
  table.header([int], [float], [string]),
  [10], [1e-06], [a],
  [10000], [0.1368753], [b],
  [1000000], [163985.8374], [c],
)
