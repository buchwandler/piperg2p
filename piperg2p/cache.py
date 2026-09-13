"""Small bounded cache for reusable PiperG2P facades."""

from __future__ import annotations

import hashlib
import json
from collections import OrderedDict, namedtuple
from collections.abc import Callable
from typing import Any

from .config import VoiceConfig

CacheInfo = namedtuple("CacheInfo", "size maxsize policy")
_DEFAULT_MAXSIZE = 8
_cache: OrderedDict[str, Any] = OrderedDict()
_maxsize = _DEFAULT_MAXSIZE


def config_fingerprint(config: VoiceConfig) -> str:
    payload = json.dumps(
        config.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def cache_key(
    config: VoiceConfig,
    language: str,
    *,
    use_cli: bool,
    missing: str,
    lexicons: tuple[str, ...],
    strict: bool,
    use_espeak_fallback: bool,
) -> str:
    value = {
        "language": language.casefold().replace("_", "-"),
        "config": config_fingerprint(config),
        "use_cli": use_cli,
        "missing": missing,
        "lexicons": lexicons,
        "strict": strict,
        "use_espeak_fallback": use_espeak_fallback,
    }
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def get_or_create(key: str, factory: Callable[[], Any]) -> Any:
    value = _cache.get(key)
    if value is not None:
        _cache.move_to_end(key)
        return value
    value = factory()
    _cache[key] = value
    _cache.move_to_end(key)
    while len(_cache) > _maxsize:
        _, evicted = _cache.popitem(last=False)
        close = getattr(evicted, "close", None)
        if close is not None:
            close()
    return value


def cache_info() -> CacheInfo:
    return CacheInfo(len(_cache), _maxsize, "lru")


def clear_cache(*, deep: bool = False) -> None:
    del deep
    values = tuple(_cache.values())
    _cache.clear()
    for value in values:
        close = getattr(value, "close", None)
        if close is not None:
            close()


def set_maxsize(value: int) -> None:
    global _maxsize
    if value <= 0:
        raise ValueError("cache maxsize must be positive")
    _maxsize = value
    while len(_cache) > _maxsize:
        _, evicted = _cache.popitem(last=False)
        close = getattr(evicted, "close", None)
        if close is not None:
            close()
