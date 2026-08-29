"""Margins at exact global profiled-Ds optima (DS-MARGINS-AT-OPTIMA / OP28).

Falsification searches for OPEN-DS-MARGINS-AT-OPTIMA.  Three modes:

1. ``trend`` — like ``ds_population_bridge.py trend`` but on a fine dyadic
   grid (multiples of 1/2**16, emulating an atomless law while keeping exact
   rational arithmetic; the audit recorded that the 1/8-grid suite is atomic
   and therefore not evidence about atomless-law margins).  For each exact
   global optimum it additionally records the DS14 margin quantities that the
   original suite never measured:

   - (M2) minimum cell mass and singleton flag;
   - (M3) the exact nuisance block ``I_11``, exact ``det I`` and ``tr I``, and
     a float ``lambda_min(I)`` display value;
   - (M5) the exact minimum projected-centroid separation and the labeling's
     own regression slope ``B_hat = I_01/I_11`` versus the full-sample slope;
   - the **exact domination sandwich**:  with ``shat = s_psi - B*_N s_lam``
     built from the *full-sample* empirical information, every labeling ``z``
     satisfies (empirical DS11(a), then 1-D contiguity)

         Phi_s(z)  <=  between_shat(z)  <=  scalar-interval optimum of shat,

     both inequalities asserted in exact rationals for the optimum, together
     with the value gap and the partition distance between the Ds optimum and
     the best shat-interval labeling.  A single exact violation refutes the
     efficient-score reduction and is serialized immediately.

2. ``scalar`` — the extreme-cell question in its cleanest setting: exact
   optimal K-interval partitions (weighted 1-D k-means via the library's
   ``scalar_interval_dp``) of large i.i.d. Gaussian/light-tailed samples;
   tracks the minimum cell mass versus N against the population optimum.

3. ``popref`` — high-precision population reference: masses and value of the
   optimal K-interval quantizer of N(0,1) by Lloyd iteration on quadrature.

Everything claim-relevant in ``trend`` runs in ``fractions.Fraction``; floats
only screen the enumeration and render display columns.  Setting: d=2,
d_psi=1 (POI first), K=3, equal weights, scores centered by the exact sample
mean (convention of CE-DS-GLOBAL-GEOMETRY-001/-002).

Run:  uv run python agenticresearch/py/ds_margins_at_optima.py trend
      uv run python agenticresearch/py/ds_margins_at_optima.py scalar
      uv run python agenticresearch/py/ds_margins_at_optima.py popref
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from fractions import Fraction
from itertools import combinations, permutations

import numpy as np

from ds_population_bridge import (
    K,
    exact_cells,
    exact_info,
    exact_objective,
    exact_geometry_report,
    projected_separation,
    sample_law,
    screen_global,
)

FINE_DENOM = 2**16


# ----------------------------------------------------------------- sampling


def round_center_fine(raw: np.ndarray, denom: int = FINE_DENOM) -> list[list[Fraction]]:
    """Round to multiples of 1/denom, then center by the exact sample mean."""
    grid = [
        [Fraction(int(round(v * denom))), Fraction(int(round(w * denom)))] for v, w in raw
    ]
    n = len(grid)
    mean = [sum(row[c] for row in grid) / n for c in range(2)]
    return [[(row[c] - mean[c]) / denom for c in range(2)] for row in grid]


# ------------------------------------------------ exact efficient-score side


def full_information(scores: list[list[Fraction]]) -> list[list[Fraction]]:
    """Exact unbinned empirical information sum_i w s_i s_i^T (uncentered)."""
    n = len(scores)
    w = Fraction(1, n)
    return [
        [sum(w * row[r] * row[c] for row in scores) for c in range(2)] for r in range(2)
    ]


def efficient_score_values(scores: list[list[Fraction]]) -> tuple[list[Fraction], Fraction]:
    """shat_i = s_psi,i - B*_N s_lam,i with B*_N = I_01/I_11 of the full info."""
    info = full_information(scores)
    if info[1][1] == 0:
        raise ValueError("full-sample nuisance information is singular")
    slope = info[0][1] / info[1][1]
    return [row[0] - slope * row[1] for row in scores], slope


def between_value(shat: list[Fraction], labels: list[int], k: int) -> Fraction:
    """Uncentered between-cell second moment sum_b (sum_{i in b} w shat_i)^2/W_b."""
    n = len(shat)
    w = Fraction(1, n)
    masses = [Fraction(0)] * k
    sums = [Fraction(0)] * k
    for i, lab in enumerate(labels):
        masses[lab] += w
        sums[lab] += w * shat[i]
    return sum(sums[b] ** 2 / masses[b] for b in range(k) if masses[b] > 0)


def scalar_interval_optimum(
    shat: list[Fraction], k: int
) -> tuple[Fraction, list[int]]:
    """Exact optimal K-interval labeling of the shat values (all breakpoints).

    Optimal K-groupings of scalar values are contiguous in sorted order, so
    enumerating the C(n-1, k-1) breakpoint choices is exhaustive over all
    K-cell groupings.  Returns the exact optimal between-value and one
    optimal labeling in original row order.
    """
    n = len(shat)
    order = sorted(range(n), key=shat.__getitem__)
    best: Fraction | None = None
    best_cuts: tuple[int, ...] = ()
    for cuts in combinations(range(1, n), k - 1):
        bounds = (0, *cuts, n)
        labels = [0] * n
        for b in range(k):
            for pos in range(bounds[b], bounds[b + 1]):
                labels[order[pos]] = b
        val = between_value(shat, labels, k)
        if best is None or val > best:
            best = val
            best_cuts = cuts
    assert best is not None
    bounds = (0, *best_cuts, n)
    labels = [0] * n
    for b in range(k):
        for pos in range(bounds[b], bounds[b + 1]):
            labels[order[pos]] = b
    return best, labels


def partition_distance(a: list[int], b: list[int], k: int) -> int:
    """Minimum Hamming mismatches between labelings over label permutations."""
    n = len(a)
    return min(
        sum(1 for i in range(n) if perm[a[i]] != b[i]) for perm in permutations(range(k))
    )


def lambda_min_float(info: list[list[Fraction]]) -> float:
    """Float display value of lambda_min for an exact symmetric 2x2 matrix."""
    tr = info[0][0] + info[1][1]
    det = info[0][0] * info[1][1] - info[0][1] * info[1][0]
    disc = tr * tr - 4 * det
    return (float(tr) - math.sqrt(max(float(disc), 0.0))) / 2.0


# ------------------------------------------------------------------ trend


def run_trend(laws: list[str], sizes: list[int], reps: int) -> list[dict]:
    rows: list[dict] = []
    for law in laws:
        for n in sizes:
            for rep in range(reps):
                digest = hashlib.md5(f"margins-{law}-{n}-{rep}".encode()).digest()
                seed = 20260829 + int.from_bytes(digest[:4], "big")
                rng = np.random.default_rng(seed)
                scores_exact = round_center_fine(sample_law(law, n, rng))
                scores = np.array([[float(v) for v in row] for row in scores_exact])
                t0 = time.time()
                candidates = screen_global(scores)
                seen: set[tuple[int, ...]] = set()
                canonical: list[list[int]] = []
                for labs in candidates:
                    relabel: dict[int, int] = {}
                    canon = []
                    for v in labs:
                        canon.append(relabel.setdefault(int(v), len(relabel)))
                    key = tuple(canon)
                    if key not in seen:
                        seen.add(key)
                        canonical.append(canon)
                ranked = sorted(
                    (
                        (obj, labs)
                        for labs in canonical
                        if (obj := exact_objective(scores_exact, labs)) is not None
                    ),
                    reverse=True,
                )
                best_obj, best_labels = ranked[0]
                n_ties = sum(1 for obj, _ in ranked if obj == best_obj)
                geo = exact_geometry_report(scores_exact, best_labels)
                masses, _moments = exact_cells(scores_exact, best_labels)
                info = exact_info(masses, _moments)
                tr = info[0][0] + info[1][1]
                det = info[0][0] * info[1][1] - info[0][1] * info[1][0]
                sep = projected_separation(scores_exact, best_labels)
                slope_hat = info[0][1] / info[1][1]

                shat, slope_full = efficient_score_values(scores_exact)
                between_opt = between_value(shat, best_labels, K)
                scalar_opt, scalar_labels = scalar_interval_optimum(shat, K)
                sandwich_lower_ok = best_obj <= between_opt
                sandwich_upper_ok = between_opt <= scalar_opt
                dist = partition_distance(best_labels, scalar_labels, K)

                row = {
                    "law": law,
                    "n": n,
                    "rep": rep,
                    "seed": seed,
                    "grid_denom": FINE_DENOM,
                    "objective": str(best_obj),
                    "labels": best_labels,
                    "n_exact_ties": n_ties,
                    "min_mass": str(geo["min_mass"]),
                    "has_singleton": geo["min_mass"] == Fraction(1, n),
                    "nuisance_block": str(info[1][1]),
                    "nuisance_block_float": float(info[1][1]),
                    "info_trace": str(tr),
                    "info_det": str(det),
                    "lambda_min_float": lambda_min_float(info),
                    "min_proj_sep": str(sep),
                    "min_proj_sep_float": float(sep),
                    "slope_hat": str(slope_hat),
                    "slope_full": str(slope_full),
                    "slope_gap_float": float(abs(slope_hat - slope_full)),
                    "scalar_opt": str(scalar_opt),
                    "between_at_optimum": str(between_opt),
                    "sandwich_lower_ok": sandwich_lower_ok,
                    "sandwich_upper_ok": sandwich_upper_ok,
                    "value_gap_float": float(scalar_opt - best_obj),
                    "value_gap_rel_float": float((scalar_opt - best_obj) / scalar_opt)
                    if scalar_opt > 0
                    else float("nan"),
                    "partition_distance": dist,
                    "n_viol": geo["n_viol"],
                    "max_rel_viol": float(geo["max_rel_viol"]),
                    "ds6_bound_respected": geo["ds6_bound_respected"],
                    "screen_seconds": round(time.time() - t0, 1),
                }
                rows.append(row)
                print(
                    f"{law:12s} N={n:3d} rep={rep} ties={n_ties} "
                    f"min_mass={row['min_mass']:>8s} I11={row['nuisance_block_float']:.5f} "
                    f"lmin={row['lambda_min_float']:.5f} gap_rel={row['value_gap_rel_float']:.4f} "
                    f"pdist={dist} sandwich={'OK' if sandwich_lower_ok and sandwich_upper_ok else 'VIOLATED'} "
                    f"({row['screen_seconds']}s)",
                    flush=True,
                )
                if not (sandwich_lower_ok and sandwich_upper_ok):
                    print("SANDWICH VIOLATION — serialize this instance", flush=True)
    return rows


# ------------------------------------------------------------------ scalar


def run_scalar(sizes: list[int], reps: int, bins: list[int]) -> list[dict]:
    """Minimum cell mass of exact optimal K-interval partitions vs N.

    Uses the library's exact scalar DP (float64 arithmetic, exact program) on
    i.i.d. samples; the DP is the certified ground-truth solver for the 1-D
    weighted SSE problem, which is criterion-equivalent to scalar D.
    """
    from scorequant.quantizers import scalar_interval_dp

    laws = {
        "gauss": lambda rng, n: rng.standard_normal(n),
        "laplace": lambda rng, n: rng.laplace(size=n),
        "uniform": lambda rng, n: rng.uniform(-1.0, 1.0, size=n),
    }
    rows: list[dict] = []
    for law, draw in laws.items():
        for n in sizes:
            for k in bins:
                for rep in range(reps):
                    digest = hashlib.md5(f"scalar-{law}-{n}-{k}-{rep}".encode()).digest()
                    seed = 20260829 + int.from_bytes(digest[:4], "big")
                    rng = np.random.default_rng(seed)
                    values = draw(rng, n)
                    values = values - values.mean()
                    labels, _ = scalar_interval_dp(values, np.full(n, 1.0 / n), k)
                    counts = np.bincount(labels, minlength=k)
                    rows.append(
                        {
                            "law": law,
                            "n": n,
                            "k": k,
                            "rep": rep,
                            "seed": seed,
                            "min_count": int(counts.min()),
                            "min_mass": float(counts.min() / n),
                            "counts": [int(c) for c in counts],
                        }
                    )
        print(f"{law}: done", flush=True)
    return rows


def summarize_scalar(rows: list[dict]) -> None:
    table: dict[tuple[str, int, int], list[dict]] = {}
    for row in rows:
        table.setdefault((row["law"], row["k"], row["n"]), []).append(row)
    print(f"{'law':8s} {'K':>2s} {'N':>6s} {'reps':>4s} {'min_mass_min':>12s} "
          f"{'min_mass_med':>12s} {'singleton_frac':>14s}")
    for (law, k, n), group in sorted(table.items()):
        mm = sorted(r["min_mass"] for r in group)
        singleton = sum(1 for r in group if r["min_count"] == 1) / len(group)
        print(f"{law:8s} {k:2d} {n:6d} {len(group):4d} {mm[0]:12.5f} "
              f"{mm[len(mm) // 2]:12.5f} {singleton:14.2f}")


# ------------------------------------------------------------------ popref


def run_popref(bins: list[int]) -> None:
    """Population-optimal K-interval quantizer of N(0,1) via Lloyd iteration."""
    from scipy.stats import norm  # scipy ships with the dev environment

    for k in bins:
        edges = norm.ppf(np.linspace(0.0, 1.0, k + 1)[1:-1])
        for _ in range(50_000):
            full = np.concatenate([[-np.inf], edges, [np.inf]])
            masses = np.diff(norm.cdf(full))
            dens = norm.pdf(full[:-1]) - norm.pdf(full[1:])
            centroids = dens / masses
            new_edges = 0.5 * (centroids[:-1] + centroids[1:])
            if np.allclose(new_edges, edges, rtol=0, atol=1e-14):
                edges = new_edges
                break
            edges = new_edges
        full = np.concatenate([[-np.inf], edges, [np.inf]])
        masses = np.diff(norm.cdf(full))
        dens = norm.pdf(full[:-1]) - norm.pdf(full[1:])
        centroids = dens / masses
        value = float(np.sum(masses * centroids**2))
        print(
            f"K={k}: edges={np.round(edges, 6).tolist()} "
            f"masses={np.round(masses, 6).tolist()} min_mass={masses.min():.6f} "
            f"value={value:.6f}",
            flush=True,
        )


# -------------------------------------------------------------------- main


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "trend"
    if mode == "trend":
        laws = sys.argv[2].split(",") if len(sys.argv) > 2 else [
            "gauss06",
            "gauss09",
            "gauss095",
            "mix3",
            "heavy_nu",
            "tiny_cluster",
        ]
        sizes = (
            [int(v) for v in sys.argv[3].split(",")] if len(sys.argv) > 3 else [8, 10, 12, 14]
        )
        reps = int(sys.argv[4]) if len(sys.argv) > 4 else 3
        rows = run_trend(laws, sizes, reps)
        out = sys.argv[5] if len(sys.argv) > 5 else "ds_margins_trend.json"
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(rows, handle, indent=1)
        print(f"wrote {len(rows)} rows to {out}", flush=True)
        return
    if mode == "scalar":
        sizes = (
            [int(v) for v in sys.argv[2].split(",")]
            if len(sys.argv) > 2
            else [100, 300, 1000, 3000, 10000, 20000]
        )
        reps = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        bins = [int(v) for v in sys.argv[4].split(",")] if len(sys.argv) > 4 else [3, 4, 6]
        rows = run_scalar(sizes, reps, bins)
        out = sys.argv[5] if len(sys.argv) > 5 else "ds_margins_scalar.json"
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(rows, handle, indent=1)
        summarize_scalar(rows)
        print(f"wrote {len(rows)} rows to {out}", flush=True)
        return
    if mode == "popref":
        bins = [int(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else [3, 4, 6]
        run_popref(bins)
        return
    raise SystemExit(f"unknown mode {mode!r}; use trend | scalar | popref")


if __name__ == "__main__":
    main()
