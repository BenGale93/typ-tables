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
  table.header([], [count]),
  table.cell(
  colspan: 2,
  stroke: (top: 1pt, bottom: 1pt),
  text(
    fill: red,
  )[group\_a],
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
  stroke: (top: 1pt, bottom: 1pt),
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
  table.hline(stroke: 1pt),
)
