from _common import load_g2p, parser

from piperg2p import OverrideSpan

args = parser("Route one source span through an explicit eSpeak voice").parse_args()
g2p = load_g2p(args)
try:
    result = g2p.phonemize_prepared(
        "Hello Welt", overrides=[OverrideSpan(6, 10, {"lang": "de-de"})]
    )
    print(result.phonemes)
    print(result.language_routes)
finally:
    g2p.close()
