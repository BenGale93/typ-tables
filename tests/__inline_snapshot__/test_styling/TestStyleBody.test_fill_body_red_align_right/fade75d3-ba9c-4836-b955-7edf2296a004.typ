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
  table.header([string], [int], [float]),
  table.hline(stroke: 1.2pt),
  table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[a],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[10],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[nan],
),
  table.hline(stroke: 0.6pt),
  table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[b],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[10000],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[1e-06],
),
  table.hline(stroke: 0.6pt),
  table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[c],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[1000000],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[0.1368753],
),
  table.hline(stroke: 0.6pt),
  table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[random\-letters],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[568282638583],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[163985.8374],
),
  table.hline(stroke: 0.6pt),
  table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[None],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[None],
), table.cell(
  colspan: 1,
  align: right,
  text(
    fill: red,
  )[None],
),
  table.hline(stroke: 0.6pt),
)
