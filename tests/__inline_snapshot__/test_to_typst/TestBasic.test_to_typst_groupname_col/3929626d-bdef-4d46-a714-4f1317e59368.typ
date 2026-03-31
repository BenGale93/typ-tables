#table(
  columns: 2,
  stroke: none,
  align: (auto, auto),
  table.vline(x: 1, start: 1),
table.header(
    [], [count]
  ),
table.hline(stroke: 1.2pt),
  table.hline(stroke: 1pt),
 table.cell(colspan: 2, [group\_a]),
 table.hline(stroke : 1pt),

  [apple], [10],
  table.hline(stroke: 0.6pt),
  [banana], [3],
  table.hline(stroke: 0.6pt),
  table.hline(stroke: 1pt),
 table.cell(colspan: 2, [group\_b]),
 table.hline(stroke : 1pt),

  [pear], [73],
  table.hline(stroke: 0.6pt),
  [kiwi], [477],
  table.hline(stroke: 0.6pt),
)
