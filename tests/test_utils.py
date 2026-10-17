from typ_tables._escape import Typst, escape_value, formatted
from typ_tables._utils import OrderedSet


class TestEscapeValue:
    def test_plain_string_escapes_special_characters(self):
        assert escape_value("A <label> #ref") == "A \\<label\\> \\#ref"

    def test_non_string_values_are_stringified(self):
        assert escape_value(42) == "42"

    def test_typst_values_are_passed_through(self):
        assert escape_value(Typst("#strong[x]")) == "#strong[x]"

    def test_single_formatted_region_is_preserved_raw(self):
        assert escape_value(formatted("$1,234")) == "$1,234"

    def test_text_around_a_formatted_region_is_escaped(self):
        value = f"a #b {formatted('$1')} c @d"

        assert escape_value(value) == "a \\#b $1 c \\@d"

    def test_multiple_formatted_regions_are_all_preserved(self):
        value = f"{formatted('$1')} and {formatted('$2')}"

        assert escape_value(value) == "$1 and $2"

    def test_unmatched_start_marker_is_escaped_instead_of_raising(self):
        assert escape_value("x <typst> y") == "x \\<typst\\> y"

    def test_unmatched_end_marker_is_escaped_instead_of_raising(self):
        assert escape_value("x </typst> y") == "x \\<\\/typst\\> y"

    def test_end_marker_before_start_marker_is_escaped(self):
        assert escape_value("</typst>x<typst>y") == "\\<\\/typst\\>x\\<typst\\>y"

    def test_stray_end_marker_after_a_valid_region_is_escaped(self):
        value = f"{formatted('$1')} trailing</typst>"

        assert escape_value(value) == "$1 trailing\\<\\/typst\\>"


class TestOrderedSet:
    def test_as_list_preserves_first_seen_order(self):
        ordered_set = OrderedSet(["beta", "alpha", "beta", "gamma", "alpha"])

        assert ordered_set.as_list() == ["beta", "alpha", "gamma"]

    def test_as_set_returns_plain_set(self):
        ordered_set = OrderedSet(["beta", "alpha", "beta"])

        result = ordered_set.as_set()

        assert result == {"alpha", "beta"}
        assert type(result) is set

    def test_as_dict_returns_plain_dict_with_true_values(self):
        ordered_set = OrderedSet(["beta", "alpha", "beta"])

        result = ordered_set.as_dict()

        assert result == {"beta": True, "alpha": True}
        assert type(result) is dict

    def test_contains_checks_membership(self):
        ordered_set = OrderedSet(["alpha", "beta"])

        assert "alpha" in ordered_set
        assert "gamma" not in ordered_set

    def test_iterates_in_first_seen_order(self):
        ordered_set = OrderedSet(["beta", "alpha", "beta", "gamma"])

        assert list(ordered_set) == ["beta", "alpha", "gamma"]

    def test_len_counts_unique_items(self):
        ordered_set = OrderedSet(["beta", "alpha", "beta", "gamma"])

        assert len(ordered_set) == 3

    def test_repr_shows_ordered_values(self):
        ordered_set = OrderedSet(["beta", "alpha", "beta"])

        assert repr(ordered_set) == "OrderedSet(['beta', 'alpha'])"

    def test_empty_ordered_set(self):
        ordered_set = OrderedSet()

        assert ordered_set.as_list() == []
        assert ordered_set.as_set() == set()
        assert ordered_set.as_dict() == {}
        assert len(ordered_set) == 0
