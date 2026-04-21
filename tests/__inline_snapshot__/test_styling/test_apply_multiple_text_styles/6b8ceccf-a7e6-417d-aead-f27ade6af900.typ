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
      text(
        spacing: 200%,
      )[Table Header],
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
  stroke: (bottom: 0.6pt),
  text(
    fill: red,
  )[a],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  text(
    stretch: 200%,
  )[10],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [nan],
),
  table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  text(
    font: "FreeMono",
  )[b],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  text(
    stroke: 2pt + red,
  )[10000],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [1e-06],
),
  table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  text(
    style: "italic",
  )[c],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  text(
    tracking: 1.5pt,
  )[1000000],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [0.1368753],
),
  table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  text(
    weight: "extrabold",
  )[random\-letters],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [568282638583],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [163985.8374],
),
  table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  text(
    weight: 150,
  )[None],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [None],
), table.cell(
  colspan: 1,
  stroke: (bottom: 0.6pt),
  [None],
),
)
