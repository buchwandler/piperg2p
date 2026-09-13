from _common import load_g2p, parser

from piperg2p import apply_marker_overrides, parse_delimited

args = parser("Convert marked source ranges to Piper overrides").parse_args()
clean, ranges, warnings = parse_delimited("Say @hello@ today")
g2p = load_g2p(args)
try:
    result = g2p.phonemize_prepared(clean, overrides=apply_marker_overrides(clean, ranges, {1: {"lang": args.language}}))
    print(result.phonemes)
    print(warnings + result.warnings)
finally:
    g2p.close()
