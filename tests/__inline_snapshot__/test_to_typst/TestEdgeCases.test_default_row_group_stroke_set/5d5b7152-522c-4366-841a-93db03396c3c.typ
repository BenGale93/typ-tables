#table(
  columns: 2,
  stroke: (x, y) => (
    bottom: if y < 1 { 1.2pt } else { 0.6pt },
    left: none,
    right: none,
    top: none
  ),
  align: (auto, auto),
  table.header([], [count]),
  table.cell(
  colspan: 2,
  stroke: 2pt,
  [group\_a],
),
  table.cell(
  colspan: 1,
  stroke: (right: 1pt),
  [apple],
), [10],
  table.cell(
  colspan: 1,
  stroke: (right: 1pt),
  [banana],
), [3],
  table.cell(
  colspan: 2,
  stroke: 2pt,
  [group\_b],
),
  table.cell(
  colspan: 1,
  stroke: (right: 1pt),
  [pear],
), [73],
  table.cell(
  colspan: 1,
  stroke: (right: 1pt),
  [kiwi],
), [477],
  table.hline(stroke: 2pt),
)
