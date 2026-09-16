# Changelog

## Unreleased

### Changed

- eSpeak auto mode now probes automatically discovered native libraries and selects the first library supporting Piper's exact `espeak_TextToPhonemesWithTerminator` API before falling back to the CLI
- Explicit native-library overrides remain authoritative
- eSpeak diagnostics distinguish unavailable native libraries from libraries that lack the exact Piper clause API
- Backend fallback warnings now identify the external caller instead of a dataclass-generated `<string>` frame
- Added non-initializing `inspect_espeak()` capability diagnostics
