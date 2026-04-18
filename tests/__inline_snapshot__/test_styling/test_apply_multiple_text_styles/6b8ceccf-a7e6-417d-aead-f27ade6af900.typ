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
      text(
        spacing: 200%,
      )[Table Header],
    ),
  ),
  table.header([string], [int], [float]),
  text(
  fill: red,
)[a], text(
  stretch: 200%,
)[10], [nan],
  text(
  font: "FreeMono",
)[b], text(
  stroke: 2pt + red,
)[10000], [1e-06],
  text(
  style: "italic",
)[c], text(
  tracking: 1.5pt,
)[1000000], [0.1368753],
  text(
  weight: "extrabold",
)[random\-letters], [568282638583], [163985.8374],
  text(
  weight: 150,
)[None], [None], [None],
)
