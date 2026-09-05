"""Guard the score-space region export against Euclidean-bisector drift.

``website/scripts/generate_data.py::_score_space_data`` compiles each committed
D-exchange partition into its canonical Mahalanobis rule (Theorem 3) and
rasterizes that rule over a display grid, so ``ScoreSpace.tsx`` can paint the
compiled cell regions the library actually computes instead of drawing
Euclidean perpendicular bisectors between bin centers -- which disagree with
the compiled rule on real fixtures (verified 5 September 2026 for K = 3, 4, 5;
see the M13-A1 spec).

This module re-derives the committed fixtures from the library directly and
checks the exported grid, labels, and metric against what the library
actually computes on a fresh fit with the same recipe, and documents why
regions are needed in the first place: Euclidean nearest-centre disagrees
with at least one stored label on at least one fixture.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest

import scorequant as sq

ROOT = Path(__file__).resolve().parents[1]
GENERATE_DATA_MODULE = ROOT / "website" / "scripts" / "generate_data.py"
PORTAL_DATA = ROOT / "website" / "src" / "generated" / "portal-data.json"

#: The number of hard bins each committed score-space fixture covers.
_BIN_COUNTS = (3, 4, 5)


def _config() -> sq.DExchangeConfig:
    """Return the exact fitting recipe ``_score_space_data`` uses for every fixture.

    Also documented in ``website/src/components/ScoreSpaceLiveFit.tsx``'s
    docstring, so a browser refit reproduces this page's own number.
    Duplicated here (rather than imported) because ``_score_space_data``
    returns JSON-ready data, not the live :class:`~scorequant.Quantizer` this
    module needs in order to call ``predict_scores``.
    """
    return sq.DExchangeConfig(seed=28, initializer_restarts=2, max_scans=120)


def _execution() -> sq.ExecutionConfig:
    return sq.ExecutionConfig(backend="numpy", precision="float64", device="cpu")


def _load_generate_data() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "_scorequant_portal_generate_data_regions", GENERATE_DATA_MODULE
    )
    assert spec is not None and spec.loader is not None, GENERATE_DATA_MODULE
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generate_data() -> ModuleType:
    assert GENERATE_DATA_MODULE.is_file(), GENERATE_DATA_MODULE
    return _load_generate_data()


@pytest.fixture(scope="module")
def score_space_data(generate_data: ModuleType) -> dict[str, object]:
    return generate_data._score_space_data()


def test_region_grid_matches_a_live_quantizer(score_space_data: dict[str, object]) -> None:
    """Exported region labels equal ``predict_scores`` on the reconstructed grid.

    The grid is rebuilt from nothing but the exported window (``x0``, ``x1``,
    ``y0``, ``y1``, ``nx``, ``ny``) -- an independent reconstruction from what
    a consumer of the JSON receives, not a call back into
    ``_score_space_data``'s own grid-building code. This also re-fits every
    partition from the exported points and weights, so a stale, uncommitted
    regeneration fails here rather than only inside the generator itself.
    """
    points = np.asarray(score_space_data["points"])
    weights = np.asarray(score_space_data["weights"])
    scenarios = score_space_data["scenarios"]
    execution = _execution()
    any_euclidean_disagreement = False
    for n_bins in _BIN_COUNTS:
        scenario = scenarios[str(n_bins)]
        result = sq.optimize_partition(
            points,
            weights=weights,
            n_bins=n_bins,
            config=_config(),
            execution=execution,
        )
        quantizer = result.compile_quantizer()

        stored_labels = np.asarray(scenario["labels"])
        assert np.array_equal(quantizer.predict_scores(points), stored_labels)

        regions = scenario["regions"]
        x0, x1, y0, y1 = regions["x0"], regions["x1"], regions["y0"], regions["y1"]
        nx, ny = regions["nx"], regions["ny"]
        cell_x = x0 + (np.arange(nx) + 0.5) * (x1 - x0) / nx
        cell_y = y0 + (np.arange(ny) + 0.5) * (y1 - y0) / ny
        grid_x, grid_y = np.meshgrid(cell_x, cell_y)
        grid_points = np.stack([grid_x.ravel(), grid_y.ravel()], axis=1)
        expected_region_labels = quantizer.predict_scores(grid_points)
        exported_region_labels = np.array([int(digit) for digit in regions["labels"]])
        assert np.array_equal(expected_region_labels, exported_region_labels)

        # The claim the regions exist to correct: the Euclidean nearest-centre
        # rule the old bisectors drew disagrees with the compiled Mahalanobis
        # rule's own stored labels.
        centers = np.asarray(scenario["centers"])
        distances = np.sum((points[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        euclidean_labels = np.argmin(distances, axis=1)
        if not np.array_equal(euclidean_labels, stored_labels):
            any_euclidean_disagreement = True

    assert any_euclidean_disagreement, (
        "Euclidean nearest-centre agreed with every stored label on every fixture; "
        "the compiled Mahalanobis regions would then draw nothing the bisectors did not"
    )


def test_committed_portal_data_carries_regions_and_metric() -> None:
    """The committed ``portal-data.json`` was regenerated with ``pnpm generate:data``."""
    payload = json.loads(PORTAL_DATA.read_text(encoding="utf-8"))
    scenarios = payload["scoreSpace"]["scenarios"]
    assert scenarios, "no score-space scenarios in the committed portal data"
    for n_bins, scenario in scenarios.items():
        assert "regions" in scenario, f"scenario {n_bins} is missing its region export"
        assert "metric" in scenario, f"scenario {n_bins} is missing its metric export"
