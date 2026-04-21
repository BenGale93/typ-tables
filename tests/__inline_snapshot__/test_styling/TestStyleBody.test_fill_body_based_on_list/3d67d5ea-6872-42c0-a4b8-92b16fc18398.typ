#table(
  columns: 3,
  stroke: none,
  align: (auto, auto, auto),
  inset: 0% + 5pt,
  
  table.header(
    table.cell(
      colspan: 3,
      align: center,
      stroke: (top: 1.2pt, bottom: 1.2pt),
      [Table Header],
    ),
  ),
  table.header(table.cell(
  stroke: (bottom: 1.2pt),
  [string],
), table.cell(
  stroke: (bottom: 1.2pt),
  [int],
), table.cell(
  stroke: (bottom: 1.2pt),
  [float],
),),
  table.cell(
  colspan: 1,
  align: left,
  stroke: (bottom: 0.6pt),
  text(
    fill: red,
  )[a],
), table.cell(
  colspan: 1,
  align: left,
  stroke: (bottom: 0.6pt),
  text(
    fill: red,
  )[10],
), table.cell(
  colspan: 1,
  align: left,
  stroke: (bottom: 0.6pt),
  text(
    fill: red,
  )[nan],
),
  table.cell(
  colspan: 1,
  align: right,
  stroke: (bottom: 0.6pt),
  text(
    fill: blue,
  )[b],
), table.cell(
  colspan: 1,
  align: right,
  stroke: (bottom: 0.6pt),
  text(
    fill: blue,
  )[10000],
), table.cell(
  colspan: 1,
  align: right,
  stroke: (bottom: 0.6pt),
  text(
    fill: blue,
  )[1e-06],
),
  table.cell(
  colspan: 1,
  align: top,
  stroke: (bottom: 0.6pt),
  text(
    fill: red,
  )[c],
), table.cell(
  colspan: 1,
  align: top,
  stroke: (bottom: 0.6pt),
  text(
    fill: red,
  )[1000000],
), table.cell(
  colspan: 1,
  align: top,
  stroke: (bottom: 0.6pt),
  text(
    fill: red,
  )[0.1368753],
),
  table.cell(
  colspan: 1,
  align: bottom,
  stroke: (bottom: 0.6pt),
  text(
    fill: yellow,
  )[random\-letters],
), table.cell(
  colspan: 1,
  align: bottom,
  stroke: (bottom: 0.6pt),
  text(
    fill: yellow,
  )[568282638583],
), table.cell(
  colspan: 1,
  align: bottom,
  stroke: (bottom: 0.6pt),
  text(
    fill: yellow,
  )[163985.8374],
),
  table.cell(
  colspan: 1,
  align: horizon,
  stroke: (bottom: 0.6pt),
  text(
    fill: purple,
  )[None],
), table.cell(
  colspan: 1,
  align: horizon,
  stroke: (bottom: 0.6pt),
  text(
    fill: purple,
  )[None],
), table.cell(
  colspan: 1,
  align: horizon,
  stroke: (bottom: 0.6pt),
  text(
    fill: purple,
  )[None],
),
)
