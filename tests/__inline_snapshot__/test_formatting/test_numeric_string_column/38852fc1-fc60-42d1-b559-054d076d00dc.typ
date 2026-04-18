#table(
  columns: 1,
  stroke: (x, y) => (
    bottom: if y < 1 { 1.2pt } else { 0.6pt },
    left: none,
    right: none,
    top: none
  ),
  align: (auto),
  table.header([string]),
  [stuff],
  [1.27],
)
