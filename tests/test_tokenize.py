from piperg2p import tokenize


def test_tokenize_is_source_aligned_and_keeps_internal_word_punctuation():
    tokens = tokenize("l’été well-being, café\u0301!")
    assert [(token.text, token.char_start, token.char_end) for token in tokens] == [
        ("l’été", 0, 5),
        ("well-being", 6, 16),
        (",", 16, 17),
        ("café\u0301", 18, 23),
        ("!", 23, 24),
    ]
    assert [token.text for token in tokenize("hello, world", keep_punct=False)] == [
        "hello",
        "world",
    ]
