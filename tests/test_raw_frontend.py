from dataclasses import dataclass

from piperg2p import PiperFrontend, VoiceConfig
from piperg2p.raw_blocks import (
    RawPhonemeSegment,
    TextSegment,
    compose_raw_segments,
    parse_raw_blocks,
)


@dataclass
class FakeBackend:
    def phonemize(self, text: str, *, voice: str):
        del voice
        return [[character for character in text]] if text else []

    def close(self):
        pass


def config():
    return VoiceConfig.from_dict(
        {
            "num_symbols": 20,
            "num_speakers": 1,
            "audio": {"sample_rate": 22050},
            "phoneme_type": "espeak",
            "phoneme_id_map": {
                "_": 0,
                "^": 1,
                "$": 2,
                **{chr(97 + i): 3 + i for i in range(17)},
            },
        }
    )


def test_raw_parser_preserves_order_and_unmatched_delimiters():
    assert parse_raw_blocks("a[[ ɹ ]]b") == [
        TextSegment("a"),
        RawPhonemeSegment("ɹ"),
        TextSegment("b"),
    ]
    assert parse_raw_blocks("a [[ unmatched") == [TextSegment("a [[ unmatched")]
    assert parse_raw_blocks("a ]] b") == [TextSegment("a ]] b")]


def test_raw_composition_joins_first_text_sentence_after_raw():
    result = compose_raw_segments(
        [TextSegment("a"), RawPhonemeSegment("ɹ"), TextSegment("bc")],
        lambda text: [[*text]],
    )
    assert result == [["a", "ɹ", "b", "c"]]


def test_frontend_raw_blocks_use_custom_backend_and_encode():
    frontend = PiperFrontend(config(), backend=FakeBackend(), missing="ignore")
    result = frontend.phonemize("ab[[c]]d")
    assert result.sentences[0].phonemes == ("a", "b", "c", "d")
    assert result.diagnostics.phoneme_type == "espeak"
