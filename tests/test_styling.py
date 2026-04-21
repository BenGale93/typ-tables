from dataclasses import fields

import narwhals as nw
import narwhals.selectors as ncs
import polars as pl
import pytest
from inline_snapshot import external, snapshot

from typ_tables import Sides, TypTable, locators, style


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

    def test_merge_text_style_with_sides(self):
        style_1 = style.TextStyleForCell(stroke=style.Sides(bottom="1pt"))
        style_2 = style.TextStyleForCell(stroke=style.Sides(right="1pt"))

        merged_style = style_1 | style_2

        assert merged_style.stroke == style.Sides(right="1pt", bottom="1pt")

    def test_merge_style_holder_none_is_replaced(self):
        holder_1 = style.StyleHolder(text=None, cell=None)
        holder_2 = style.StyleHolder(
            text=style.TextStyleForCell(font="test"), cell=style.CellStyleForCell(align="end")
        )

        new_holder = holder_1 | holder_2

        assert holder_2 == new_holder

    def test_merge_style_holder_default_and_none(self):
        holder_1 = style.StyleHolder(
            text=style.TextStyleForCell(font="test"), cell=style.CellStyleForCell(align="end")
        )
        holder_2 = style.StyleHolder(text=None, cell=None)

        new_holder = holder_1 | holder_2

        assert holder_1 == new_holder

    def test_merge_style_holder_recursive_merge(self):
        holder_1 = style.StyleHolder(
            text=style.TextStyleForCell(weight="bold"), cell=style.CellStyleForCell(fill="red")
        )
        holder_2 = style.StyleHolder(
            text=style.TextStyleForCell(font="test"), cell=style.CellStyleForCell(align="end")
        )

        new_holder = holder_1 | holder_2

        assert new_holder.text == style.TextStyleForCell(font="test", weight="bold")
        assert new_holder.cell == style.CellStyleForCell(align="end", fill="red")


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


class TestCellStyle:
    def test_coerce_inset_dict(self):
        cell_style = style.CellStyle(inset={"x": "10pt", "y": "20pt"})

        assert isinstance(cell_style.inset, style.Sides)
        assert cell_style.inset.x == "10pt"
        assert cell_style.inset.y == "20pt"

    def test_coerce_inset_list_dict(self):
        cell_style = style.CellStyle(inset=[{"x": "10pt", "y": "20pt"}, {"top": "30pt"}])

        assert isinstance(cell_style.inset, list)
        sides_a = cell_style.inset[0]
        sides_b = cell_style.inset[1]

        assert isinstance(sides_a, style.Sides)
        assert sides_a.x == "10pt"
        assert sides_a.y == "20pt"

        assert isinstance(sides_b, style.Sides)
        assert sides_b.top == "30pt"


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

    def test_change_top_border(self, table_check, basic_data) -> None:
        table = (
            TypTable(basic_data)
            .tab_style(cell=style.CellStyle(stroke="(top: blue)"), locator=locators.LocHeader())
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:dce36646-a219-460e-84d7-d72d78fb2b64.typ")

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


class TestStyleRowGroup:
    def test_fill_row_group_red(self, table_check, group_data) -> None:
        table = (
            TypTable(group_data, rowname_col="fruit", groupname_col="group")
            .tab_style(
                text=style.TextStyle(fill="red"),
                locator=locators.LocRowGroup(),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:4345a4f0-2d5a-4d89-af4c-c30d7b6e257a.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_fill_specific_row_group_red(self, table_check, group_data) -> None:
        table = (
            TypTable(group_data, rowname_col="fruit", groupname_col="group")
            .tab_style(
                text=style.TextStyle(fill="red"),
                locator=locators.LocRowGroup(group="group_a"),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:6d836139-467f-490c-bb31-d179b2864e71.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_fill_specific_row_groups_red(self, table_check, group_data) -> None:
        table = (
            TypTable(group_data, rowname_col="fruit", groupname_col="group")
            .tab_style(
                text=style.TextStyle(fill="red"),
                locator=locators.LocRowGroup(group=["group_b"]),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:94bd8900-5432-4e14-8fe2-cdbdcfabfb35.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_fill_row_groups_red_and_format(self, table_check, group_data) -> None:
        table = (
            TypTable(group_data, rowname_col="fruit", groupname_col="group")
            .tab_style(
                text=style.TextStyle(fill="red"),
                locator=locators.LocRowGroup(),
            )
            .fmt(columns="group", f_string="${}$")
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:b393a321-59cd-43a5-8cb5-3c9ed3101014.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_style_row_group_none_set(self, table_check, group_data) -> None:
        table = (
            TypTable(group_data)
            .tab_style(
                text=style.TextStyle(fill="red"),
                locator=locators.LocRowGroup(),
            )
            .tab_header("Table Header")
        )
        with pytest.warns(
            UserWarning, match=r"Row-group style locator was used but no row-group was set."
        ):
            result = table.to_typst()

        assert result == external("uuid:907dfd32-eed8-4d8f-88a7-99cb7647ba55.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestStyleColumnLabels:
    def test_fill_column_labels(self, table_check, basic_data) -> None:
        table = (
            TypTable(basic_data)
            .tab_style(
                text=style.TextStyle(fill="blue"),
                locator=locators.LocColumnLabels(columns=ncs.numeric()),
            )
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:a320710c-9285-46cb-9e07-2efeae2333f7.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestStyleStubhead:
    def test_fill_stub_head(self, table_check, group_data) -> None:
        table = (
            TypTable(group_data, rowname_col="fruit", groupname_col="group")
            .tab_style(
                text=style.TextStyle(fill="blue"),
                locator=locators.LocStubhead(),
            )
            .tab_stubhead("Test")
            .tab_header("Table Header")
        )
        result = table.to_typst()

        assert result == external("uuid:e16f9236-bae2-43fa-a5df-b3b98d644f5d.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestSetInset:
    def test_inset_dict(self, table_check, basic_data):
        table = (
            TypTable(basic_data)
            .set_table_inset({"top": "10pt", "bottom": "2pt", "rest": "0% + 5pt"})
            .tab_header("Test Header")
        )
        result = table.to_typst()

        assert result == external("uuid:06d9a14e-f284-4f9a-9ad2-88922da8b5e9.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_inset_sides(self, table_check, basic_data):
        table = (
            TypTable(basic_data)
            .set_table_inset(Sides(top="10pt", bottom="2pt", rest="0% + 5pt"))
            .tab_header("Test Header")
        )
        result = table.to_typst()

        assert result == external("uuid:3fb2f1a4-15db-461e-9c47-fbbecb697036.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


def test_apply_multiple_text_styles(table_check, basic_data) -> None:
    table = (
        TypTable(basic_data)
        .tab_style(
            text=style.TextStyle(fill="red"),
            locator=locators.LocBody(rows=0, columns="string"),
        )
        .tab_style(
            text=style.TextStyle(font="FreeMono"),
            locator=locators.LocBody(rows=1, columns="string"),
        )
        .tab_style(
            text=style.TextStyle(style="italic"),
            locator=locators.LocBody(rows=2, columns="string"),
        )
        .tab_style(
            text=style.TextStyle(weight="extrabold"),
            locator=locators.LocBody(rows=3, columns="string"),
        )
        .tab_style(
            text=style.TextStyle(weight=150),
            locator=locators.LocBody(rows=4, columns="string"),
        )
        .tab_style(
            text=style.TextStyle(stretch="200%"),
            locator=locators.LocBody(rows=0, columns="int"),
        )
        .tab_style(
            text=style.TextStyle(stroke="2pt + red"),
            locator=locators.LocBody(rows=1, columns="int"),
        )
        .tab_style(
            text=style.TextStyle(tracking="1.5pt"),
            locator=locators.LocBody(rows=2, columns="int"),
        )
        .tab_style(
            text=style.TextStyle(spacing="200%"),
            locator=locators.LocHeader(),
        )
        .tab_header("Table Header")
    )

    result = table.to_typst()

    assert result == external("uuid:6b8ceccf-a7e6-417d-aead-f27ade6af900.typ")

    warnings = table_check(result)

    assert len(warnings) == 0


def test_test_fractions(table_check) -> None:
    data = pl.DataFrame({"Fractions": ["1/2", "1/3"]})
    table = (
        TypTable(data)
        .tab_style(
            text=style.TextStyle(fractions=True),
            locator=locators.LocBody(),
        )
        .tab_header("Table Header")
    )

    result = table.to_typst()

    assert result == external("uuid:5447bc09-92ed-4a1e-babb-2719b59a54d2.typ")

    warnings = table_check(result)

    assert len(warnings) == 0


def test_apply_multiple_cell_styles(table_check, basic_data) -> None:
    table = (
        TypTable(basic_data)
        .tab_style(
            cell=style.CellStyle(inset="1pt"),
            locator=locators.LocBody(rows=0, columns="string"),
        )
        .tab_style(
            cell=style.CellStyle(align="right"),
            locator=locators.LocBody(rows=1, columns="string"),
        )
        .tab_style(
            cell=style.CellStyle(fill="red"),
            locator=locators.LocBody(rows=2, columns="string"),
        )
        .tab_style(
            cell=style.CellStyle(stroke="2pt + blue"),
            locator=locators.LocBody(rows=3, columns="string"),
        )
        .tab_style(
            cell=style.CellStyle(stroke={"bottom": "1pt + red"}),
            locator=locators.LocBody(rows=4, columns="string"),
        )
        .tab_header("Table Header")
    )

    result = table.to_typst()

    assert result == external("uuid:799a8d78-754f-4475-ae73-a067ac194699.typ")

    warnings = table_check(result)

    assert len(warnings) == 0


def test_clear_style(table_check, basic_data):
    table = TypTable(basic_data).clear_defaults().tab_header("Table Header")

    result = table.to_typst()

    assert result == external("uuid:18e3eacb-9137-4f4a-9b64-6229932c8ab2.typ")

    warnings = table_check(result)

    assert len(warnings) == 0
