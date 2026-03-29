#table(
  columns: 3,
  align: (auto, auto, auto),
  table.header(
    table.cell(
      colspan: 3,
      align: center,
      [
        == Title Here \
        Subtitle here
      ]
    )
  ),
  table.header(
    [string], [int], [float]
  ),
  [a], [10], [nan],
  [b], [10000], [1e-06],
  [c], [1000000], [0.1368753],
  [random\-letters], [568282638583], [163985.8374],
  [None], [None], [None],
)
