#table(
  columns: 2,
  stroke: (x, y) => (
    bottom: if y < 1 { 1.2pt } else { 0.6pt },
    left: none,
    right: none,
    top: none
  ),
  align: (auto, auto),
  table.vline(x: 1, start: 1),
table.header([], [count]),
  table.cell(
  colspan: 2,
  stroke: (bottom: 1pt),
  [group\_a],
),
  [apple], [10],
  [banana], [3],
  table.cell(
  colspan: 2,
  stroke: (bottom: 1pt),
  [group\_b],
),
  [pear], [73],
  [kiwi], [477],
)
