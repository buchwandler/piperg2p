from piperg2p.lexicons.spans import SourceSpan, scan_source_spans, word_spans


def test_source_scanner_preserves_nonword_text_and_offsets():
    text = "Hi, naïve-world!"
    spans = scan_source_spans(text)
    assert spans == (
        SourceSpan("Hi", 0, 2, "word"),
        SourceSpan(", ", 2, 4, "other"),
        SourceSpan("naïve-world", 4, 15, "word"),
        SourceSpan("!", 15, 16, "other"),
    )


def test_word_scanner_handles_numbers_combining_marks_and_apostrophes():
    text = "v2 l'été cafe\u0301 123"
    assert [span.text for span in word_spans(text)] == ["v2", "l'été", "café", "123"]


def test_hyphen_is_internal_only_when_surrounded_by_word_characters():
    assert [span.text for span in word_spans("well-being - done-")] == [
        "well-being",
        "done",
    ]
