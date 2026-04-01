from inline_snapshot import external, snapshot

from typ_tables import TypTable, locators, style


class TestApplyStyle:
    def test_apply_no_style(self):
        content = "Test content"
        style_holder = style.StyleHolder()

        assert style_holder.to_typst(content) == snapshot("[Test content],")

    def test_apply_no_style_blank_stylers(self):
        content = "Test content"
        style_holder = style.StyleHolder(cell=style.CellStyle(), text=style.TextStyle())

        assert style_holder.to_typst(content) == snapshot("[Test content],")

    def test_apply_cell_style(self):
        content = "Test content"
        cell_style = style.CellStyle(align="right")
        style_holder = style.StyleHolder(cell=cell_style)

        assert style_holder.to_typst(content) == snapshot("""\
table.cell(
  align: right,
  [Test content],
),\
""")

    def test_apply_text_size_style(self):
        content = "Test content"
        text_style = style.TextStyle(size="20pt")
        style_holder = style.StyleHolder(text=text_style)

        assert style_holder.to_typst(content) == snapshot("""\
text(
  size: 20pt,
)[Test content],\
""")

    def test_apply_text_fill_style(self):
        content = "Test content"
        text_style = style.TextStyle(fill="red")
        style_holder = style.StyleHolder(text=text_style)

        assert style_holder.to_typst(content) == snapshot("""\
text(
  fill: red,
)[Test content],\
""")


class TestStyleHeader:
    def test_align_to_right(self, table_check, basic_data) -> None:
        table = (
            TypTable(basic_data)
            .tab_style(cell=style.CellStyle(align="right"), locator=locators.LocHeader())
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:9b8c38d9-61f4-4ae3-aea7-6491de7ccc07.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_inset_top_bottom(self, table_check, basic_data) -> None:
        table = (
            TypTable(basic_data)
            .tab_style(
                cell=style.CellStyle(inset=style.Sides(top="10pt", bottom="10pt")),
                locator=locators.LocHeader(),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:4f62791f-a517-4c0a-88c5-c220988cdc50.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_increase_text_size(self, table_check, basic_data) -> None:
        table = (
            TypTable(basic_data)
            .tab_style(text=style.TextStyle(size="20pt"), locator=locators.LocHeader())
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:39118e75-eb5e-4991-ab8d-bab8252da367.typ")

        warnings = table_check(result)

        assert len(warnings) == 0
