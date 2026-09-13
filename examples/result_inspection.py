from _common import load_g2p, parser

from piperg2p import ids_to_phonemes

args = parser("Inspect source tokens, sentences, IDs, and decoded symbols").parse_args()
g2p = load_g2p(args)
try:
    result = g2p.phonemize_prepared("Hello world")
    print(result.clean_text)
    print(result.tokens)
    print(result.sentences)
    print(result.phonemes)
    print(result.token_ids)
    print(ids_to_phonemes(result.token_ids, g2p.config))
finally:
    g2p.close()
