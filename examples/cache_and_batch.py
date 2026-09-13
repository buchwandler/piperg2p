from _common import parser

from piperg2p import cache_info, clear_cache, get_g2p

args = parser("Reuse a bounded PiperG2P cache entry").parse_args()
first = get_g2p(args.language, config=args.config)
second = get_g2p(args.language, config=args.config)
try:
    print(first is second, cache_info())
    for text in ("Hello world", "Good morning", "See you"):
        print(first.phonemize(text))
finally:
    clear_cache()
