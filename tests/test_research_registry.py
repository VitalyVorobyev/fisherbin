"""Integrity checks for the agenticresearch scientific memory.

These tests never do mathematics; they keep the claim registry, the
counterexample bank, and the human ledgers referentially consistent so that
research agents can trust the graph. If a workspace restructure breaks a
`proof_location` or drops a fixture, CI fails here instead of silently
corrupting the memory.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).parents[1] / "agenticresearch"
CLAIMS_PATH = WORKSPACE / "CLAIMS.json"


@pytest.fixture(scope="module")
def registry() -> dict:
    assert CLAIMS_PATH.is_file(), (
        f"claim registry not found at {CLAIMS_PATH}; if the research workspace "
        "moved, update WORKSPACE here and in test_research_claims.py"
    )
    return json.loads(CLAIMS_PATH.read_text())


@pytest.fixture(scope="module")
def claims_by_id(registry: dict) -> dict[str, dict]:
    claims = {claim["id"]: claim for claim in registry["claims"]}
    assert len(claims) == len(registry["claims"]), "duplicate claim ids"
    return claims


def test_every_claim_uses_declared_vocabularies(registry: dict) -> None:
    statuses = set(registry["status_definitions"])
    publication_statuses = set(registry["publication_status_definitions"])
    search_statuses = set(registry["literature_search_status_definitions"])
    levels = set(registry["levels"])
    criteria = set(registry["criteria"])
    for claim in registry["claims"]:
        assert claim["status"] in statuses, claim["id"]
        assert claim["publication_status"] in publication_statuses, claim["id"]
        assert claim["level"] in levels, claim["id"]
        for criterion in claim["criterion"]:
            assert criterion in criteria, (claim["id"], criterion)
        if "literature_search_status" in claim:
            assert claim["literature_search_status"] in search_statuses, claim["id"]


def test_graph_edges_resolve(claims_by_id: dict[str, dict]) -> None:
    for claim in claims_by_id.values():
        for field in ("dependencies", "implies", "converse_failures"):
            for other in claim.get(field, []):
                assert other in claims_by_id, (claim["id"], field, other)


def test_proof_locations_resolve(registry: dict) -> None:
    file_cache: dict[str, str] = {}
    for claim in registry["claims"]:
        location = claim["proof_location"]
        target = WORKSPACE / location["file"]
        assert target.is_file(), (claim["id"], location["file"])
        if location["file"] not in file_cache:
            file_cache[location["file"]] = target.read_text()
        assert location["section"] in file_cache[location["file"]], (
            claim["id"],
            f"section {location['section']!r} not found in {location['file']}",
        )


def test_referenced_counterexamples_have_fixtures(registry: dict) -> None:
    for claim in registry["claims"]:
        ids = claim.get("counterexamples", []) + claim.get("boundary_counterexamples", [])
        for fixture_id in ids:
            fixture = WORKSPACE / "COUNTEREXAMPLES" / f"{fixture_id}.json"
            assert fixture.is_file(), (claim["id"], fixture_id)


def test_artifact_paths_exist(registry: dict) -> None:
    for claim in registry["claims"]:
        if "artifact" in claim:
            assert (WORKSPACE / claim["artifact"]).is_file(), (
                claim["id"],
                claim["artifact"],
            )


def test_every_fixture_is_cited_and_self_consistent(
    claims_by_id: dict[str, dict],
) -> None:
    cited: set[str] = set()
    for claim in claims_by_id.values():
        cited.update(claim.get("counterexamples", []))
        cited.update(claim.get("boundary_counterexamples", []))
    fixtures = sorted((WORKSPACE / "COUNTEREXAMPLES").glob("CE-*.json"))
    assert fixtures, "counterexample bank is empty"
    for path in fixtures:
        fixture = json.loads(path.read_text())
        assert fixture["id"] == path.stem, path.name
        assert fixture["id"] in cited, f"{path.name} is cited by no claim"
        assert len(fixture["labels_before"]) == len(fixture["scores"]), path.name
        assert len(fixture["weights"]) == len(fixture["scores"]), path.name
        assert set(fixture["labels_before"]) <= set(range(fixture["K"])), path.name


def test_indexes_match_claim_array(registry: dict) -> None:
    by_status: dict[str, set[str]] = {}
    by_criterion: dict[str, set[str]] = {}
    by_level: dict[str, set[str]] = {}
    for claim in registry["claims"]:
        by_status.setdefault(claim["status"], set()).add(claim["id"])
        by_level.setdefault(claim["level"], set()).add(claim["id"])
        for criterion in claim["criterion"]:
            by_criterion.setdefault(criterion, set()).add(claim["id"])
    indexes = registry["indexes"]
    for name, fresh in (
        ("by_status", by_status),
        ("by_criterion", by_criterion),
        ("by_level", by_level),
    ):
        stored = {key: set(value) for key, value in indexes[name].items()}
        assert stored == fresh, f"stale index {name}"
    assert set(indexes["priority_open_claims"]) == by_status.get("open", set())


def test_bibliography_references_resolve(registry: dict) -> None:
    bibliography = set(registry["bibliography"])
    for claim in registry["claims"]:
        for key in claim.get("literature", []):
            assert key in bibliography, (claim["id"], key)
