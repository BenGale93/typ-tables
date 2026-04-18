#table(
  columns: 3,
  stroke: (x, y) => (
    bottom: if y < 2 { 1.2pt } else { 0.6pt },
    left: none,
    right: none,
    top: none
  ),
  align: (auto, auto, auto),
  
  table.header(
    table.cell(
      colspan: 3,
      align: center,
      stroke: (top: 1.2pt, bottom: 1.2pt),
      [Table Header],
    ),
  ),
  table.header([group], [fruit], [count]),
  [group\_a], [apple], [10],
  [group\_b], [pear], [73],
  [group\_a], [banana], [3],
  [group\_b], [kiwi], [477],
)
