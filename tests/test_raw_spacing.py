from piperg2p.raw_blocks import (
    RawPhonemeSegment,
    TextSegment,
    compose_raw_segments,
    needs_left_boundary_space,
    needs_right_boundary_space,
    parse_raw_blocks,
)


def phonemize(text: str):
    return [[*text]] if text else []


def test_raw_block_boundary_spacing_is_source_preserving():
    cases = {
        "ab [[c]] d": ["a", "b", " ", "c", " ", "d"],
        "ab [[c]]d": ["a", "b", " ", "c", "d"],
        "ab[[c]] d": ["a", "b", "c", " ", "d"],
        "ab[[c]]d": ["a", "b", "c", "d"],
    }
    for text, expected in cases.items():
        assert compose_raw_segments(parse_raw_blocks(text), phonemize) == [expected]


def test_raw_segments_keep_offsets_for_shared_compositor():
    segments = parse_raw_blocks("ab [[ c ]] d")
    assert segments == [TextSegment("ab "), RawPhonemeSegment("c"), TextSegment(" d")]
    assert (segments[0].source_start, segments[0].source_end) == (0, 3)
    assert (segments[1].source_start, segments[1].source_end) == (3, 10)
    assert (segments[2].source_start, segments[2].source_end) == (10, 12)


def test_boundary_helpers_detect_explicit_source_whitespace():
    assert needs_left_boundary_space("ab ", "c")
    assert needs_right_boundary_space("c", " d")
    assert not needs_left_boundary_space("ab", "c")
