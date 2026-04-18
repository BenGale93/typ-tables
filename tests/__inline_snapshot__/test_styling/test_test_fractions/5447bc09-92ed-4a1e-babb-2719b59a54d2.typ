#table(
  columns: 1,
  stroke: (x, y) => (
    bottom: if y < 2 { 1.2pt } else { 0.6pt },
    left: none,
    right: none,
    top: none
  ),
  align: (auto),
  
  table.header(
    table.cell(
      colspan: 1,
      align: center,
      stroke: (top: 1.2pt, bottom: 1.2pt),
      [Table Header],
    ),
  ),
  table.header([Fractions]),
  text(
  fractions: true,
)[1\/2],
  text(
  fractions: true,
)[1\/3],
)
