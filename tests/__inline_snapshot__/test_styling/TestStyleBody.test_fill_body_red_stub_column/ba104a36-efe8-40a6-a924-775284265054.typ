#table(
  columns: 2,
  stroke: (x, y) => (
    bottom: if y < 2 { 1.2pt } else { 0.6pt },
    left: none,
    right: none,
    top: none
  ),
  align: (auto, auto),
  
  table.header(
    table.cell(
      colspan: 2,
      align: center,
      stroke: (top: 1.2pt, bottom: 1.2pt),
      [Table Header],
    ),
  ),
  table.vline(x: 1, start: 2),
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
