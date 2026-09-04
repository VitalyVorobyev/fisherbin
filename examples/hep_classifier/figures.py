"""Committed figure for the HEP classifier showcase."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from .experiment import Study


def _mapping(metrics: dict[str, object], key: str) -> dict[str, object]:
    value = metrics[key]
    if not isinstance(value, dict):
        raise TypeError(f"metrics[{key!r}] must be a mapping")
    return value


def _rows(metrics: dict[str, object], key: str) -> list[dict[str, object]]:
    value = metrics[key]
    if not isinstance(value, list):
        raise TypeError(f"metrics[{key!r}] must be a list")
    return [row for row in value if isinstance(row, dict)]


def make_figure(study: Study) -> Figure:
    """Render the four-panel HEP classifier dashboard.

    Parameters
    ----------
    study
        The object returned by `examples.hep_classifier.experiment.run_study`.

    Returns
    -------
    matplotlib.figure.Figure
        Score-space scatter of the two ScoreQuant labelings, the headline
        full/profiled retention bars, the bin-budget sweep against the
        certified ceiling, and the delta convergence study.
    """
    metrics = study.metrics
    figure, axes = plt.subplots(2, 2, figsize=(13.0, 9.0), constrained_layout=True)

    axes[0, 0].scatter(
        study.signal_posterior,
        study.tes_score,
        c=study.ds_labels,
        cmap="tab10",
        s=10,
        alpha=0.7,
        linewidths=0,
    )
    axes[0, 0].set(
        xlabel="calibrated signal posterior $\\eta_s$",
        ylabel="tes score",
        title="Profiled $D_s$ cells in (signal posterior, tes score)",
    )

    partitions = _rows(metrics, "partitions")
    names = [str(row["label"]) for row in partitions]
    full_values = [float(row["full_retention"]) for row in partitions]
    profiled_values = [float(row["profiled_retention"]) for row in partitions]
    y = np.arange(len(names))
    axes[0, 1].barh(y - 0.2, full_values, height=0.4, label="full D", color="#38618c")
    axes[0, 1].barh(y + 0.2, profiled_values, height=0.4, label="profiled $D_s$", color="#c0563c")
    axes[0, 1].set(
        yticks=y,
        yticklabels=names,
        xlabel="retention",
        title="Every labeling, scored both ways",
    )
    axes[0, 1].legend()

    sweep = _rows(metrics, "ceiling_sweep")
    budgets = [float(row["n_bins"]) for row in sweep]
    axes[1, 0].plot(
        budgets,
        [float(row["ceiling_retention"]) for row in sweep],
        marker="^",
        linestyle="--",
        color="#666666",
        label="certified ceiling",
    )
    axes[1, 0].plot(
        budgets,
        [float(row["ds_profiled_retention"]) for row in sweep],
        marker="o",
        color="#38618c",
        label="ScoreQuant profiled $D_s$",
    )
    axes[1, 0].plot(
        budgets,
        [float(row["classifier_quantile_profiled_retention"]) for row in sweep],
        marker="s",
        color="#c0563c",
        label="classifier-quantile bins",
    )
    axes[1, 0].set(
        xlabel="bin budget",
        ylabel="profiled retention of mu_htautau",
        xticks=budgets,
        title="Bin-budget sweep against the certified ceiling",
    )
    axes[1, 0].legend()

    delta_rows = _rows(_mapping(metrics, "delta_convergence"), "rows")
    deltas = [float(row["delta"]) for row in delta_rows]
    axes[1, 1].plot(
        deltas,
        [float(row["ds_profiled_retention"]) for row in delta_rows],
        marker="o",
        color="#38618c",
        label="profiled $D_s$ retention",
    )
    axes[1, 1].plot(
        deltas,
        [float(row["minus_plus_auc"]) for row in delta_rows],
        marker="s",
        color="#4f9d69",
        label="minus/plus classifier AUC",
    )
    axes[1, 1].set(
        xlabel="delta",
        title="Three-point delta convergence study",
    )
    axes[1, 1].legend()

    figure.suptitle("FAIR Universe HiggsML classifier showcase")
    return figure
