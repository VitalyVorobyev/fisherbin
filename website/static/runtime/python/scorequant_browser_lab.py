"""Locked browser-lab adapter; kept outside the ScoreQuant package."""

from __future__ import annotations

import json

import numpy as np

import scorequant as sq


def _configuration(problem: dict[str, object]) -> object:
    seed = int(problem["seed"])
    max_steps = int(problem.get("maxSteps", 120))
    max_scans = int(problem.get("maxScans", 120))
    solver = problem["solver"]
    if solver == "d_exchange":
        return sq.DExchangeConfig(seed=seed, n_init=2, max_scans=max_scans)
    if solver == "mahalanobis_lloyd":
        return sq.MahalanobisLloydConfig(seed=seed, n_init=2, max_iter=max_steps)
    if solver == "kmeans":
        return sq.KMeansConfig(seed=seed, n_init=2, max_iter=max_steps)
    if solver == "scalar_dp":
        return sq.ScalarDPConfig(seed=seed, max_rows=5_000)
    if solver == "soft_voronoi":
        return sq.SoftVoronoiConfig(
            seed=seed,
            n_init=2,
            kmeans_max_iter=min(80, max_steps),
            max_steps=max_steps,
            record_every=max(1, max_steps // 10),
        )
    raise ValueError(f"unsupported browser solver: {solver}")


def run_lab(payload: str) -> str:
    """Run one bounded ScoreQuant problem and return protocol JSON."""
    problem = json.loads(payload)
    scores = np.asarray(problem["scores"], dtype=np.float64)
    weights = np.asarray(problem["weights"], dtype=np.float64)
    if scores.ndim != 2 or not 1 <= scores.shape[1] <= 4 or scores.shape[0] > 5_000:
        raise ValueError("browser score capacity exceeded")
    execution = sq.ExecutionConfig(backend="numpy", precision="float64", device="cpu")
    source = sq.ScoreSample(scores=scores, weights=weights)
    result = sq.fit_quantizer(
        source,
        n_bins=int(problem["nBins"]),
        config=_configuration(problem),
        execution=execution,
    )
    labels = np.asarray(result.labels)
    centers = np.vstack(
        [
            np.average(scores[labels == cell], axis=0, weights=weights[labels == cell])
            for cell in range(result.n_bins)
        ]
    )
    return json.dumps(
        {
            "labels": labels.tolist(),
            "centers": centers.tolist(),
            "retention": result.train_report.geometric_mean_retention,
            "objective": float(result.trace.objective[-1]),
            "execution": "numpy/float64/cpu",
        }
    )
