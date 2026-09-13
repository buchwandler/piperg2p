from _common import parser

from piperg2p import available_lexicons, lexicon_info

args = parser("Inspect locally installed pronunciation assets").parse_args()
for name in available_lexicons(args.language):
    print(name, lexicon_info(args.language, name))
