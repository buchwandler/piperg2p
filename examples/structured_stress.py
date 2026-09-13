from _common import load_g2p, parser

from piperg2p import OverrideSpan

args = parser("Apply structured stress after pronunciation resolution").parse_args()
g2p = load_g2p(args)
try:
    result = g2p.phonemize_prepared(
        "Hello", overrides=[OverrideSpan(0, 5, {"ph": "hello", "stress": 2})]
    )
    print(result.phonemes)
finally:
    g2p.close()
