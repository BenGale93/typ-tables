#table(
  columns: 3,
  stroke: none,
  align: (auto, auto, auto),
  table.hline(stroke: 1.2pt),
  table.header(
    table.cell(
      colspan: 3,
      align: center,
      [Table Header],
    ),
  ),
  table.hline(stroke: 1.2pt),
  table.header([group], [fruit], [count]),
  table.hline(stroke: 1.2pt),
  [group\_a], [apple], [10],
  table.hline(stroke: 0.6pt),
  [group\_b], [pear], [73],
  table.hline(stroke: 0.6pt),
  [group\_a], [banana], [3],
  table.hline(stroke: 0.6pt),
  [group\_b], [kiwi], [477],
  table.hline(stroke: 0.6pt),
)
