from _common import load_g2p, parser

args = parser("Show Piper lexicon-first fallback configuration").parse_args()
print("Use get_g2p(..., lexicons=(...), use_espeak_fallback=True) for lexicon miss fallback.")
g2p = load_g2p(args)
try:
    print(g2p.phonemize("Hello world"))
finally:
    g2p.close()
