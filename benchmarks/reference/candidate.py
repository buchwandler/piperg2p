from __future__ import annotations

from pathlib import Path

from piperg2p import EspeakBackend, PiperFrontend, VoiceConfig


def run_candidate(text: str, voice: str, *, candidate: str, config: Path | None = None) -> tuple[str, dict[str, object]]:
    if config is None:
        backend = EspeakBackend(mode=candidate)
        try:
            groups = backend.phonemize(text, voice=voice)
            return "".join("".join(group) for group in groups), {
                "implementation": backend.diagnostics.implementation,
                "diagnostics": backend.diagnostics.__dict__,
            }
        finally:
            backend.close()
    voice_config = VoiceConfig.from_json(config)
    frontend = PiperFrontend(voice_config, backend=EspeakBackend(mode=candidate))
    try:
        result = frontend.phonemize_prepared(text)
        return result.phonemes, {
            "implementation": result.diagnostics.backend if result.diagnostics else None,
            "diagnostics": result.diagnostics.backend_diagnostics.__dict__ if result.diagnostics and result.diagnostics.backend_diagnostics else None,
        }
    finally:
        frontend.close()
