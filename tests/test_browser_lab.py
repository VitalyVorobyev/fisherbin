from __future__ import annotations

import json
import runpy
from collections.abc import Callable
from pathlib import Path
from typing import cast

import numpy as np

ROOT = Path(__file__).parents[1]


def test_browser_adapter_matches_committed_numpy_fixture() -> None:
    portal_data = json.loads((ROOT / "website/src/generated/portal-data.json").read_text())
    score_space = portal_data["scoreSpace"]
    problem = {
        "scores": score_space["points"],
        "weights": score_space["weights"],
        "nBins": 4,
        "solver": "d_exchange",
        "seed": 28,
        "maxSteps": 120,
        "maxScans": 120,
    }
    namespace = runpy.run_path(ROOT / "website/static/runtime/python/scorequant_browser_lab.py")
    run_lab = cast(Callable[[str], str], namespace["run_lab"])
    result = json.loads(run_lab(json.dumps(problem)))
    fixture = score_space["scenarios"]["4"]

    # The labels are the portable part of the fixture: the assignment is discrete
    # and must reproduce exactly. The scalars are reductions over that assignment,
    # so they carry the host BLAS's summation order and land a ULP apart between
    # the machine that regenerated `portal-data.json` and CI. They are pinned to
    # the same 1e-12 as the centers rather than to bit equality.
    np.testing.assert_array_equal(result["labels"], fixture["labels"])
    np.testing.assert_allclose(result["centers"], fixture["centers"], rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(result["retention"], fixture["retention"], rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(result["objective"], fixture["objective"], rtol=1e-12, atol=1e-12)
