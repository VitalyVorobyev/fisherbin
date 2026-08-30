"""Render the soft-rule annealing figure for chapter 12.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch12_soft_hardening.py

The left panel follows one annealed soft-Voronoi fit: the retention of the
randomized rule it is actually optimizing, the retention of the hard rule its
centers imply, and the temperature schedule that connects them. The right panel
shows how the reported hardening gap collapses as the final temperature is
lowered.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np

import scorequant as sq

OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch12_soft_hardening.png"

MIXING = np.array([[1.0, 0.5], [0.0, 1.2]])
N_BINS = 4
MAX_STEPS = 300
RATIOS = (0.8, 0.5, 0.3, 0.2, 0.1, 0.05)


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)
    scores = np.random.default_rng(120).normal(size=(1_200, 2)) @ MIXING

    traced = sq.fit_quantizer(
        sq.ScoreSample(scores),
        n_bins=N_BINS,
        criterion=sq.DOptimality(),
        config=sq.SoftVoronoiConfig(
            seed=0,
            initializer_restarts=4,
            max_steps=MAX_STEPS,
            record_every=10,
            temperature_end_ratio=0.05,
        ),
        diagnostics="full",
    )
    trace = traced.trace
    steps = np.asarray(trace.steps)
    soft = np.asarray(trace.soft_retention)
    hard = np.asarray(trace.train_hard_retention)
    temperatures = np.asarray(trace.temperatures)

    gaps = []
    for ratio in RATIOS:
        fitted = sq.fit_quantizer(
            sq.ScoreSample(scores),
            n_bins=N_BINS,
            criterion=sq.DOptimality(),
            config=sq.SoftVoronoiConfig(
                seed=0,
                initializer_restarts=4,
                max_steps=MAX_STEPS,
                record_every=25,
                temperature_end_ratio=ratio,
            ),
        )
        gaps.append(abs(float(fitted.hardening_gap)))
    print(
        f"soft {soft[0]:.6f} -> {soft[-1]:.6f}; hard {hard[0]:.6f} -> {hard[-1]:.6f}; "
        f"gaps {np.round(gaps, 7)}"
    )

    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), constrained_layout=True)

    axes[0].plot(steps, soft, color="C0", linewidth=1.8, label="randomized rule (optimized)")
    axes[0].plot(steps, hard, color="C3", linewidth=1.8, label="hard rule (reported)")
    axes[0].set_xlabel("Adam steps")
    axes[0].set_ylabel("geometric mean retention")
    axes[0].set_ylim(0.0, 0.72)
    axes[0].legend(loc="lower left", fontsize=9)
    axes[0].set_title("one annealed fit:\nwhat is optimized and what is reported")

    twin = axes[0].twinx()
    twin.plot(steps, temperatures, color="0.45", linestyle=":", linewidth=1.5)
    twin.set_yscale("log")
    twin.set_ylabel(r"temperature $\tau$ (dotted)", color="0.35")
    twin.tick_params(axis="y", colors="0.35")

    axes[1].plot(RATIOS, gaps, marker="o", color="black", linewidth=1.6)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xticks(list(RATIOS), [f"{ratio:g}" for ratio in RATIOS], minor=False)
    axes[1].set_xticks([], [], minor=True)
    axes[1].set_xlabel(r"final temperature ratio $\tau_{\mathrm{end}}/\tau_0$")
    axes[1].set_ylabel("|hardening gap|")
    axes[1].set_title("the gap between the soft and hard\nobjectives closes with temperature")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
