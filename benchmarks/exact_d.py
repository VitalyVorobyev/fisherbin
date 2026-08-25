"""Deterministic exact-D scan benchmark; reports measurements, not promises."""

from __future__ import annotations

import argparse
import resource
from time import perf_counter

import jax
import numpy as np

import scorequant as sq


def main() -> None:
    """Run one moderate-scale exact-D optimization and print aggregate evidence."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=200_000)
    parser.add_argument("--dimensions", type=int, default=5)
    parser.add_argument("--bins", type=int, default=8)
    parser.add_argument("--max-sweeps", type=int, default=1)
    args = parser.parse_args()
    rng = np.random.default_rng(2026)
    scores = rng.normal(size=(args.rows, args.dimensions))
    weights = rng.uniform(0.5, 1.5, size=len(scores))
    started = perf_counter()
    result = sq.optimize_partition(
        scores,
        weights=weights,
        n_bins=args.bins,
        config=sq.DExchangeConfig(seed=2026, n_init=1, max_sweeps=args.max_sweeps),
    )
    jax.block_until_ready(result.labels)
    elapsed = perf_counter() - started
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024**2)
    print(
        {
            "rows": len(scores),
            "dimensions": scores.shape[1],
            "bins": result.n_bins,
            "elapsed_seconds": elapsed,
            "peak_rss_megabytes": peak_rss,
            "accepted_moves": result.accepted_moves,
            "exchange_stable": result.exchange_stable,
            "best_remaining_gain": result.best_remaining_gain,
        }
    )


if __name__ == "__main__":
    main()
