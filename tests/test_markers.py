from piperg2p import apply_marker_overrides, parse_delimited


def test_parse_delimited_preserves_clean_offsets_and_escapes():
    clean, ranges, warnings = parse_delimited(r"Use @tea@ and \@literal\@")
    assert clean == "Use tea and @literal@"
    assert ranges == [(4, 7)]
    assert warnings == []


def test_marker_assignments_support_ordinals_and_sequences():
    ranges = [(0, 3), (4, 7)]
    assert [item.attrs["lang"] for item in apply_marker_overrides("one two", ranges, {2: {"lang": "de"}})] == ["de"]
    assert [item.attrs["ph"] for item in apply_marker_overrides("one two", ranges, [{"ph": "a"}, {"ph": "b"}])] == ["a", "b"]


def test_unmatched_marker_is_reported():
    clean, ranges, warnings = parse_delimited("open @marker")
    assert clean == "open @marker"
    assert ranges == []
    assert "Unmatched opening marker" in warnings[0]
