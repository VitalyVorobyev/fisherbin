"""Integrity checks for the agenticresearch scientific memory.

These tests never do mathematics; they keep the claim registry, the
counterexample bank, and the human ledgers referentially consistent so that
research agents can trust the graph. If a workspace restructure breaks a
`proof_location`, drops a fixture, or leaves a completed packet's pointer
behind, CI fails here instead of silently corrupting the memory.

The checks themselves live in `agenticresearch/py/registry.py` so that a
bookkeeping session can run exactly what CI runs, without pytest:

    python agenticresearch/py/registry.py validate
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

WORKSPACE = Path(__file__).parents[1] / "agenticresearch"
REGISTRY_MODULE = WORKSPACE / "py" / "registry.py"


def _load_registry_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_scorequant_registry", REGISTRY_MODULE)
    assert spec is not None and spec.loader is not None, REGISTRY_MODULE
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def tool() -> ModuleType:
    assert REGISTRY_MODULE.is_file(), (
        f"registry tool not found at {REGISTRY_MODULE}; if the research workspace "
        "moved, update WORKSPACE here and in test_research_claims.py"
    )
    return _load_registry_module()


def test_registry_loads_with_one_file_per_claim(tool: ModuleType) -> None:
    registry = tool.load(WORKSPACE)
    claims = registry["claims"]
    assert claims, "claim registry is empty"
    ids = {claim["id"] for claim in claims}
    assert len(ids) == len(claims), "duplicate claim ids"
    on_disk = {path.stem for path in (WORKSPACE / "claims").glob("*.json")}
    assert ids == on_disk, "claims/ and the loaded registry disagree"


def test_registry_is_referentially_consistent(tool: ModuleType) -> None:
    violations = tool.validate(WORKSPACE)
    assert not violations, "\n".join(["registry integrity violations:", *violations])


def test_generated_indexes_are_current(tool: ModuleType) -> None:
    stale = tool.reindex(WORKSPACE, check=True)
    assert not stale, "\n".join(
        ["stale generated indexes; run `python agenticresearch/py/registry.py reindex`", *stale]
    )


def test_formal_proof_is_attached_only_to_the_atomic_scalar_claim(tool: ModuleType) -> None:
    registry = tool.load(WORKSPACE)
    claims = tool.claims_by_id(registry)
    formal = claims["D-EXCHANGE-SCALAR-CORE"]["formal_proof"]

    assert formal["declaration"] == ("ScoreQuantFormal.scalarExchangeStrengthenedLowerBound")
    assert "formal_proof" not in claims["D-EXCHANGE-VIOLATION-LOWER-BOUND"]
    assert "formal_proof" not in claims["D-EXCHANGE-IMPLIES-VORONOI"]
    assert formal["declaration"] in tool.render_index(registry)
