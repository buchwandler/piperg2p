# Backend API

`EspeakBackend(mode="auto")` selects an exact native clause provider only when the public terminator API is available. Otherwise it reports `terminator API unavailable` and falls back to the CLI with best-effort parity. `mode="native"` fails instead of silently selecting an inexact provider. `mode="cli"` explicitly selects the best-effort subprocess backend.

Discovery order is explicit constructor or environment override, the optional modern eSpeak loader, system eSpeak NG, and legacy system eSpeak. `BackendDiagnostics.discovery_source` records the selected source.

The native binding requests synchronous text conversion using the public eSpeak API value `AUDIO_OUTPUT_SYNCHRONOUS = 2`; it does not request playback.
