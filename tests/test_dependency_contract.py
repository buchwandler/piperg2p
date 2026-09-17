from __future__ import annotations

from importlib.metadata import requires

from packaging.requirements import Requirement

FORBIDDEN_SEMANTIC_DEPENDENCIES = frozenset({"numeralform", "spokenform"})
ALLOWED_CORE_RUNTIME_DEPENDENCIES = frozenset({"espeakng-runtime"})


def _piperg2p_requirements() -> list[Requirement]:
    raw = requires("piperg2p")
    if raw is None:
        return []
    return [Requirement(value) for value in raw]


def _normalized_name(requirement: Requirement) -> str:
    return requirement.name.casefold().replace("_", "-")


def test_semantic_packages_are_not_piperg2p_dependencies() -> None:
    names = {_normalized_name(item) for item in _piperg2p_requirements()}
    assert names.isdisjoint(FORBIDDEN_SEMANTIC_DEPENDENCIES)


def test_core_runtime_dependencies_are_intentional() -> None:
    core_requirements = [
        item
        for item in _piperg2p_requirements()
        if item.marker is None or "extra" not in str(item.marker)
    ]
    assert {
        _normalized_name(item) for item in core_requirements
    } == ALLOWED_CORE_RUNTIME_DEPENDENCIES


def test_espeakng_runtime_floor() -> None:
    requirement = next(
        item
        for item in _piperg2p_requirements()
        if _normalized_name(item) == "espeakng-runtime" and item.marker is None
    )
    assert ">=0.1.3" in str(requirement.specifier)
    assert "<0.2" in str(requirement.specifier)
