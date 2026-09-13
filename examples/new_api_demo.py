from _common import load_g2p, parser

from piperg2p import OverrideSpan

args = parser("Basic PiperG2P prepared API").parse_args()
g2p = load_g2p(args)
try:
    result = g2p.phonemize_prepared(
        "Hello world", overrides=[OverrideSpan(0, 5, {"lang": args.language})]
    )
    print(result.phonemes)
    print(result.ids)
    print(result.warnings)
finally:
    g2p.close()
