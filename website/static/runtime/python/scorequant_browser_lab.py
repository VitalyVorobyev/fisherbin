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
        return sq.DExchangeConfig(seed=seed, initializer_restarts=2, max_scans=max_scans)
    if solver == "mahalanobis_lloyd":
        return sq.MahalanobisLloydConfig(seed=seed, initializer_restarts=2, max_iter=max_steps)
    if solver == "kmeans":
        return sq.KMeansConfig(seed=seed, solver_restarts=2, max_iter=max_steps)
    if solver == "scalar_dp":
        return sq.ScalarDPConfig(seed=seed, max_rows=5_000)
    if solver == "soft_voronoi":
        return sq.SoftVoronoiConfig(
            seed=seed,
            initializer_restarts=2,
            kmeans_max_iter=min(80, max_steps),
            max_steps=max_steps,
            record_every=max(1, max_steps // 10),
        )
    raise ValueError(f"unsupported browser solver: {solver}")


#: Browser ceiling, mirroring `LAB_LIMITS` in `src/lab/protocol.ts` and the
#: JSON Schema. Six columns admits the five-dimensional FlowCyt mixture score.
MAX_DIMENSIONS = 6
MAX_ROWS = 5_000


def _criterion(problem: dict[str, object], schema: object) -> object:
    """Build the declared objective, naming parameters of interest when given.

    The schema is what makes ``interest=("HSPCs",)`` possible here: without it
    the browser would have to send column indices and the reader would have to
    know what column four means.
    """
    declared = problem.get("criterion")
    if declared is None:
        return sq.DOptimality()
    name = declared["name"]
    if name == "d_optimality":
        return sq.DOptimality()
    if name == "normalized_trace":
        return sq.NormalizedTrace()
    if name == "profiled_d_optimality":
        interest = tuple(declared.get("interest") or ())
        if not interest:
            raise ValueError("profiled D_s requires at least one parameter of interest")
        if schema is None:
            raise ValueError("profiled D_s by name requires a score schema")
        return sq.ProfiledDOptimality(interest=interest)
    raise ValueError(f"unsupported browser criterion: {name}")


def run_lab(payload: str) -> str:
    """Run one bounded ScoreQuant problem and return protocol JSON."""
    problem = json.loads(payload)
    scores = np.asarray(problem["scores"], dtype=np.float64)
    weights = np.asarray(problem["weights"], dtype=np.float64)
    if scores.ndim != 2 or not 1 <= scores.shape[1] <= MAX_DIMENSIONS or scores.shape[0] > MAX_ROWS:
        raise ValueError("browser score capacity exceeded")
    names = problem.get("schema")
    schema = None if names is None else sq.ScoreSchema(tuple(str(name) for name in names))
    criterion = _criterion(problem, schema)
    execution = sq.ExecutionConfig(backend="numpy", precision="float64", device="cpu")
    source = sq.ScoreSample(scores=scores, weights=weights, schema=schema)
    result = sq.fit_quantizer(
        source,
        n_bins=int(problem["nBins"]),
        criterion=criterion,
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
    profiled = result.train_profiled_report
    # A profiled run must report the profiled retention: the full-D retention of
    # a D_s fit is a different number answering a different question, and
    # showing it beside a "profiled" label would be a quiet lie.
    retention = (
        result.train_report.geometric_mean_retention
        if profiled is None
        else profiled.geometric_mean_retention
    )
    payload_out: dict[str, object] = {
        "labels": labels.tolist(),
        "centers": centers.tolist(),
        "retention": retention,
        "objective": float(result.trace.objective[-1]),
        "execution": "numpy/float64/cpu",
        "criterionLabel": _criterion_label(criterion, profiled),
    }
    if profiled is not None and profiled.interest_names is not None:
        payload_out["interest"] = list(profiled.interest_names)
    return json.dumps(payload_out)


def _criterion_label(criterion: object, profiled: object) -> str:
    """Name the objective the reported retention is measured against."""
    if isinstance(criterion, sq.ProfiledDOptimality):
        names = getattr(profiled, "interest_names", None)
        shown = ", ".join(names) if names else ", ".join(str(i) for i in criterion.interest)
        return f"Profiled D_s ({shown})"
    if isinstance(criterion, sq.NormalizedTrace):
        return "Normalized trace"
    return "D-optimality"
