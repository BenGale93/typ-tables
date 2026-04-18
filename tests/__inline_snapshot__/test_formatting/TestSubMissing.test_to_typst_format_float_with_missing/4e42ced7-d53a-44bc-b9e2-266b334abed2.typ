#table(
  columns: 3,
  stroke: (x, y) => (
    bottom: if y < 1 { 1.2pt } else { 0.6pt },
    left: none,
    right: none,
    top: none
  ),
  align: (auto, auto, auto),
  table.header([string], [int], [float]),
  [a], [10.00], [Missing],
  [b], [10,000.00], [0.00],
  [c], [1,000,000.00], [0.14],
  [random\-letters], [568,282,638,583.00], [163,985.84],
  [Missing], [Missing], [Missing],
)
