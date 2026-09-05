"""Guard the generated criterion/solver compatibility matrix against drift.

``website/scripts/generate_data.py`` derives the single criterion/solver compatibility
table from ``scorequant.api._SOLVER_TABLE`` and writes it into
``website/src/generated/portal-data.json`` and into a marked region of ``docs/method.md``,
``README.md``, ``docs/book/ch06-two-tasks.md`` and ``docs/api.md``. This module checks those
derived artifacts against the registry and against each other -- a hand edit inside a
generated region, or a registry change without regeneration, fails here.

Behaviour-versus-registry (does the library actually accept or refuse each pairing) is
already covered by the executed fence in ``docs/book/ch14-choosing-a-method.md``, which
enumerates all thirty (task, config, criterion) combinations and pins
``(accepted, refused) == (10, 20)``. This module does not duplicate that check.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType

import pytest

from scorequant.api import _SOLVER_TABLE

ROOT = Path(__file__).resolve().parents[1]
GENERATE_DATA_MODULE = ROOT / "website" / "scripts" / "generate_data.py"
PORTAL_DATA = ROOT / "website" / "src" / "generated" / "portal-data.json"

# The four Markdown files whose ``<!-- generated: solver-matrix -->`` region must equal
# the table rendered from the current registry. README and the API guide carry the extra
# "Contract" column.
_CONSUMERS = (
    (ROOT / "docs" / "method.md", False),
    (ROOT / "README.md", True),
    (ROOT / "docs" / "book" / "ch06-two-tasks.md", False),
    (ROOT / "docs" / "api.md", True),
)


def _load_generate_data() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "_scorequant_portal_generate_data", GENERATE_DATA_MODULE
    )
    assert spec is not None and spec.loader is not None, GENERATE_DATA_MODULE
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generate_data() -> ModuleType:
    assert GENERATE_DATA_MODULE.is_file(), GENERATE_DATA_MODULE
    return _load_generate_data()


def _extract_generated_region(text: str, start: str, end: str) -> str:
    match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, flags=re.DOTALL)
    assert match is not None, "solver-matrix generated region not found"
    return match.group(1).strip("\n")


def test_solver_matrix_matches_registry(generate_data: ModuleType) -> None:
    """``_solver_matrix()`` reflects ``_SOLVER_TABLE`` exactly, row for row, in order."""
    rows = generate_data._solver_matrix()
    assert [row["configuration"] for row in rows] == [
        config_type.__name__ for config_type in _SOLVER_TABLE
    ]
    for row, (config_type, spec) in zip(rows, _SOLVER_TABLE.items(), strict=True):
        assert row["configuration"] == config_type.__name__
        assert row["partitionCriteria"] == [
            criterion.__name__ for criterion in spec.partition_criteria
        ]
        assert row["quantizerCriteria"] == [
            criterion.__name__ for criterion in spec.quantizer_criteria
        ]


def test_portal_data_solver_matrix_matches_registry(generate_data: ModuleType) -> None:
    """The committed ``portal-data.json`` matrix equals what ``_SOLVER_TABLE`` declares now."""
    payload = json.loads(PORTAL_DATA.read_text(encoding="utf-8"))
    assert payload["solverMatrix"] == generate_data._solver_matrix()


@pytest.mark.parametrize(("path", "with_contract"), _CONSUMERS, ids=lambda value: str(value))
def test_generated_region_matches_rendered_matrix(
    generate_data: ModuleType, path: Path, with_contract: bool
) -> None:
    """Each committed generated region equals the table rendered from the current registry."""
    rows = generate_data._solver_matrix()
    expected = generate_data._render_solver_matrix(rows, with_contract=with_contract)
    actual = _extract_generated_region(
        path.read_text(encoding="utf-8"),
        generate_data._SOLVER_MATRIX_START,
        generate_data._SOLVER_MATRIX_END,
    )
    assert actual == expected
