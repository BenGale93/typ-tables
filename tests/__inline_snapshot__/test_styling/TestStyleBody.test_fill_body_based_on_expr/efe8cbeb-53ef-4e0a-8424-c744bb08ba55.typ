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
  table.header([string], [int], [float]),
  table.cell(
  colspan: 1,
  align: right,
  text(
    fill: blue,
  )[a],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: blue,
  )[10],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: blue,
  )[nan],
),
  table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[b],
), table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[10000],
), table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[1e-06],
),
  table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[c],
), table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[1000000],
), table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[0.1368753],
),
  table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[random\-letters],
), table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[568282638583],
), table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[163985.8374],
),
  table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[None],
), table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[None],
), table.cell(
  colspan: 1,
  align: left,
  text(
    fill: red,
  )[None],
),
)
