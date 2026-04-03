from dataclasses import fields

import narwhals as nw
import narwhals.selectors as ncs
import pytest
from inline_snapshot import external, snapshot

from typ_tables import TypTable, locators, style


class TestAttributesMatch:
    def test_text_attrs_match(self):
        assert [f.name for f in fields(style.TextStyleForCell)] == [
            f.name for f in fields(style.TextStyle)
        ]

    def test_cell_attrs_match(self):
        assert [f.name for f in fields(style.CellStyleForCell)] == [
            f.name for f in fields(style.CellStyle)
        ]


class TestMergeStyles:
    def test_merge_cell_style(self):
        style_1 = style.CellStyleForCell(inset="10pt", align="auto")
        style_2 = style.CellStyleForCell(align="bottom")

        merged_style = style_1 | style_2

        assert merged_style.inset == "10pt"
        assert merged_style.align == "bottom"

    def test_merge_text_style(self):
        style_1 = style.TextStyleForCell(size="20pt", fill="red")
        style_2 = style.TextStyleForCell(fill="blue")

        merged_style = style_1 | style_2

        assert merged_style.size == "20pt"
        assert merged_style.fill == "blue"


class TestApplyStyle:
    def test_apply_no_style(self):
        content = "Test content"
        style_holder = style.StyleHolder()

        assert style_holder.to_typst(content) == snapshot("[Test content],")

    def test_apply_no_style_blank_stylers(self):
        content = "Test content"
        style_holder = style.StyleHolder(
            cell=style.CellStyleForCell(), text=style.TextStyleForCell()
        )

        assert style_holder.to_typst(content) == snapshot("[Test content],")

    def test_apply_cell_style(self):
        content = "Test content"
        cell_style = style.CellStyleForCell(align="right")
        style_holder = style.StyleHolder(cell=cell_style)

        assert style_holder.to_typst(content) == snapshot("""\
table.cell(
  align: right,
  [Test content],
),\
""")

    def test_apply_text_size_style(self):
        content = "Test content"
        text_style = style.TextStyleForCell(size="20pt")
        style_holder = style.StyleHolder(text=text_style)

        assert style_holder.to_typst(content) == snapshot("""\
text(
  size: 20pt,
)[Test content],\
""")

    def test_apply_text_fill_style(self):
        content = "Test content"
        text_style = style.TextStyleForCell(fill="red")
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

    def test_fill_header_based_on_expr_fails(self, basic_data) -> None:
        with pytest.raises(
            TypeError, match=r"Expected only scalars in style field: `fill` for this location."
        ):
            _ = TypTable(basic_data).tab_style(
                text=style.TextStyle(
                    fill=nw.when(nw.col("int") < 100).then(nw.lit("blue")).otherwise(nw.lit("red"))
                ),
                cell=style.CellStyle(
                    align=nw.when(nw.col("int") < 100)
                    .then(nw.lit("right"))
                    .otherwise(nw.lit("left"))
                ),
                locator=locators.LocHeader(),
            )


class TestStyleBody:
    def test_fill_body_red_align_right(self, table_check, basic_data) -> None:
        table = (
            TypTable(basic_data)
            .tab_style(
                text=style.TextStyle(fill="red"),
                cell=style.CellStyle(align="right"),
                locator=locators.LocBody(),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:fade75d3-ba9c-4836-b955-7edf2296a004.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_fill_body_based_on_expr(self, table_check, basic_data) -> None:
        table = (
            TypTable(basic_data)
            .tab_style(
                text=style.TextStyle(
                    fill=nw.when(nw.col("int") < 100).then(nw.lit("blue")).otherwise(nw.lit("red"))
                ),
                cell=style.CellStyle(
                    align=nw.when(nw.col("int") < 100)
                    .then(nw.lit("right"))
                    .otherwise(nw.lit("left"))
                ),
                locator=locators.LocBody(),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:efe8cbeb-53ef-4e0a-8424-c744bb08ba55.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_fill_body_based_on_list(self, table_check, basic_data) -> None:
        table = (
            TypTable(basic_data)
            .tab_style(
                text=style.TextStyle(fill=["red", "blue", "red", "yellow", "purple"]),
                cell=style.CellStyle(align=["left", "right", "top", "bottom", "horizon"]),
                locator=locators.LocBody(),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:3d67d5ea-6872-42c0-a4b8-92b16fc18398.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_fill_body_red_align_right_then_fill_numeric_blue(
        self, table_check, basic_data
    ) -> None:
        table = (
            TypTable(basic_data)
            .tab_style(
                text=style.TextStyle(fill="red"),
                cell=style.CellStyle(align="right"),
                locator=locators.LocBody(),
            )
            .tab_style(
                text=style.TextStyle(fill="blue"),
                locator=locators.LocBody(columns=ncs.numeric()),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:67393b35-f334-488d-8506-323e7efd5a97.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_fill_body_red_stub_column(self, table_check, group_data) -> None:
        table = (
            TypTable(group_data, rowname_col="fruit", groupname_col="group")
            .tab_style(
                text=style.TextStyle(fill="red"),
                # fruit is not in the body so nothing should happen.
                locator=locators.LocBody(columns="fruit"),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:ba104a36-efe8-40a6-a924-775284265054.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestStyleStub:
    def test_fill_stub_red(self, table_check, group_data) -> None:
        table = (
            TypTable(group_data, rowname_col="fruit", groupname_col="group")
            .tab_style(
                text=style.TextStyle(fill="red"),
                locator=locators.LocStub(),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:fd8bca6a-032b-47a8-9f84-c867d340f239.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_fill_stub_red_at_top(self, table_check, group_data) -> None:
        table = (
            TypTable(group_data, rowname_col="fruit", groupname_col="group")
            .tab_style(
                text=style.TextStyle(fill="red"),
                locator=locators.LocStub(rows=[0, 1]),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:6343032e-15db-4f4f-9396-9f702e95f76e.typ")

        warnings = table_check(result)

        assert len(warnings) == 0
