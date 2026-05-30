#table(
  columns: 2,
  stroke: none,
  align: (auto, auto),
  table.header[#table.cell(colspan: 2, align: center, stroke: (top: 1.2pt, bottom: 1.2pt))[Table Header]],
  table.header[#table.cell(align: center)[]][#table.cell(align: center)[#text(fill: red)[
  Count
  #v(5pt)
  #place(bottom + center, line(length: 100%, stroke: 1.2pt))]]],
  table.header[#table.cell(stroke: (bottom: 1.2pt))[]][#table.cell(stroke: (bottom: 1.2pt))[count]],
  [#table.cell(colspan: 2, stroke: (bottom: 1pt))[group\_a]],
  [#table.cell(stroke: (right: 1pt, bottom: 0.6pt))[#text(fill: red)[apple]]], [#table.cell(stroke: (bottom: 0.6pt))[10]],
  [#table.cell(stroke: (right: 1pt, bottom: 0.6pt))[#text(fill: red)[banana]]], [#table.cell(stroke: (bottom: 0.6pt))[3]],
  [#table.cell(colspan: 2, stroke: (bottom: 1pt))[group\_b]],
  [#table.cell(stroke: (right: 1pt, bottom: 0.6pt))[#text(fill: red)[pear]]], [#table.cell(stroke: (bottom: 0.6pt))[73]],
  [#table.cell(stroke: (right: 1pt, bottom: 0.6pt))[#text(fill: red)[kiwi]]], [#table.cell(stroke: (bottom: 0.6pt))[477]],
  table.footer[#table.cell(colspan: 2, stroke: (top: 1.2pt, bottom: 1.2pt))[Table Footer]],
)
