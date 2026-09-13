from _common import load_g2p, parser

from piperg2p import TokenAnnotation

args = parser("Pass source-aligned POS and lexicon tags").parse_args()
g2p = load_g2p(args)
try:
    result = g2p.phonemize_prepared(
        "Hello world", annotations=[TokenAnnotation(0, 5, tag="NN")]
    )
    print([(token.text, token.meta) for token in result.tokens])
    print(result.phonemes)
finally:
    g2p.close()
