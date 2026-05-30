import pytest
from inline_snapshot import external, snapshot

from typ_tables import TypTable, _style
from typ_tables._rendering import Cell, Content
from typ_tables._spanners import Spanner, SpannerCell, Spanners
from typ_tables._style import CellStyleForCell


class TestSpannerCell:
    def test_to_typst_labeled_cell_uses_stroke_for_bottom_rule(self):
        cell = SpannerCell(label="Numeric", id_="numeric", colspan=2)
        style_holder = _style.StyleHolder(
            cell=_style.CellStyleForCell(align="center", stroke="1.2pt")
        )

        assert cell.to_typst(style_holder) == snapshot(
            Cell(
                content=Content(
                    value="""\

  Numeric
  #v(5pt)
  #place(bottom + center, line(length: 100%, stroke: 1.2pt))\
"""
                ),
                colspan=2,
                cell_style=CellStyleForCell(align="center"),
            )
        )

    def test_to_typst_labeled_cell_uses_only_bottom_stroke_for_rule(self):
        cell = SpannerCell(label="Numeric", id_="numeric", colspan=2)
        style_holder = _style.StyleHolder(
            cell=_style.CellStyleForCell(
                align="center",
                stroke=_style.Sides(top="0.5pt", right="2pt", bottom="1.2pt"),
            )
        )

        assert cell.to_typst(style_holder) == snapshot(
            Cell(
                content=Content(
                    value="""\

  Numeric
  #v(5pt)
  #place(bottom + center, line(length: 100%, stroke: 1.2pt))\
"""
                ),
                colspan=2,
                cell_style=CellStyleForCell(align="center"),
            )
        )

    def test_to_typst_escapes_special_characters_in_label(self):
        cell = SpannerCell(label="Growth #1 [net]", id_="growth", colspan=2)
        style_holder = _style.StyleHolder(
            cell=_style.CellStyleForCell(align="center", stroke="1.2pt")
        )

        assert cell.to_typst(style_holder) == snapshot(
            Cell(
                content=Content(
                    value="""\

  Growth \\#1 \\[net\\]
  #v(5pt)
  #place(bottom + center, line(length: 100%, stroke: 1.2pt))\
"""
                ),
                colspan=2,
                cell_style=CellStyleForCell(align="center"),
            )
        )

    def test_to_typst_blank_cell_drops_stroke(self):
        cell = SpannerCell(label="", id_=None, colspan=1)
        style_holder = _style.StyleHolder(
            cell=_style.CellStyleForCell(align="center", stroke="1.2pt")
        )

        assert cell.to_typst(style_holder) == snapshot(
            Cell(content=Content(value=""), cell_style=CellStyleForCell(align="center"))
        )

    def test_to_typst_labeled_cell_without_cell_style_uses_no_rule_stroke(self):
        cell = SpannerCell(label="Numeric", id_="numeric", colspan=2)
        style_holder = _style.StyleHolder()

        assert cell.to_typst(style_holder) == snapshot(
            Cell(
                content=Content(
                    value="""\

  Numeric
  #v(5pt)
  #place(bottom + center, line(length: 100%, stroke: none))\
"""
                ),
                colspan=2,
            )
        )


class TestSpanners:
    def test_spanner_id_defaults_to_label_string(self):
        spanner = Spanner.from_data(label="Date", spanning=["Year", "Month", "Day"])

        assert spanner.id_ == "Date"

    def test_add_single_spanner(self):
        spanners = Spanners()
        spanner = Spanner.from_data(label="Date", spanning=["Year", "Month", "Day"])

        spanners.add_spanner(spanner)

        assert spanners.get_spanner_by_id("Date")[0] == 0

    def test_add_single_spanner_specific_level(self):
        spanners = Spanners()
        spanner = Spanner.from_data(label="Date", spanning=["Year", "Month", "Day"])

        spanners.add_spanner(spanner, level=1)

        assert spanners.get_spanner_by_id("Date")[0] == 1

    def test_add_two_disjoint_spanners(self):
        spanners = Spanners()
        spanner_1 = Spanner.from_data(label="Date", spanning=["Year", "Month", "Day"])
        spanner_2 = Spanner.from_data(label="Measurement", spanning=["Wind", "Temp"])

        spanners.add_spanner(spanner_1)
        spanners.add_spanner(spanner_2)

        assert spanners.get_spanner_by_id("Date")[0] == 0
        assert spanners.get_spanner_by_id("Measurement")[0] == 0

    def test_add_spanner_spanner(self):
        spanners = Spanners()
        spanner_1 = Spanner.from_data(label="Date", spanning=["Year", "Month", "Day"])
        spanner_2 = Spanner.from_data(label="Measurement", spanning=["Wind", "Temp"])
        spanner_3 = Spanner.from_data(
            label="Top", spanning=["Year", "Month", "Day", "Wind", "Temp"]
        )

        spanners.add_spanner(spanner_1)
        spanners.add_spanner(spanner_2)
        spanners.add_spanner(spanner_3)

        assert spanners.get_spanner_by_id("Top")[0] == 1

    def test_add_three_overlapping_spanners(self):
        spanners = Spanners()
        spanner_1 = Spanner.from_data(label="hp", spanning=["hp", "hp_rpm"])
        spanner_2 = Spanner.from_data(
            label="performance", spanning=["hp", "hp_rpm", "trq", "trq_rpm"]
        )
        spanner_3 = Spanner.from_data(label="trq", spanning=["trq", "trq_rpm"])

        spanners.add_spanner(spanner_1)
        spanners.add_spanner(spanner_2)
        spanners.add_spanner(spanner_3)

        assert spanners.get_spanner_by_id("hp")[0] == 0
        assert spanners.get_spanner_by_id("performance")[0] == 1
        assert spanners.get_spanner_by_id("trq")[0] == 2  # order dependent

    def test_add_spanner_under_existing_spanner(self):
        spanners = Spanners()
        spanner_1 = Spanner.from_data(label="hp", spanning=["hp", "hp_rpm"])
        spanner_2 = Spanner.from_data(
            label="performance", spanning=["hp", "hp_rpm", "trq", "trq_rpm"]
        )
        spanner_3 = Spanner.from_data(label="trq", spanning=["trq", "trq_rpm"])

        spanners.add_spanner(spanner_1)
        spanners.add_spanner(spanner_2)
        spanners.add_spanner(spanner_3, level=0)

        assert spanners.get_spanner_by_id("hp")[0] == 0
        assert spanners.get_spanner_by_id("performance")[0] == 1
        assert spanners.get_spanner_by_id("trq")[0] == 0

    def test_add_spanner_under_existing_spanner_with_overlap(self):
        spanners = Spanners()
        spanner_1 = Spanner.from_data(label="hp", spanning=["hp", "hp_rpm"])
        spanner_2 = Spanner.from_data(
            label="performance", spanning=["hp", "hp_rpm", "trq", "trq_rpm"]
        )
        spanner_3 = Spanner.from_data(label="trq", spanning=["hp_rpm", "trq", "trq_rpm"])

        spanners.add_spanner(spanner_1)
        spanners.add_spanner(spanner_2)
        spanners.add_spanner(spanner_3, level=0)

        hp_level, hp = spanners.get_spanner_by_id("hp")

        assert hp_level == 0
        assert hp.spanning == ["hp"]
        assert spanners.get_spanner_by_id("performance")[0] == 1
        assert spanners.get_spanner_by_id("trq")[0] == 0

    def test_reject_negative_level(self):
        spanners = Spanners()
        spanner = Spanner.from_data(label="Date", spanning=["Year", "Month", "Day"])

        with pytest.raises(ValueError, match="Level may not be negative"):
            spanners.add_spanner(spanner, level=-1)

    def test_reject_duplicate_spanner_id(self):
        spanners = Spanners()

        spanners.add_spanner(Spanner.from_data(label="Date", spanning=["Year"]))

        with pytest.raises(ValueError, match="Spanner id 'Date' already exists"):
            spanners.add_spanner(Spanner.from_data(label="Date", spanning=["Month"]))

    def test_get_columns_deduplicates_overlapping_spanners_in_order(self):
        spanners = Spanners()
        spanners.add_spanner(Spanner.from_data(label="First", spanning=["a", "b", "c"]))
        spanners.add_spanner(Spanner.from_data(label="Second", spanning=["b", "d"]))

        columns = spanners.get_columns(["Second", "First"]).as_list()

        assert columns == ["a", "b", "c", "d"]

    def test_get_columns_rejects_unknown_spanner_id(self):
        spanners = Spanners()
        spanners.add_spanner(Spanner.from_data(label="First", spanning=["a", "b", "c"]))

        with pytest.raises(ValueError, match="Spanner ids not found: \\['Second'\\]"):
            spanners.get_columns(["First", "Second"])

    def test_clear_blank_spanners_removes_empty_levels(self):
        spanners = Spanners()

        spanners.add_spanner(Spanner.from_data(label="Blank", spanning=[]), level=0)

        assert spanners.build_spanners(["a"]) == []

    def test_build_spanners_adds_blank_cell_after_spanner(self):
        spanners = Spanners()
        spanners.add_spanner(Spanner.from_data(label="First", spanning=["a"]))

        spanner_rows = spanners.build_spanners(["a", "b"])

        assert spanner_rows == [
            [
                SpannerCell(label="First", id_="First", colspan=1),
                SpannerCell(label="", id_=None, colspan=1),
            ]
        ]

    def test_build_spanners_handles_empty_columns_for_multiple_levels(self):
        spanners = Spanners()
        spanners.add_spanner(Spanner.from_data(label="First", spanning=["a"]), level=0)
        spanners.add_spanner(Spanner.from_data(label="Second", spanning=["b"]), level=1)

        spanner_rows = spanners.build_spanners([])

        assert spanner_rows == [[], []]

    def test_add_spanner_under_existing_spanner_with_total_overlap(self):
        spanners = Spanners()
        spanner_1 = Spanner.from_data(label="hp", spanning=["hp", "hp_rpm"])
        spanner_2 = Spanner.from_data(
            label="performance", spanning=["hp", "hp_rpm", "trq", "trq_rpm"]
        )
        spanner_3 = Spanner.from_data(label="trq", spanning=["hp", "hp_rpm", "trq", "trq_rpm"])

        spanners.add_spanner(spanner_1)
        spanners.add_spanner(spanner_2)
        spanners.add_spanner(spanner_3, level=0)

        with pytest.raises(ValueError, match=r"'hp' not found"):
            spanners.get_spanner_by_id("hp")
        assert spanners.get_spanner_by_id("performance")[0] == 1
        assert spanners.get_spanner_by_id("trq")[0] == 0


class TestTabSpanner:
    def test_basic_spanner(self, table_check, basic_data):
        table = TypTable(basic_data).tab_spanner("Numeric", columns=["float", "int"])
        result = table.to_typst()

        assert result == external("uuid:60b5c6ca-6af7-4469-bbf3-c704c9f2fe14.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_two_disjoint_spanners(self, table_check, basic_data):
        table = (
            TypTable(basic_data)
            .tab_spanner("Numeric", columns=["float", "int"])
            .tab_spanner("Not Numeric", columns="string")
        )
        result = table.to_typst()

        assert result == external("uuid:5096f477-c50f-4cb0-bf3e-2bd403decc17.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_spanner_with_stub_column(self, table_check, group_data):
        table = TypTable(group_data, rowname_col="fruit").tab_spanner("Counts", columns="count")

        result = table.to_typst()

        assert result == external("uuid:c4e7e64d-dc37-4d59-8683-c466c5f32bda.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_spanner_with_stub_and_row_group_columns(self, table_check, group_data):
        table = TypTable(group_data, rowname_col="fruit", groupname_col="group").tab_spanner(
            "Counts", columns="count"
        )

        result = table.to_typst()

        assert result == external("uuid:1aadb6f3-4658-4fee-ae48-9a9c1e025b55.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_spanner_over_stub_column(self, table_check, group_data):
        table = TypTable(group_data, rowname_col="fruit").tab_spanner(
            "Counts", columns=["fruit", "count"]
        )

        result = table.to_typst()

        assert result == external("uuid:3eca71bd-51b6-493c-bdc6-553945239abb.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_spanner_over_stub_and_row_group_columns(self, table_check, group_data):
        table = TypTable(group_data, rowname_col="fruit", groupname_col="group").tab_spanner(
            "Counts", columns=["group", "count"]
        )

        result = table.to_typst()

        assert result == external("uuid:7cd67b61-1ea3-4609-93b7-15d683eb4612.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_requires_columns_or_spanners(self, basic_data):
        table = TypTable(basic_data)

        with pytest.raises(NotImplementedError, match="columns/spanners must be specified"):
            table.tab_spanner("Empty")

    def test_gather_moves_directly_selected_columns_together(self, basic_data):
        table = TypTable(basic_data).tab_spanner("Numeric", columns=["float", "int"])

        assert [col.var for col in table._typ_data.boxhead] == ["string", "float", "int"]

    def test_gather_false_preserves_column_order(self, basic_data):
        table = TypTable(basic_data).tab_spanner("Numeric", columns=["float", "int"], gather=False)

        assert [col.var for col in table._typ_data.boxhead] == ["string", "int", "float"]

    def test_higher_level_spanner_from_existing_spanners(self, basic_data):
        table = (
            TypTable(basic_data)
            .tab_spanner("Integers", columns="int", id_="ints")
            .tab_spanner("Floats", columns="float", id_="floats")
            .tab_spanner("Numeric", spanners=["ints", "floats"])
        )

        numeric_level, numeric = table._typ_data.spanners.get_spanner_by_id("Numeric")

        assert numeric_level == 1
        assert numeric.spanning == ["int", "float"]
        assert [col.var for col in table._typ_data.boxhead] == ["string", "int", "float"]

    def test_higher_level_spanner_accepts_spanner_and_column_string(self, basic_data):
        table = (
            TypTable(basic_data)
            .tab_spanner("Numeric", columns=["float", "int"], id_="numeric")
            .tab_spanner("All values", spanners="numeric", columns="string")
        )

        top_level, top = table._typ_data.spanners.get_spanner_by_id("All values")

        assert top_level == 1
        assert top.spanning == ["string", "float", "int"]

    def test_custom_ids_allow_repeated_labels(self, basic_data):
        table = (
            TypTable(basic_data)
            .tab_spanner("Value", columns="int", id_="integer-value")
            .tab_spanner("Value", columns="float", id_="float-value")
        )

        assert table._typ_data.spanners.get_ids() == {"integer-value", "float-value"}

    def test_rejects_duplicate_default_label_id(self, basic_data):
        table = TypTable(basic_data).tab_spanner("Value", columns="int")

        with pytest.raises(ValueError, match="Spanner id 'Value' already exists"):
            table.tab_spanner("Value", columns="float")
