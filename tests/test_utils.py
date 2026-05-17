from typ_tables._utils import OrderedSet


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
