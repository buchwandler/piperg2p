from _common import load_g2p, parser

from piperg2p import OverrideSpan

args = parser("Combine prepared text and explicit overrides").parse_args()
g2p = load_g2p(args)
try:
    result = g2p.phonemize_prepared("Hello world", overrides=[OverrideSpan(6, 11, {"lang": "en-us"})])
    print(result.phonemes)
    print([(token.text, token.meta) for token in result.tokens])
finally:
    g2p.close()
