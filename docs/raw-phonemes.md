# Raw phonemes

In eSpeak mode, PiperG2P recognizes `[[ ... ]]` blocks before normal conversion. Their contents are inserted as phoneme characters and are not normalized or sent through eSpeak. Adjacent ordinary text remains composed into its sentence group. With a lexicon overlay, raw blocks take precedence over lexicon lookup. Raw symbols still pass through the configured voice map and are reported as missing when they are unmapped.

Opening or closing delimiters without a matching pair are deterministic ordinary text. Empty blocks add no symbols. See the [executable examples](https://github.com/buchwandler/piperg2p/blob/main/examples/README.md) for executable raw-block usage.

## Compose with external text rewriting

PiperG2P owns the `[[ ... ]]` syntax. If an external semantic-preparation layer runs before phonemization, identify and protect raw-block source ranges before rewriting ordinary text, then restore the blocks for PiperG2P. This is an external composition pattern, not a locally verified integration: the preparation package is not included in this repository snapshot or required by PiperG2P.

Any override or annotation offsets must be remapped to the final transformed text after rewriting. See the canonical [prepared-text guide](prepared-text.md) for source-coordinate ownership and [overrides](overrides.md) for half-open span semantics.
