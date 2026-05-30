from inline_snapshot import snapshot

from typ_tables._escape import Typst
from typ_tables._rendering import Cell, Content, Figure, Footer, Header, Table
from typ_tables._style import CellStyleForCell, Sides, TextStyleForCell


def test_content_renders_plain_text_with_escaping() -> None:
    content = Content(value="Growth #1 [net]")

    assert content.render() == snapshot("Growth \\#1 \\[net\\]")


def test_content_renders_raw_typst_without_escaping() -> None:
    content = Content(value=Typst("#strong[Growth #1]"))

    assert content.render() == snapshot("#strong[Growth #1]")


def test_content_renders_text_style_arguments() -> None:
    content = Content(
        value="1/2",
        text_style=TextStyleForCell(
            font="IBM Plex Sans",
            weight="bold",
            fill="blue",
            fractions=True,
        ),
    )

    assert content.render() == snapshot(
        '#text(font: "IBM Plex Sans", weight: "bold", fill: blue, fractions: true)[1\\/2]'
    )


def test_cell_renders_span_and_cell_style_arguments() -> None:
    cell = Cell(
        content=Content(value="Total"),
        rowspan=2,
        colspan=3,
        cell_style=CellStyleForCell(
            inset=Sides(x="4pt", y="2pt"),
            align="center",
            fill='rgb("f5f5f5")',
            stroke=Sides(top="1pt", bottom="0.5pt"),
        ),
    )

    assert cell.render() == snapshot(
        "[#table.cell(rowspan: 2, colspan: 3, inset: (x: 4pt, y: 2pt), align: center, "
        'fill: rgb("f5f5f5"), stroke: (top: 1pt, bottom: 0.5pt))[Total]]'
    )


def test_header_renders_level_repeat_and_cells() -> None:
    header = Header(
        content=[
            Cell(Content("Name"), cell_style=CellStyleForCell(align="left")),
            Cell(Content("Score"), cell_style=CellStyleForCell(align="right")),
        ],
        repeat=False,
        level=2,
    )

    assert header.render() == snapshot(
        "table.header(repeat: false, level: 2,)[#table.cell(align: left)[Name]]"
        "[#table.cell(align: right)[Score]]"
    )


def test_footer_renders_cells() -> None:
    footer = Footer(
        content=[
            Cell(Content("Note")),
        ],
    )

    assert footer.render() == snapshot("table.footer[Note]")


def test_footer_renders_repeat_and_cells() -> None:
    footer = Footer(
        content=[
            Cell(Content("Note"), colspan=3),
        ],
        repeat=False,
    )

    assert footer.render() == snapshot(
        "table.footer(repeat: false,)[#table.cell(colspan: 3)[Note]]"
    )


def test_table_renders_arguments_headers_and_body() -> None:
    table = Table(
        columns="(auto, 1fr)",
        column_gutter="6pt",
        row_gutter="3pt",
        stroke="none",
        alignment="horizon",
        inset=Sides(x="3pt", y="1pt"),
        headers=[
            Header(
                content=[
                    Cell(Content("Item")),
                    Cell(Content("Value")),
                ]
            )
        ],
        body=[
            [Cell(Content("Alpha")), Cell(Content("10"))],
            [Cell(Content("Beta")), Cell(Content("20"))],
        ],
    )

    assert table.render() == snapshot(
        """\
#table(
  columns: (auto, 1fr),
  column-gutter: 6pt,
  row-gutter: 3pt,
  stroke: none,
  align: horizon,
  inset: (x: 3pt, y: 1pt),
  table.header[Item][Value],
  [Alpha], [10],
  [Beta], [20],
)
"""
    )


def test_table_renders_empty_body() -> None:
    table = Table(
        columns="2",
        headers=[
            Header(
                content=[
                    Cell(Content("Item")),
                    Cell(Content("Value")),
                ]
            )
        ],
    )

    assert table.render() == snapshot(
        """\
#table(
  columns: 2,
  table.header[Item][Value],
)
"""
    )


def test_table_renders_without_headers_or_body() -> None:
    table = Table(columns="2")

    assert table.render() == snapshot(
        """\
#table(
  columns: 2,
)
"""
    )


def test_table_renders_without_arguments_headers_or_body() -> None:
    table = Table()

    assert table.render() == snapshot("#table()\n")


def test_figure_renders_body_with_caption() -> None:
    figure = Figure(
        body=Table(body=[[Cell(Content("Alpha")), Cell(Content("10"))]]),
        caption="Totals #1",
    )

    assert figure.render() == snapshot(
        """\
#figure(caption: [Totals \\#1])[
  #table(
    [Alpha], [10],
  )
]
"""
    )
