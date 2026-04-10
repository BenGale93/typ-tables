#table(
  columns: 3,
  stroke: none,
  align: (auto, auto, auto),
  table.hline(stroke: 1.2pt),
  table.header(
    table.cell(
      colspan: 3,
      align: center,
      text(
        spacing: 200%,
      )[Table Header],
    ),
  ),
  table.hline(stroke: 1.2pt),
  table.header([string], [int], [float]),
  table.hline(stroke: 1.2pt),
  text(
  fill: red,
)[a], text(
  stretch: 200%,
)[10], [nan],
  table.hline(stroke: 0.6pt),
  text(
  font: "FreeMono",
)[b], text(
  stroke: 2pt + red,
)[10000], [1e-06],
  table.hline(stroke: 0.6pt),
  text(
  style: "italic",
)[c], text(
  tracking: 1.5pt,
)[1000000], [0.1368753],
  table.hline(stroke: 0.6pt),
  text(
  weight: "extrabold",
)[random\-letters], [568282638583], [163985.8374],
  table.hline(stroke: 0.6pt),
  text(
  weight: 150,
)[None], [None], [None],
  table.hline(stroke: 0.6pt),
)
