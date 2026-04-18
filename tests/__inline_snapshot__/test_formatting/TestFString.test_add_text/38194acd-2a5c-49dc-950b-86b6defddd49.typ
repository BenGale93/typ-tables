#table(
  columns: 2,
  stroke: (x, y) => (
    bottom: if y < 1 { 1.2pt } else { 0.6pt },
    left: none,
    right: none,
    top: none
  ),
  align: (auto, auto),
  table.header([string], [int]),
  [^a\*], [10],
  [^b\*], [10000],
  [^c\*], [1000000],
  [None], [None],
)
