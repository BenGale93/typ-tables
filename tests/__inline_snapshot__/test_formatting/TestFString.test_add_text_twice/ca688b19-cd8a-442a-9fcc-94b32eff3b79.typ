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
  [\_^a\*\_], [\_10\_],
  [\_^b\*\_], [\_10000\_],
  [\_^c\*\_], [\_1000000\_],
  [None], [None],
)
