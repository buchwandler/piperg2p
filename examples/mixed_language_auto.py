from _common import load_g2p, parser

from piperg2p import LanguageRoutingConfig

args = parser("Conservative lexicon-evidence language routing").parse_args()
g2p = load_g2p(args)
try:
    routing = LanguageRoutingConfig(
        mode="auto", languages=(args.language, "de-de"), lexicons={}
    )
    result = g2p.phonemize_prepared("Hello Welt", language_routing=routing)
    print(result.phonemes)
    for route in result.language_routes:
        print(route)
finally:
    g2p.close()
