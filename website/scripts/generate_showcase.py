"""Generate the FlowCyt showcase data the portal renders.

Two tiers, because they cost very different amounts. The narrative data --
marker histograms, patient compositions, the published method comparison -- is
derived from committed artifacts in seconds and is regenerated on every build.
The five-dimensional score table the browser Lab runs on requires fitting the
cross-fitted classifier, so it is written once and reused unless ``--force``.

Everything here reads committed inputs only. The 3.7 GB upstream FlowCyt data is
never required, and never ships.

The FlowCyt data is licensed CC BY-NC-SA 4.0, separately from ScoreQuant's MIT
license. Attribution and share-alike travel with every array this script emits;
see ``website/static/showcase-data/LICENSE.txt``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from examples.cell_population.data import (  # noqa: E402
    CLASS_NAMES,
    FEATURE_NAMES,
    REFERENCE_PATIENTS,
    TEST_PATIENTS,
    RobustArcsinhTransform,
    load_fixture,
)

FIXTURE = REPO_ROOT / "examples" / "data" / "flowcyt_fixture.npz"
FIXTURE_FACTS = REPO_ROOT / "examples" / "data" / "flowcyt_fixture.json"
STUDY_METRICS = REPO_ROOT / "docs" / "usecases" / "assets" / "cell_population.json"
NARRATIVE_OUT = REPO_ROOT / "website" / "src" / "generated" / "showcase-data.json"
SCORES_OUT = REPO_ROOT / "website" / "static" / "showcase-data" / "flowcyt-scores.json"

#: Marker histogram resolution. Thirty-two bins over the robust range keeps the
#: whole exploration payload under ~40 KB while still showing the bimodality
#: that separates the populations.
HISTOGRAM_BINS = 32

#: Bin budget the study reports as its operating point.
OPERATING_BINS = 8

#: Rows handed to the browser. The Lab caps a run at 8,000 rows; a stratified
#: subsample of this size keeps every population represented.
LAB_ROWS = 5_000

#: Score column names. The mixture score absorbs one component as the
#: simplex-dependent reference, so there are five columns for six populations.
SCORE_PARAMETERS = CLASS_NAMES[:-1]


def _round(values: object, digits: int = 6) -> object:
    """Round nested numeric data so the committed JSON has no float noise."""
    if isinstance(values, np.ndarray):
        return _round(values.tolist(), digits)
    if isinstance(values, list):
        return [_round(item, digits) for item in values]
    if isinstance(values, (float, np.floating)):
        return round(float(values), digits)
    if isinstance(values, (int, np.integer)):
        return int(values)
    return values


def _marker_histograms(features: np.ndarray, labels: np.ndarray) -> list[dict[str, object]]:
    """Bin every marker per population over one shared robust range.

    Cytometry intensities are heavily skewed -- on a linear axis every panel is
    one spike against the origin and shows nothing. These are binned on the same
    robust arcsinh scale the study's classifier is trained on, which is what
    makes the population structure visible at all. The range is the 0.5-99.5
    percentile so a handful of saturated events do not flatten it back.
    """
    transform = RobustArcsinhTransform.fit(features)
    scaled = transform.apply(features)
    panels: list[dict[str, object]] = []
    for column, name in enumerate(FEATURE_NAMES):
        values = scaled[:, column]
        low, high = np.percentile(values, [0.5, 99.5])
        if not np.isfinite(low) or not np.isfinite(high) or high <= low:
            low, high = float(values.min()), float(values.max()) + 1e-9
        edges = np.linspace(low, high, HISTOGRAM_BINS + 1)
        series = []
        for index, population in enumerate(CLASS_NAMES):
            counts, _ = np.histogram(values[labels == index], bins=edges)
            total = int(counts.sum())
            series.append(
                {
                    "population": population,
                    "density": _round(counts / total if total else counts.astype(float), 5),
                }
            )
        panels.append(
            {
                "marker": name,
                "edges": _round(edges, 4),
                "series": series,
            }
        )
    return panels


def _patient_compositions(metrics: dict[str, object]) -> list[dict[str, object]]:
    """Per-patient population fractions, which is what the study actually estimates.

    Taken from the study's record rather than counted in the committed fixture.
    The fixture deliberately samples a fixed number of cells per class for the
    reference patients, so counting it would plot the sampling design and label
    it biology.
    """
    dataset = metrics["dataset"]
    assert isinstance(dataset, dict)
    entries = dataset["patient_compositions"]
    assert isinstance(entries, list)
    rows: list[dict[str, object]] = []
    for entry in entries:
        assert isinstance(entry, dict)
        rows.append(
            {
                "patient": int(entry["patient"]),  # type: ignore[arg-type]
                "role": "reference" if entry["split"] == "reference" else "held-out",
                "fractions": _round(entry["fractions"], 5),
            }
        )
    return sorted(rows, key=lambda row: int(row["patient"]))  # type: ignore[arg-type]


def _method_comparison(metrics: dict[str, object]) -> dict[str, object]:
    """Reshape the published study metrics into a method x budget grid.

    These are the study's own numbers, not a re-run: the showcase reports what
    was measured on the full 600,000-cell sample rather than what the committed
    34,554-cell fixture would reproduce.
    """
    labels = {
        "finite_d_exchange": "D exchange (compiled)",
        "score_kmeans": "Normalized trace (k-means)",
        "soft_voronoi": "Soft Voronoi",
        "random_score_voronoi": "Random score Voronoi",
        "one_dimensional_score": "One score direction",
        "two_dimensional_grid": "Two-dimensional grid",
        "marker_kmeans": "k-means on raw markers",
    }
    grid: dict[str, list[dict[str, object]]] = {}
    budgets: set[int] = set()
    for key, payload in metrics.items():
        if ":" not in key or not isinstance(payload, dict):
            continue
        method, _, budget_text = key.partition(":")
        if method not in labels or "target_macro_rmse" not in payload:
            continue
        budget = int(budget_text)
        budgets.add(budget)
        grid.setdefault(method, []).append(
            {
                "bins": budget,
                "macroRmse": _round(payload["target_macro_rmse"]),
                "heldOutEfficiency": _round(payload.get("held_out_d_efficiency")),
                "minimumBinCount": payload.get("minimum_bin_count"),
            }
        )
    baseline = metrics["unbinned_classifier_ratio"]
    assert isinstance(baseline, dict)
    return {
        "budgets": sorted(budgets),
        "methods": [
            {
                "key": method,
                "label": labels[method],
                "isScoreQuant": method in ("finite_d_exchange", "score_kmeans", "soft_voronoi"),
                "points": sorted(points, key=lambda point: point["bins"]),
            }
            for method, points in sorted(grid.items())
        ],
        "unbinnedBaseline": {
            "label": "Unbinned classifier ratio",
            "macroRmse": _round(baseline["target_macro_rmse"]),
            "perClassRmse": _round(baseline["per_class_rmse"]),
        },
    }


def _headline(metrics: dict[str, object]) -> dict[str, object]:
    """Read the three numbers the showcase leads with from the study's own record."""
    operating = metrics[f"soft_voronoi:{OPERATING_BINS}"]
    baseline = metrics["unbinned_classifier_ratio"]
    assert isinstance(operating, dict) and isinstance(baseline, dict)
    return {
        "bins": OPERATING_BINS,
        "heldOutEfficiency": _round(operating["held_out_d_efficiency"]),
        "macroRmse": _round(operating["target_macro_rmse"]),
        "unbinnedMacroRmse": _round(baseline["target_macro_rmse"]),
    }


def build_narrative() -> dict[str, object]:
    """Assemble everything the showcase renders without running a solver."""
    data = load_fixture(FIXTURE)
    facts = json.loads(FIXTURE_FACTS.read_text())
    metrics = json.loads(STUDY_METRICS.read_text())
    upstream = facts.get("upstream_file_totals", {})
    return {
        "dataset": {
            "name": "FlowCyt",
            "citation": "Bini, Nassajian Mojarrad, Liarou, Matthes, Marchand-Maillet (CHIL 2024)",
            "repository": facts["source_repository"],
            "license": facts["source_license"],
            "licenseUrl": facts["license_url"],
            "patients": len(set(REFERENCE_PATIENTS) | set(TEST_PATIENTS)),
            "referencePatients": list(REFERENCE_PATIENTS),
            "heldOutPatients": list(TEST_PATIENTS),
            "markers": list(FEATURE_NAMES),
            "populations": list(CLASS_NAMES),
            "fixtureCells": int(data.features.shape[0]),
            "upstreamEvents": int(sum(int(value) for value in upstream.values())),
            "studyCells": 600_000,
        },
        "scoreSchema": {"parameters": list(SCORE_PARAMETERS)},
        "headline": _headline(metrics),
        "exploration": {
            "markerScale": "robust arcsinh (cofactor 150), the study's own transform",
            "markers": _marker_histograms(data.features, data.labels),
            "patients": _patient_compositions(metrics),
        },
        "comparison": _method_comparison(metrics),
    }


def build_lab_scores() -> dict[str, object]:
    """Fit the cross-fitted score model and emit a Lab-sized score table.

    This is the expensive half. It reuses the study's own preparation rather
    than reimplementing the science, so the browser runs on the same score
    construction the published numbers came from.
    """
    from examples.cell_population.experiment import _prepare_experiment  # noqa: PLC0415

    data = load_fixture(FIXTURE)
    context = _prepare_experiment(data, quick=True, seed=2026)
    scores = np.asarray(context.reference_scores)[context.partition_mask]
    weights = np.asarray(context.weights)
    labels = np.asarray(context.reference.labels)[context.partition_mask]

    if scores.shape[0] > LAB_ROWS:
        # Stratify by population so a small subsample still contains the rare
        # compartments the profiled criterion is about.
        rng = np.random.default_rng(2026)
        keep: list[np.ndarray] = []
        share = LAB_ROWS / scores.shape[0]
        for population in np.unique(labels):
            index = np.flatnonzero(labels == population)
            take = max(1, int(round(index.size * share)))
            keep.append(rng.choice(index, size=min(take, index.size), replace=False))
        selection = np.sort(np.concatenate(keep))
        scores, weights, labels = scores[selection], weights[selection], labels[selection]

    return {
        "schema": {"parameters": list(SCORE_PARAMETERS)},
        "rows": int(scores.shape[0]),
        "structure": _score_structure(scores, labels),
        "dimensions": int(scores.shape[1]),
        "scores": _round(scores, 5),
        "weights": _round(weights / weights.mean(), 5),
        "populations": [int(value) for value in labels],
        "populationNames": list(CLASS_NAMES),
        "license": "CC-BY-NC-SA-4.0",
    }


def _score_structure(scores: np.ndarray, labels: np.ndarray) -> dict[str, object]:
    """Measure how concentrated the score cloud is.

    A confidently classified cell has a nearly fixed score, so the cloud is much
    closer to a handful of atoms than to a continuum. That is the reason a small
    bin budget can retain almost all the information, and it is worth reporting
    as a measurement rather than leaving a reader to wonder why the score-space
    plot looks sparse.
    """
    plane = np.round(scores[:, :2], 1)
    distinct = int(np.unique(plane, axis=0).shape[0])
    per_population = []
    for index, name in enumerate(CLASS_NAMES):
        selected = scores[labels == index]
        if selected.shape[0] == 0:
            continue
        per_population.append(
            {
                "population": name,
                "cells": int(selected.shape[0]),
                "meanFirstScore": _round(float(selected[:, 0].mean()), 3),
                "spread": _round(float(selected[:, 0].std()), 3),
            }
        )
    return {
        "distinctPlanePositions": distinct,
        "rows": int(scores.shape[0]),
        "perPopulation": per_population,
    }


def main() -> None:
    """Write both tiers, skipping the expensive one when it is already current."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="rebuild the score table even if it exists"
    )
    arguments = parser.parse_args()

    NARRATIVE_OUT.parent.mkdir(parents=True, exist_ok=True)
    NARRATIVE_OUT.write_text(json.dumps(build_narrative(), indent=2) + "\n")
    print(f"wrote {NARRATIVE_OUT.relative_to(REPO_ROOT)}")

    SCORES_OUT.parent.mkdir(parents=True, exist_ok=True)
    if SCORES_OUT.exists() and not arguments.force:
        print(f"kept {SCORES_OUT.relative_to(REPO_ROOT)} (pass --force to rebuild)")
        return
    SCORES_OUT.write_text(json.dumps(build_lab_scores()) + "\n")
    print(f"wrote {SCORES_OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
