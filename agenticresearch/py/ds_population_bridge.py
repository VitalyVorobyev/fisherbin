"""Growing-N geometry of exact global profiled-Ds optima (DS-POPULATION-BRIDGE).

Falsification searches for the finite-to-population Ds bridge (OP4/OP5):

1. ``trend``   — for fixed sampling laws, draw i.i.d. score samples of growing N,
   find the exact (exhaustively enumerated) global finite Ds optimum, and track
   (a) the maximum relative efficient-semimetric violation of its own
   nearest-cell rule, (b) the weight of rule-violating points, and
   (c) the minimum cell mass at the optimum.  A non-shrinking violation along a
   law with a nice atomless limit would kill the strongest bridge; violations
   forced to zero via DS-OKN-BOUND require the mass margin in (c) to persist.
2. ``degenerate`` — exact rational verification of the symmetric
   coincident-projected-centroid construction (population stationary Ds
   partitions that no efficient-semimetric rule can separate).

Everything claim-relevant is re-verified in ``fractions.Fraction``; floats are
used only to screen the exhaustive enumeration (top candidates are re-ranked
exactly, and the reported optimum is exact).

Setting: d=2, d_psi=1 (POI first coordinate), K=3, equal weights, scores
rounded to exact multiples of 1/8 and centered by the exact sample mean
(the convention of CE-DS-GLOBAL-GEOMETRY-001/-002).

Run:  uv run python agenticresearch/py/ds_population_bridge.py trend
      uv run python agenticresearch/py/ds_population_bridge.py degenerate
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from fractions import Fraction

import numpy as np

K = 3
D = 2
BATCH = 200_000
TOP_KEEP = 64
FLOAT_GUARD = 1e-9


# ----------------------------------------------------------------- sampling


GAUSS_RHO = {"gauss06": 0.6, "gauss09": 0.9, "gauss095": 0.95}


def sample_law(law: str, n: int, rng: np.random.Generator) -> np.ndarray:
    """Draw n raw score rows (before rounding/centering) from a named law."""
    if law in GAUSS_RHO:
        rho = GAUSS_RHO[law]
        cov = np.array([[1.0, rho], [rho, 1.0]])
        return rng.multivariate_normal(np.zeros(2), cov, size=n)
    if law == "mix3":
        centers = np.array([[-2.0, 0.0], [2.0, 1.0], [0.0, -1.5]])
        comp = rng.choice(3, size=n, p=[0.4, 0.4, 0.2])
        return centers[comp] + 0.55 * rng.standard_normal((n, 2))
    if law == "heavy_nu":
        s_psi = rng.standard_normal(n)
        s_lam = 0.5 * s_psi + rng.standard_t(2, size=n)
        return np.column_stack([s_psi, s_lam])
    if law == "tiny_cluster":
        comp = rng.random(n) < 0.05
        base = rng.standard_normal((n, 2))
        base[comp] = np.array([5.0, 5.0]) + 0.3 * base[comp]
        return base
    raise ValueError(law)


def round_center(raw: np.ndarray) -> list[list[Fraction]]:
    """Round to multiples of 1/8, then center by the exact sample mean."""
    eighths = [[Fraction(int(round(v * 8))), Fraction(int(round(w * 8)))] for v, w in raw]
    n = len(eighths)
    mean = [sum(row[c] for row in eighths) / n for c in range(2)]
    return [[(row[c] - mean[c]) / 8 for c in range(2)] for row in eighths]


# ------------------------------------------------- float exhaustive screening


def screen_global(scores: np.ndarray) -> list[np.ndarray]:
    """Return the TOP_KEEP labelings by float profiled-Ds objective.

    Enumerates all K^N labelings in batches (labeled partitions; the K!
    redundancy is harmless).  Labelings with an empty cell or a numerically
    invalid objective are discarded.
    """
    n = scores.shape[0]
    total = K**n
    powers = K ** np.arange(n, dtype=np.int64)
    best_vals: np.ndarray = np.empty(0)
    best_labs: np.ndarray = np.empty((0, n), dtype=np.int8)
    w = 1.0 / n
    for start in range(0, total, BATCH):
        idx = np.arange(start, min(start + BATCH, total), dtype=np.int64)
        labs = (idx[:, None] // powers[None, :]) % K
        masses = np.stack([(labs == c).sum(axis=1) * w for c in range(K)], axis=1)
        ok = (masses > 0).all(axis=1)
        moments = np.stack(
            [(labs == c).astype(np.float64) @ scores * w for c in range(K)], axis=1
        )
        with np.errstate(divide="ignore", invalid="ignore"):
            contrib = moments[:, :, :, None] * moments[:, :, None, :] / masses[:, :, None, None]
            info = contrib.sum(axis=1)
            i11 = info[:, 1, 1]
            obj = info[:, 0, 0] - info[:, 0, 1] ** 2 / np.where(i11 > 0, i11, np.nan)
        obj = np.where(ok & np.isfinite(obj) & (i11 > FLOAT_GUARD), obj, -np.inf)
        take = np.argsort(obj)[-TOP_KEEP:]
        best_vals = np.concatenate([best_vals, obj[take]])
        best_labs = np.concatenate([best_labs, labs[take].astype(np.int8)])
        order = np.argsort(best_vals)[-TOP_KEEP:]
        best_vals, best_labs = best_vals[order], best_labs[order]
    return [best_labs[i] for i in range(len(best_labs))[::-1]]


# ------------------------------------------------------- exact Ds evaluation


def exact_cells(
    scores: list[list[Fraction]], labels: list[int]
) -> tuple[list[Fraction], list[list[Fraction]]]:
    n = len(scores)
    w = Fraction(1, n)
    masses = [Fraction(0)] * K
    moments = [[Fraction(0), Fraction(0)] for _ in range(K)]
    for row, lab in enumerate(labels):
        masses[lab] += w
        for c in range(2):
            moments[lab][c] += w * scores[row][c]
    return masses, moments


def exact_info(masses: list[Fraction], moments: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [
            sum(moments[b][r] * moments[b][c] / masses[b] for b in range(K) if masses[b] > 0)
            for c in range(2)
        ]
        for r in range(2)
    ]


def exact_objective(scores: list[list[Fraction]], labels: list[int]) -> Fraction | None:
    masses, moments = exact_cells(scores, labels)
    if any(m == 0 for m in masses):
        return None
    info = exact_info(masses, moments)
    if info[1][1] == 0:
        return None
    return info[0][0] - info[0][1] * info[1][0] / info[1][1]


def exact_geometry_report(scores: list[list[Fraction]], labels: list[int]) -> dict:
    """Violations of the optimum's own efficient-semimetric nearest-cell rule.

    The semimetric is G_s = I^{-1} - E_lam I_ll^{-1} E_lam^T evaluated at the
    labeling's own binned information matrix (DS2), all in exact rationals.
    Relative violations are normalized by q_aa = u_a^T I^{-1} u_a as in
    DS-OKN-BOUND; the DS6 bound value w(1/W_a + 1/W_b) is reported alongside.
    """
    n = len(scores)
    w = Fraction(1, n)
    masses, moments = exact_cells(scores, labels)
    info = exact_info(masses, moments)
    det = info[0][0] * info[1][1] - info[0][1] * info[1][0]
    inv = [
        [info[1][1] / det, -info[0][1] / det],
        [-info[1][0] / det, info[0][0] / det],
    ]
    metric = [row[:] for row in inv]
    metric[1][1] -= 1 / info[1][1]
    means = [[moments[b][c] / masses[b] for c in range(2)] for b in range(K)]

    def quad(mat: list[list[Fraction]], row: int, b: int) -> Fraction:
        u = [scores[row][c] - means[b][c] for c in range(2)]
        return sum(u[r] * mat[r][c] * u[c] for r in range(2) for c in range(2))

    n_viol = 0
    viol_weight = Fraction(0)
    max_rel = Fraction(0)
    max_abs = Fraction(0)
    bound_ok = True
    for row, lab in enumerate(labels):
        dists = [quad(metric, row, b) for b in range(K)]
        best = min(range(K), key=dists.__getitem__)
        gap = dists[lab] - dists[best]
        if gap > 0:
            n_viol += 1
            viol_weight += w
            max_abs = max(max_abs, gap)
            q_aa = quad(inv, row, lab)
            if q_aa > 0:
                rel = gap / q_aa
                max_rel = max(max_rel, rel)
                if rel > w * (1 / masses[lab] + 1 / masses[best]):
                    bound_ok = False
    return {
        "n_viol": n_viol,
        "viol_weight": viol_weight,
        "max_rel_viol": max_rel,
        "max_abs_viol": max_abs,
        "min_mass": min(masses),
        "ds6_bound_respected": bound_ok,
    }


# ------------------------------------------------------------------ searches


def run_trend(laws: list[str], sizes: list[int], reps: int) -> list[dict]:
    rows: list[dict] = []
    for law in laws:
        for n in sizes:
            for rep in range(reps):
                digest = hashlib.md5(f"{law}-{n}-{rep}".encode()).digest()
                seed = 20260828 + int.from_bytes(digest[:4], "big")
                rng = np.random.default_rng(seed)
                scores_exact = round_center(sample_law(law, n, rng))
                scores = np.array([[float(v) for v in row] for row in scores_exact])
                t0 = time.time()
                candidates = screen_global(scores)
                ranked = sorted(
                    (
                        (obj, [int(v) for v in labs])
                        for labs in candidates
                        if (obj := exact_objective(scores_exact, [int(v) for v in labs]))
                        is not None
                    ),
                    reverse=True,
                )
                best_obj, best_labels = ranked[0]
                report = exact_geometry_report(scores_exact, best_labels)
                row = {
                    "law": law,
                    "n": n,
                    "rep": rep,
                    "seed": seed,
                    "objective": str(best_obj),
                    "labels": best_labels,
                    "n_viol": report["n_viol"],
                    "viol_weight": str(report["viol_weight"]),
                    "max_rel_viol": float(report["max_rel_viol"]),
                    "max_rel_viol_exact": str(report["max_rel_viol"]),
                    "min_mass": str(report["min_mass"]),
                    "ds6_bound_respected": report["ds6_bound_respected"],
                    "screen_seconds": round(time.time() - t0, 1),
                }
                rows.append(row)
                print(
                    f"{law:12s} N={n:3d} rep={rep} viol={row['n_viol']} "
                    f"max_rel={row['max_rel_viol']:.4f} min_mass={row['min_mass']:8s} "
                    f"bound_ok={row['ds6_bound_respected']} ({row['screen_seconds']}s)",
                    flush=True,
                )
    return rows


def run_degenerate() -> dict:
    """Exact check of the symmetric wasted-cell construction (K=4 quadrature).

    Law: uniform weights on 8 atoms symmetric under s_lam -> -s_lam.  Partition
    A: K=2 threshold in s_psi (its binned nuisance block is exactly singular:
    I_ll = 0, so its profiled objective is undefined).  Partition B: the same
    threshold with each side split by sign(s_lam) (K=4, nonsingular blocks).
    Claims verified exactly: B's profiled objective equals A's POI-block
    information (the lambda-split adds nuisance information but exactly zero
    profiled information); B's binned cross-information vanishes; B satisfies
    the first-order nearest-cell rule of its own efficient semimetric
    everywhere; and B's projected centroids coincide pairwise, so no
    efficient-semimetric rule can separate its cells.
    """
    atoms = [
        (Fraction(-3), Fraction(1)),
        (Fraction(-3), Fraction(-1)),
        (Fraction(-1), Fraction(2)),
        (Fraction(-1), Fraction(-2)),
        (Fraction(1), Fraction(1)),
        (Fraction(1), Fraction(-1)),
        (Fraction(3), Fraction(2)),
        (Fraction(3), Fraction(-2)),
    ]
    scores = [[a, b] for a, b in atoms]
    labels_a = [0 if row[0] < 0 else 1 for row in scores]
    labels_b = [
        (0 if row[0] < 0 else 2) + (0 if row[1] > 0 else 1) for row in scores
    ]

    def binned_info(
        labels: list[int], k: int
    ) -> tuple[list[list[Fraction]], list[Fraction], list[list[Fraction]]]:
        n = len(scores)
        w = Fraction(1, n)
        masses = [Fraction(0)] * k
        moments = [[Fraction(0), Fraction(0)] for _ in range(k)]
        for row, lab in enumerate(labels):
            masses[lab] += w
            for c in range(2):
                moments[lab][c] += w * scores[row][c]
        info = [
            [
                sum(moments[b][r] * moments[b][c] / masses[b] for b in range(k))
                for c in range(2)
            ]
            for r in range(2)
        ]
        return info, masses, moments

    info_a, _, _ = binned_info(labels_a, 2)
    info_b, masses_b, moments_b = binned_info(labels_b, 4)
    obj_b = info_b[0][0] - info_b[0][1] * info_b[1][0] / info_b[1][1]
    det = info_b[0][0] * info_b[1][1] - info_b[0][1] * info_b[1][0]
    inv = [
        [info_b[1][1] / det, -info_b[0][1] / det],
        [-info_b[1][0] / det, info_b[0][0] / det],
    ]
    metric = [row[:] for row in inv]
    metric[1][1] -= 1 / info_b[1][1]
    means = [[moments_b[b][c] / masses_b[b] for c in range(2)] for b in range(4)]
    viol = 0
    for row, lab in enumerate(labels_b):
        dists = [
            sum(
                (scores[row][r] - means[b][r]) * metric[r][c] * (scores[row][c] - means[b][c])
                for r in range(2)
                for c in range(2)
            )
            for b in range(4)
        ]
        if dists[lab] > min(dists):
            viol += 1
    # efficient projection e(s) = s_psi - (I01/I11) s_lam under the B-binned info
    slope = info_b[0][1] / info_b[1][1]
    projected = [means[b][0] - slope * means[b][1] for b in range(4)]
    result = {
        "k2_nuisance_block": str(info_a[1][1]),
        "k2_nuisance_block_singular": info_a[1][1] == 0,
        "k2_poi_information": str(info_a[0][0]),
        "objective_k4": str(obj_b),
        "k4_profiled_equals_k2_poi": obj_b == info_a[0][0],
        "k4_nuisance_block": str(info_b[1][1]),
        "cross_information_k4": str(info_b[0][1]),
        "first_order_violations_k4": viol,
        "projected_centroids": [str(p) for p in projected],
        "projected_centroids_coincide_pairwise": projected[0] == projected[1]
        and projected[2] == projected[3],
    }
    print(json.dumps(result, indent=2))
    return result


def leverage_check(scores: list[list[Fraction]], labels: list[int]) -> dict:
    """Exact check of the profiled leverage stability bound at a labeling.

    For every admissible one-point move (source cell non-singleton), verify

        s_aa - s_bb <= beta * q_aa * q_bb,   beta = w W_b / (W_b + w),

    where s_xx = u_x^T G_s u_x, q_xx = u_x^T I^{-1} u_x.  The bound is an
    exact consequence of one-point exchange stability, so it must hold at any
    global optimum.  Returns the number of checked moves, violations, and the
    maximum slack ratio (s_aa - s_bb)/(beta q_aa q_bb) over improving-side
    moves.
    """
    n = len(scores)
    w = Fraction(1, n)
    masses, moments = exact_cells(scores, labels)
    info = exact_info(masses, moments)
    det = info[0][0] * info[1][1] - info[0][1] * info[1][0]
    inv = [
        [info[1][1] / det, -info[0][1] / det],
        [-info[1][0] / det, info[0][0] / det],
    ]
    metric = [row[:] for row in inv]
    metric[1][1] -= 1 / info[1][1]
    means = [[moments[b][c] / masses[b] for c in range(2)] for b in range(K)]

    def quad(mat: list[list[Fraction]], row: int, b: int) -> Fraction:
        u = [scores[row][c] - means[b][c] for c in range(2)]
        return sum(u[r] * mat[r][c] * u[c] for r in range(2) for c in range(2))

    checked = 0
    violations = 0
    max_ratio = Fraction(0)
    counts = [labels.count(b) for b in range(K)]
    for row, lab in enumerate(labels):
        if counts[lab] <= 1:
            continue
        s_aa = quad(metric, row, lab)
        q_aa = quad(inv, row, lab)
        for b in range(K):
            if b == lab:
                continue
            checked += 1
            s_bb = quad(metric, row, b)
            q_bb = quad(inv, row, b)
            beta = w * masses[b] / (masses[b] + w)
            bound = beta * q_aa * q_bb
            gap = s_aa - s_bb
            if gap > bound:
                violations += 1
            if gap > 0 and bound > 0:
                max_ratio = max(max_ratio, gap / bound)
    return {"checked": checked, "violations": violations, "max_ratio": max_ratio}


def projected_separation(scores: list[list[Fraction]], labels: list[int]) -> Fraction:
    """Minimum pairwise separation of projected centroids e_b = mu_psi - B mu_lam."""
    masses, moments = exact_cells(scores, labels)
    info = exact_info(masses, moments)
    slope = info[0][1] / info[1][1]
    means = [[moments[b][c] / masses[b] for c in range(2)] for b in range(K)]
    projected = [means[b][0] - slope * means[b][1] for b in range(K)]
    return min(
        abs(projected[b] - projected[c]) for b in range(K) for c in range(b + 1, K)
    )


def run_analyze(paths: list[str]) -> None:
    """Aggregate trend results and re-verify optima exactly.

    Recomputes each stored optimum's scores from its stored seed, then checks
    the leverage stability bound and the projected-centroid separation in
    exact arithmetic, and prints a per-(law, N) trend table.
    """
    rows = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            rows.extend(json.load(handle))
    total_checked = total_viol = 0
    max_ratio = Fraction(0)
    table: dict[tuple[str, int], list[dict]] = {}
    for row in rows:
        rng = np.random.default_rng(row["seed"])
        scores_exact = round_center(sample_law(row["law"], row["n"], rng))
        report = leverage_check(scores_exact, row["labels"])
        sep = projected_separation(scores_exact, row["labels"])
        row["min_proj_sep"] = float(sep)
        total_checked += report["checked"]
        total_viol += report["violations"]
        max_ratio = max(max_ratio, report["max_ratio"])
        table.setdefault((row["law"], row["n"]), []).append(row)
    print(f"leverage bound: {total_checked} moves checked, {total_viol} violations, "
          f"max gap/bound ratio {float(max_ratio):.4f}")
    print(f"{'law':12s} {'N':>3s} {'reps':>4s} {'mean_max_rel':>12s} {'worst_rel':>10s} "
          f"{'mean_nviol':>10s} {'min_mass':>9s} {'min_projsep':>11s}")
    for (law, n), group in sorted(table.items()):
        mean_rel = sum(r["max_rel_viol"] for r in group) / len(group)
        worst = max(r["max_rel_viol"] for r in group)
        mean_nv = sum(r["n_viol"] for r in group) / len(group)
        min_mass = min(Fraction(r["min_mass"]) for r in group)
        min_sep = min(r["min_proj_sep"] for r in group)
        print(f"{law:12s} {n:3d} {len(group):4d} {mean_rel:12.4f} {worst:10.4f} "
              f"{mean_nv:10.2f} {str(min_mass):>9s} {min_sep:11.4f}")


def run_fixture_leverage() -> None:
    """Exact leverage-bound check on the two canonical Ds counterexamples."""
    import pathlib

    base = pathlib.Path(__file__).resolve().parents[1] / "COUNTEREXAMPLES"
    for name in ("CE-DS-GLOBAL-GEOMETRY-001", "CE-DS-GLOBAL-GEOMETRY-002"):
        with open(base / f"{name}.json", encoding="utf-8") as handle:
            fix = json.load(handle)
        scores = [[Fraction(v) for v in row] for row in fix["scores"]]
        labels = list(fix["labels_after_or_optimum"])
        report = leverage_check(scores, labels)
        print(f"{name}: checked={report['checked']} violations={report['violations']} "
              f"max_ratio={float(report['max_ratio']):.4f}")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "trend"
    if mode == "degenerate":
        run_degenerate()
        return
    if mode == "analyze":
        run_analyze(sys.argv[2:])
        return
    if mode == "leverage":
        run_fixture_leverage()
        return
    laws = sys.argv[2].split(",") if len(sys.argv) > 2 else [
        "gauss06",
        "gauss09",
        "mix3",
        "heavy_nu",
        "tiny_cluster",
    ]
    sizes = [int(v) for v in sys.argv[3].split(",")] if len(sys.argv) > 3 else [8, 10, 12, 14]
    reps = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    rows = run_trend(laws, sizes, reps)
    out = sys.argv[5] if len(sys.argv) > 5 else "ds_population_bridge_results.json"
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=1)
    print(f"wrote {len(rows)} rows to {out}", flush=True)


if __name__ == "__main__":
    main()
