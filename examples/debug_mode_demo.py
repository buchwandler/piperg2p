from _common import load_g2p, parser

args = parser("Inspect Piper-native diagnostics").parse_args()
g2p = load_g2p(args)
try:
    result = g2p.phonemize_prepared("Hello world")
    print(result.diagnostics)
    print(result.tokens)
    print(result.missing_phonemes)
    print(result.warnings)
    print(result.sentences)
finally:
    g2p.close()
