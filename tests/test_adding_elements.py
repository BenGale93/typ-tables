from inline_snapshot import external

from typ_tables import Typst, TypTable


class TestTabHeader:
    def test_string_title(self, table_check, basic_data) -> None:
        table = TypTable(basic_data).tab_header(title="Title Here")
        result = table.to_typst()

        assert result == external("uuid:b93906cf-393c-4e3e-b988-4d5c77de27b2.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_typst_title(self, table_check, basic_data) -> None:
        table = TypTable(basic_data).tab_header(title=Typst("_Title Here_"))
        result = table.to_typst()

        assert result == external("uuid:2f92128f-4518-476e-a234-a3dc1c1f4c82.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_string_title_and_subtitle(self, table_check, basic_data) -> None:
        table = TypTable(basic_data).tab_header(title="Title Here", subtitle="Subtitle here")
        result = table.to_typst()

        assert result == external("uuid:a5494390-6b07-4388-8123-18ac44b5356b.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestTabFigure:
    def test_string_caption(self, table_check, basic_data) -> None:
        table = TypTable(basic_data).tab_figure(caption="Caption Here")
        result = table.to_typst()

        assert result == external("uuid:15718cad-d93d-4cbe-b576-728b5db06a15.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_typst_caption(self, table_check, basic_data) -> None:
        table = TypTable(basic_data).tab_figure(caption=Typst("_Caption Here_"))
        result = table.to_typst()

        assert result == external("uuid:f1f82a2a-2cbf-4e59-95d2-8599f7b323ed.typ")

        warnings = table_check(result)

        assert len(warnings) == 0


class TestTabFooter:
    def test_string_note(self, table_check, basic_data) -> None:
        table = TypTable(basic_data).tab_footer(note="Note here")
        result = table.to_typst()

        assert result == external("uuid:daba0a3e-ef91-40a3-8111-3e98b003dbee.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_typst_note(self, table_check, basic_data) -> None:
        table = TypTable(basic_data).tab_footer(note=Typst("#underline[Note here]"))
        result = table.to_typst()

        assert result == external("uuid:85c090a2-6e48-4918-989b-7902237a5a9f.typ")

        warnings = table_check(result)

        assert len(warnings) == 0

    def test_multiple_notes(self, table_check, basic_data) -> None:
        table = (
            TypTable(basic_data)
            .tab_footer(note=Typst("#underline[Note here]"))
            .tab_footer(note="Another note")
        )
        result = table.to_typst()

        assert result == external("uuid:26c6d1d2-6eb8-4393-a5b7-cad03629ff0a.typ")

        warnings = table_check(result)

        assert len(warnings) == 0
