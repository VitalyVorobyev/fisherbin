"""Branch-and-bound certificates, and what multiple restarts are worth.

This script is the single deterministic generator behind the
`docs/examples/global-certification.md` page. It runs

* the two committed incumbent fixtures: a small table on which the exchange
  already found the global optimum, and one on which certification improves on
  an exchange-stable incumbent;
* a multi-restart hit-rate study on a twenty-eight-event problem with genuine
  local optima: how often a fit lands on the certified global optimum, as a
  function of the number of independent exchange restarts and of how those
  restarts are seeded;
* a scaling sweep of the certification itself, in nodes explored and seconds,
  against the number of score atoms and the cell budget, ending with one run
  that deliberately runs out of node budget;

and writes `docs/examples/assets/global-certification.json` plus
`docs/examples/assets/global-certification.png`.

Run it with::

    JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run python -m examples.global_certification
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

import scorequant as sq
from examples._env import example_scale
from examples.synthetic_problems import SyntheticDataset, spectral_templates

FIGURE_PATH = Path("docs/examples/assets/global-certification.png")
METRICS_PATH = Path("docs/examples/assets/global-certification.json")

#: Events in the hit-rate problem. Small enough that branch and bound finishes,
#: large enough that a single exchange restart usually stops short.
HITRATE_ROWS = 28
#: Cell budget of the hit-rate problem.
HITRATE_BINS = 5
#: Restart counts swept. Restart ``r`` of a run with base seed ``s`` uses seed
#: ``s + r``, so trials are spaced by the largest count to keep them disjoint.
RESTART_COUNTS = (1, 2, 3, 4, 6, 8, 12, 16)
#: Independent trials per restart count and seeding mode.
HITRATE_TRIALS = 64
#: Seedings compared.
INIT_MODES = ("kmeans++", "random")
#: Slack within which a run counts as having found the certified optimum.
HIT_TOLERANCE = 1e-9

#: Atom counts of the certification scaling sweep.
SCALING_ROWS = (12, 16, 20, 24, 28, 32)
#: Cell budgets of the same sweep.
SCALING_BINS = (3, 4, 5)
#: Atom count and budget of the deliberate budget-exhausted run.
OVERRUN_ROWS = 36
OVERRUN_BINS = 4
#: Node budget of that run, chosen so it stops in seconds rather than minutes.
OVERRUN_NODES = 200_000


def certification_table(n_rows: int) -> SyntheticDataset:
    """Return a small weighted score table to certify.

    The rows are the first `n_rows` events of the two-template spectral problem,
    so the scores are exact component scores with a meaningful origin rather
    than an arbitrary point cloud.

    Parameters
    ----------
    n_rows
        Events to draw.

    Returns
    -------
    SyntheticDataset
        Observations, exact scores, and reference weights.
    """
    return spectral_templates(sizes=(n_rows, 8, 8)).train


def _seeded_scores(seed: int, n_rows: int) -> np.ndarray:
    """Return the committed incumbent fixture of the regression suite."""
    generator = np.random.default_rng(seed)
    scores = generator.normal(size=(n_rows, 2))
    return scores - scores.mean(axis=0)


@dataclass(frozen=True, slots=True)
class IncumbentCase:
    """One exchange incumbent, and what certification proved about it.

    Attributes
    ----------
    key, label
        Identity of the case.
    n_rows, n_bins
        Size of the table and the cell budget.
    incumbent_objective, certified_objective
        Whitened objective of the exchange result and of the certificate.
    gain
        How much the certificate improved on the incumbent; zero when the
        incumbent was already optimal.
    status, incumbent_was_optimal, gap, nodes_explored
        The certificate's own report.
    seconds
        Wall-clock seconds of the certification.
    """

    key: str
    label: str
    n_rows: int
    n_bins: int
    incumbent_objective: float
    certified_objective: float
    gain: float
    status: str
    incumbent_was_optimal: bool
    gap: float
    nodes_explored: int
    seconds: float


def incumbent_cases() -> list[IncumbentCase]:
    """Certify two committed incumbents, one optimal and one not.

    Both fixtures are the ones the regression suite pins, so the two possible
    outcomes of certification are demonstrated on tables that do not move.

    Returns
    -------
    list of IncumbentCase
        The confirmed case first, then the improved one.
    """
    cases: list[IncumbentCase] = []

    confirmed_scores = _seeded_scores(1, 8)
    improved_scores = _seeded_scores(15, 10)
    improved_weights = np.random.default_rng(115).uniform(0.3, 2.0, size=10)
    fixtures = (
        ("confirmed", "Incumbent proved optimal", confirmed_scores, None, 3),
        ("improved", "Incumbent beaten by the search", improved_scores, improved_weights, 3),
    )
    for key, label, scores, weights, n_bins in fixtures:
        incumbent = sq.optimize_partition(scores, weights=weights, n_bins=n_bins)
        start = time.perf_counter()
        certificate = sq.certify_partition(
            scores, weights=weights, n_bins=n_bins, incumbent=incumbent.labels
        )
        seconds = time.perf_counter() - start
        cases.append(
            IncumbentCase(
                key=key,
                label=label,
                n_rows=int(scores.shape[0]),
                n_bins=n_bins,
                incumbent_objective=float(incumbent.objective),
                certified_objective=float(certificate.objective),
                gain=float(certificate.objective - incumbent.objective),
                status=str(certificate.status),
                incumbent_was_optimal=bool(certificate.incumbent_was_optimal),
                gap=float(certificate.gap),
                nodes_explored=int(certificate.nodes_explored),
                seconds=seconds,
            )
        )
    return cases


@dataclass(frozen=True, slots=True)
class RestartRow:
    """The measured hit rate of one seeding mode at one restart count.

    Attributes
    ----------
    init, n_restarts, trials
        The seeding mode, the restarts each trial was allowed, and how many
        independent trials were run.
    hits, hit_rate
        Trials whose terminal objective matched the certified optimum, and the
        fraction they represent.
    median_shortfall
        Median distance below the certified optimum over the trials, in nat.
    seconds_per_trial
        Mean wall-clock seconds of one trial.
    """

    init: str
    n_restarts: int
    trials: int
    hits: int
    hit_rate: float
    median_shortfall: float
    seconds_per_trial: float


@dataclass(frozen=True, slots=True)
class HitRateStudy:
    """The whole restart study on one certified problem.

    Attributes
    ----------
    n_rows, n_bins
        The problem certified.
    certified_objective, certified_nodes, certified_seconds
        What proving the optimum cost and what it proved.
    rows
        One `RestartRow` per seeding mode and restart count.
    single_restart_shortfalls
        Every single-restart shortfall, kept for the histogram.
    """

    n_rows: int
    n_bins: int
    certified_objective: float
    certified_nodes: int
    certified_seconds: float
    rows: list[RestartRow]
    single_restart_shortfalls: dict[str, list[float]] = field(repr=False, default_factory=dict)


def restart_hit_rates(
    *,
    n_rows: int = HITRATE_ROWS,
    n_bins: int = HITRATE_BINS,
    restarts: tuple[int, ...] = RESTART_COUNTS,
    trials: int = HITRATE_TRIALS,
    inits: tuple[str, ...] = INIT_MODES,
) -> HitRateStudy:
    """Measure how often multi-restart exchange reaches the certified optimum.

    Every trial is a genuine `scorequant.optimize_partition` call with
    ``n_restarts`` set, rather than a maximum reconstructed from single runs, so
    the reported hit rate is the one a user would experience. Trial ``t`` uses
    base seed ``t * max(restarts)``, which keeps the restart seeds of different
    trials disjoint at every restart count.

    Parameters
    ----------
    n_rows, n_bins
        The certified problem.
    restarts
        Restart counts to sweep.
    trials
        Independent trials per seeding mode and restart count.
    inits
        Seeding modes to compare.

    Returns
    -------
    HitRateStudy
        The certificate, the hit-rate rows, and the single-restart shortfalls.
    """
    split = certification_table(n_rows)
    start = time.perf_counter()
    certificate = sq.certify_partition(split.scores, weights=split.weights, n_bins=n_bins)
    certified_seconds = time.perf_counter() - start
    if certificate.status != "optimal":
        raise RuntimeError("the hit-rate problem must be certified before it is used")

    spacing = max(restarts)
    rows: list[RestartRow] = []
    shortfalls: dict[str, list[float]] = {}
    for init in inits:
        for n_restarts in restarts:
            objectives: list[float] = []
            begin = time.perf_counter()
            for trial in range(trials):
                run = sq.optimize_partition(
                    split.scores,
                    weights=split.weights,
                    n_bins=n_bins,
                    config=sq.DExchangeConfig(
                        seed=trial * spacing,
                        n_init=1,
                        n_restarts=n_restarts,
                        init=init,  # type: ignore[arg-type]
                    ),
                )
                objectives.append(float(run.objective))
            elapsed = time.perf_counter() - begin
            deficits = certificate.objective - np.asarray(objectives)
            hits = int(np.sum(deficits <= HIT_TOLERANCE))
            rows.append(
                RestartRow(
                    init=init,
                    n_restarts=n_restarts,
                    trials=trials,
                    hits=hits,
                    hit_rate=hits / trials,
                    median_shortfall=float(np.median(np.maximum(deficits, 0.0))),
                    seconds_per_trial=elapsed / trials,
                )
            )
            if n_restarts == 1:
                shortfalls[init] = [float(value) for value in np.maximum(deficits, 0.0)]

    return HitRateStudy(
        n_rows=n_rows,
        n_bins=n_bins,
        certified_objective=float(certificate.objective),
        certified_nodes=int(certificate.nodes_explored),
        certified_seconds=certified_seconds,
        rows=rows,
        single_restart_shortfalls=shortfalls,
    )


@dataclass(frozen=True, slots=True)
class ScalingRow:
    """The cost of one certification.

    Attributes
    ----------
    n_rows, n_bins
        Score atoms certified and cells requested.
    status
        ``"optimal"`` when the tree was exhausted, ``"budget_exhausted"``
        otherwise.
    nodes_explored, seconds
        Search nodes visited and wall-clock seconds.
    gap
        Outstanding ceiling minus the best objective found, exactly zero for a
        proved optimum.
    """

    n_rows: int
    n_bins: int
    status: str
    nodes_explored: int
    seconds: float
    gap: float


def certification_scaling(
    *,
    sizes: tuple[int, ...] = SCALING_ROWS,
    budgets: tuple[int, ...] = SCALING_BINS,
) -> list[ScalingRow]:
    """Measure what certification costs as the table and the budget grow.

    Parameters
    ----------
    sizes
        Atom counts to certify.
    budgets
        Cell budgets to certify at.

    Returns
    -------
    list of ScalingRow
        One row per configuration, in budget-major order.
    """
    rows: list[ScalingRow] = []
    for n_bins in budgets:
        for n_rows in sizes:
            split = certification_table(n_rows)
            start = time.perf_counter()
            certificate = sq.certify_partition(split.scores, weights=split.weights, n_bins=n_bins)
            rows.append(
                ScalingRow(
                    n_rows=n_rows,
                    n_bins=n_bins,
                    status=str(certificate.status),
                    nodes_explored=int(certificate.nodes_explored),
                    seconds=time.perf_counter() - start,
                    gap=float(certificate.gap),
                )
            )
    return rows


def budget_overrun(
    *, n_rows: int = OVERRUN_ROWS, n_bins: int = OVERRUN_BINS, max_nodes: int = OVERRUN_NODES
) -> ScalingRow:
    """Certify one instance that deliberately runs out of node budget.

    Parameters
    ----------
    n_rows, n_bins
        A configuration past the practical envelope.
    max_nodes
        Node budget, small enough that the run stops in seconds.

    Returns
    -------
    ScalingRow
        The downgraded certificate, whose gap is a genuine outstanding ceiling
        rather than a claim of optimality.
    """
    split = certification_table(n_rows)
    incumbent = sq.optimize_partition(split.scores, weights=split.weights, n_bins=n_bins)
    start = time.perf_counter()
    certificate = sq.certify_partition(
        split.scores,
        weights=split.weights,
        n_bins=n_bins,
        incumbent=incumbent.labels,
        config=sq.CertificationConfig(max_nodes=max_nodes),
    )
    return ScalingRow(
        n_rows=n_rows,
        n_bins=n_bins,
        status=str(certificate.status),
        nodes_explored=int(certificate.nodes_explored),
        seconds=time.perf_counter() - start,
        gap=float(certificate.gap),
    )


@dataclass(frozen=True, slots=True)
class Study:
    """Everything the page and the figure need from one deterministic run."""

    metrics: dict[str, object]
    cases: list[IncumbentCase] = field(repr=False)
    hit_rates: HitRateStudy = field(repr=False)
    scaling: list[ScalingRow] = field(repr=False)
    overrun: ScalingRow = field(repr=False)


def run_study(
    *,
    restarts: tuple[int, ...] | None = None,
    trials: int | None = None,
    sizes: tuple[int, ...] | None = None,
) -> Study:
    """Run the certificates, the restart study, and the scaling sweep.

    Parameters
    ----------
    restarts
        Restart counts to sweep. Defaults to the fast-mode aware list.
    trials
        Independent trials per restart count and seeding mode.
    sizes
        Atom counts of the scaling sweep.

    Returns
    -------
    Study
        The exact structure written to
        ``docs/examples/assets/global-certification.json``, plus the objects the
        figure draws.
    """
    resolved_restarts = (
        example_scale(RESTART_COUNTS, (1, 2, 4, 8)) if restarts is None else restarts
    )
    resolved_trials = example_scale(HITRATE_TRIALS, 12) if trials is None else trials
    resolved_sizes = example_scale(SCALING_ROWS, (12, 16, 20, 24)) if sizes is None else sizes

    cases = incumbent_cases()
    hit_rates = restart_hit_rates(restarts=resolved_restarts, trials=resolved_trials)
    scaling = certification_scaling(sizes=resolved_sizes)
    overrun = budget_overrun()

    metrics: dict[str, object] = {
        "incumbent_cases": [asdict(case) for case in cases],
        "hit_rates": {
            "n_rows": hit_rates.n_rows,
            "n_bins": hit_rates.n_bins,
            "certified_objective": hit_rates.certified_objective,
            "certified_nodes": hit_rates.certified_nodes,
            "certified_seconds": hit_rates.certified_seconds,
            "rows": [asdict(row) for row in hit_rates.rows],
            "single_restart_shortfalls": hit_rates.single_restart_shortfalls,
        },
        "scaling": [asdict(row) for row in scaling],
        "overrun": asdict(overrun),
    }
    return Study(
        metrics=metrics,
        cases=cases,
        hit_rates=hit_rates,
        scaling=scaling,
        overrun=overrun,
    )


def make_figure(study: Study) -> Figure:
    """Render the three-panel certification dashboard.

    Parameters
    ----------
    study
        The object returned by `run_study`.

    Returns
    -------
    matplotlib.figure.Figure
        The distribution of single-restart shortfalls, the hit rate against the
        number of restarts, and what certification costs as the table grows.
    """
    figure, axes = plt.subplots(1, 3, figsize=(16.0, 4.8), constrained_layout=True)
    palette = {"kmeans++": "#38618c", "random": "#c0563c"}

    study_rates = study.hit_rates
    for init, shortfalls in study_rates.single_restart_shortfalls.items():
        values = np.sort(np.maximum(np.asarray(shortfalls), 0.0))
        fraction = np.arange(values.shape[0]) / max(values.shape[0] - 1, 1)
        axes[0].step(
            fraction,
            values,
            where="post",
            color=palette.get(init, "#666666"),
            label=f"{init} seeding",
        )
    axes[0].axhline(0.0, color="#333333", linewidth=0.8, linestyle=":")
    axes[0].set(
        xlabel="single-restart runs, sorted",
        ylabel="shortfall from the certified optimum (nat)",
        title=f"{study_rates.n_rows} events, {study_rates.n_bins} cells",
    )
    axes[0].legend(loc="upper left", fontsize=8)

    for init in dict.fromkeys(row.init for row in study_rates.rows):
        group = [row for row in study_rates.rows if row.init == init]
        axes[1].plot(
            [row.n_restarts for row in group],
            [row.hit_rate for row in group],
            marker="o",
            color=palette.get(init, "#666666"),
            label=f"{init} seeding",
        )
    axes[1].axhline(1.0, color="#999999", linewidth=0.8, linestyle=":")
    axes[1].set(
        xscale="log",
        ylim=(0.0, 1.06),
        xlabel="independent exchange restarts",
        ylabel="runs reaching the certified optimum",
        title=f"Hit rate over {study_rates.rows[0].trials} trials",
    )
    axes[1].legend(loc="lower right", fontsize=8)

    markers = {3: "o", 4: "s", 5: "^"}
    for n_bins in dict.fromkeys(row.n_bins for row in study.scaling):
        group = [row for row in study.scaling if row.n_bins == n_bins]
        axes[2].plot(
            [row.n_rows for row in group],
            [row.nodes_explored for row in group],
            marker=markers.get(n_bins, "d"),
            color="#38618c" if n_bins == 3 else ("#4f9d69" if n_bins == 4 else "#c0563c"),
            label=f"{n_bins} cells",
        )
    overrun = study.overrun
    axes[2].scatter(
        [overrun.n_rows],
        [overrun.nodes_explored],
        marker="x",
        s=110,
        color="#333333",
        label=f"{overrun.n_bins} cells, stopped by a {overrun.nodes_explored - 1:,}-node budget",
    )
    axes[2].set(
        yscale="log",
        xlim=(10, 39),
        xlabel="score atoms certified",
        ylabel="search nodes explored",
        title="Certification is exponential",
    )
    axes[2].legend(loc="upper left", fontsize=8)

    figure.suptitle("What a certificate proves, and what restarts are worth")
    return figure


def main() -> None:
    """Run the study, then write the committed JSON and figure."""
    jax.config.update("jax_enable_x64", True)

    study = run_study()
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with METRICS_PATH.open("w", encoding="utf-8") as stream:
        json.dump(study.metrics, stream, indent=2)
        stream.write("\n")
    figure = make_figure(study)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURE_PATH, dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    main()
