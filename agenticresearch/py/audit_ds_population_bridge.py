"""Independent adversarial falsification suite for the DS-POPULATION-BRIDGE audit.

Audits DS11-DS14 (packet AUDIT-DS-POPULATION-BRIDGE) with pure-stdlib exact
rational arithmetic: no numpy, no floats, and no shared code with the
researcher's py/ds_population_bridge.py. Every quantity that decides a claim is
a fractions.Fraction.

Modes (run as: uv run python agenticresearch/py/audit_ds_population_bridge.py <mode>):

  ds11      variational identity S_psi^+(I) = min_B V(B) on deterministic
            pseudo-random exact PSD instances, including singular nuisance
            blocks and multiple normal-equation solutions; plus the
            pseudo-inverse discontinuity witness for the DS11(a) K->infty
            remark (why I_ll^full > 0 must be assumed).
  ds13      exhaustive exact verification of the DS13 leverage bound at EVERY
            one-point exchange-stable state (not only optima) over adversarial
            datasets: duplicates, unequal weights, exact ties, vector nuisance
            (d_lambda=2), vector POI (d_psi=2), and nuisance-symmetric scores
            that generate singular-destination moves.
  fixtures  independent re-verification of CE-DS-DEGENERATE-GLOBAL-TIE-001 and
            CE-DS-POP-WASTED-CELLS-001 from their raw scores.
  margins   independent exact global-optimum margin scan at N=10 (own integer
            LCG datasets, full exact enumeration, no float screen): singleton
            cells, tie multiplicity, projected-centroid separation, and the
            DS13/DS6 bounds at the exact optimum.
  all       every mode in sequence.

Exit is nonzero on any violated claim-relevant identity or bound.
"""

from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]

# ----------------------------------------------------------------------------
# Exact rational linear algebra (dimensions <= 4).
# ----------------------------------------------------------------------------


def mat_zeros(n, m):
    return [[Fraction(0)] * m for _ in range(n)]


def mat_add(a, b):
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def mat_sub(a, b):
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def mat_mul(a, b):
    n, k, m = len(a), len(b), len(b[0])
    out = mat_zeros(n, m)
    for i in range(n):
        for j in range(m):
            out[i][j] = sum(a[i][t] * b[t][j] for t in range(k))
    return out


def mat_t(a):
    return [list(row) for row in zip(*a)]


def det(a):
    n = len(a)
    if n == 1:
        return a[0][0]
    if n == 2:
        return a[0][0] * a[1][1] - a[0][1] * a[1][0]
    total = Fraction(0)
    for j in range(n):
        minor = [row[:j] + row[j + 1 :] for row in a[1:]]
        sign = -1 if j % 2 else 1
        total += sign * a[0][j] * det(minor)
    return total


def inv(a):
    n = len(a)
    d = det(a)
    if d == 0:
        raise ZeroDivisionError("singular matrix")
    if n == 1:
        return [[1 / d]]
    cof = mat_zeros(n, n)
    for i in range(n):
        for j in range(n):
            minor = [row[:j] + row[j + 1 :] for k, row in enumerate(a) if k != i]
            sign = -1 if (i + j) % 2 else 1
            cof[i][j] = sign * det(minor)
    return [[cof[j][i] / d for j in range(n)] for i in range(n)]


def quad(u, g, v):
    """u^T G v for vectors u, v."""
    return sum(u[i] * g[i][j] * v[j] for i in range(len(u)) for j in range(len(v)))


def submat(a, rows, cols):
    return [[a[i][j] for j in cols] for i in rows]


def is_psd(a):
    """Exact PSD test for symmetric a (n <= 4): all principal minors >= 0."""
    n = len(a)
    for r in range(1, n + 1):
        for idx in itertools.combinations(range(n), r):
            if det(submat(a, idx, idx)) < 0:
                return False
    return True


def solve_sym(a, rhs):
    """Solve a X = rhs (a symmetric PSD, possibly singular) over Fractions.

    Returns (particular_solution, kernel_basis). Raises if inconsistent.
    rhs is n x m; solution is n x m; kernel basis vectors are length-n lists.
    """
    n = len(a)
    m = len(rhs[0])
    aug = [[a[i][j] for j in range(n)] + [rhs[i][j] for j in range(m)] for i in range(n)]
    pivots = []
    row = 0
    for col in range(n):
        piv = next((r for r in range(row, n) if aug[r][col] != 0), None)
        if piv is None:
            continue
        aug[row], aug[piv] = aug[piv], aug[row]
        pv = aug[row][col]
        aug[row] = [x / pv for x in aug[row]]
        for r in range(n):
            if r != row and aug[r][col] != 0:
                f = aug[r][col]
                aug[r] = [x - f * y for x, y in zip(aug[r], aug[row])]
        pivots.append(col)
        row += 1
    for r in range(row, n):
        if any(aug[r][n + j] != 0 for j in range(m)):
            raise ValueError("inconsistent system: range condition violated")
    x = mat_zeros(n, m)
    for r, col in enumerate(pivots):
        for j in range(m):
            x[col][j] = aug[r][n + j]
    free = [c for c in range(n) if c not in pivots]
    kernel = []
    for fc in free:
        v = [Fraction(0)] * n
        v[fc] = Fraction(1)
        for r, col in enumerate(pivots):
            v[col] = -aug[r][fc]
        kernel.append(v)
    return x, kernel


# ----------------------------------------------------------------------------
# Binned information and the profiled-Ds machinery.
# ----------------------------------------------------------------------------


def binned_moments(scores, weights, labels, k):
    """Per-cell (W_b, m_b); every cell must be nonempty."""
    d = len(scores[0])
    masses = [Fraction(0)] * k
    moments = [[Fraction(0)] * d for _ in range(k)]
    for s, w, b in zip(scores, weights, labels):
        masses[b] += w
        for j in range(d):
            moments[b][j] += w * s[j]
    if any(m == 0 for m in masses):
        raise ValueError("empty cell")
    return masses, moments


def info_matrix(masses, moments):
    d = len(moments[0])
    info = mat_zeros(d, d)
    for wb, mb in zip(masses, moments):
        for i in range(d):
            for j in range(d):
                info[i][j] += mb[i] * mb[j] / wb
    return info


def state(scores, weights, labels, k, poi, nuis):
    masses, moments = binned_moments(scores, weights, labels, k)
    info = info_matrix(masses, moments)
    lam = submat(info, nuis, nuis)
    return masses, moments, info, det(info), det(lam)


def efficient_semimetric(info, poi, nuis):
    """G_s = I^{-1} - E_lam I_ll^{-1} E_lam^T (requires both nonsingular)."""
    d = len(info)
    h = inv(info)
    lam_inv = inv(submat(info, nuis, nuis))
    g = [[h[i][j] for j in range(d)] for i in range(d)]
    for a, i in enumerate(nuis):
        for b, j in enumerate(nuis):
            g[i][j] -= lam_inv[a][b]
    return g, h


def is_exchange_stable(scores, weights, labels, k, poi, nuis, det_i, det_l):
    """No admissible one-point move strictly improves det I / det I_ll.

    A move is admissible iff its source cell keeps another point. A move to an
    infeasible (singular) state has profiled value -inf and never improves.
    """
    counts = [0] * k
    for b in labels:
        counts[b] += 1
    n = len(scores)
    for i in range(n):
        a = labels[i]
        if counts[a] <= 1:
            continue
        for b in range(k):
            if b == a:
                continue
            new_labels = list(labels)
            new_labels[i] = b
            masses, moments = binned_moments(scores, weights, new_labels, k)
            info2 = info_matrix(masses, moments)
            d2i = det(info2)
            d2l = det(submat(info2, nuis, nuis))
            if d2i <= 0 or d2l <= 0:
                continue
            if d2i * det_l > det_i * d2l:
                return False
    return True


def leverage_report(scores, weights, labels, k, poi, nuis):
    """Check DS13 (and DS6) at a feasible state for every admissible move.

    Returns dict with counters; raises AssertionError on any DS13 violation.
    """
    masses, moments, info, det_i, det_l = state(scores, weights, labels, k, poi, nuis)
    assert det_i > 0 and det_l > 0, "leverage check requires a feasible state"
    g, h = efficient_semimetric(info, poi, nuis)
    mus = [[m / w for m in mom] for w, mom in zip(masses, moments)]
    counts = [0] * k
    for b in labels:
        counts[b] += 1
    checked = 0
    degenerate_dest = 0
    max_ratio = None
    ds6_ok = True
    for i, (s, w) in enumerate(zip(scores, weights)):
        a = labels[i]
        if counts[a] <= 1:
            continue
        ua = [s[j] - mus[a][j] for j in range(len(s))]
        s_aa = quad(ua, g, ua)
        q_aa = quad(ua, h, ua)
        for b in range(k):
            if b == a:
                continue
            ub = [s[j] - mus[b][j] for j in range(len(s))]
            s_bb = quad(ub, g, ub)
            q_bb = quad(ub, h, ub)
            beta = w * masses[b] / (masses[b] + w)
            lhs = s_aa - s_bb
            rhs = beta * q_aa * q_bb
            assert lhs <= rhs, (
                f"DS13 VIOLATION: point {i} {a}->{b}: "
                f"{lhs} > {rhs} at labels {labels}"
            )
            checked += 1
            if lhs > 0 and rhs > 0:
                ratio = lhs / rhs
                if max_ratio is None or ratio > max_ratio:
                    max_ratio = ratio
            if q_aa > 0 and s_aa - s_bb > q_aa * w * (1 / masses[a] + 1 / masses[b]):
                ds6_ok = False
            new_labels = list(labels)
            new_labels[i] = b
            m2, mm2 = binned_moments(scores, weights, new_labels, k)
            if det(submat(info_matrix(m2, mm2), nuis, nuis)) == 0:
                degenerate_dest += 1
    return {
        "checked": checked,
        "degenerate_destination_moves": degenerate_dest,
        "max_ratio": None if max_ratio is None else str(max_ratio),
        "ds6_ok": ds6_ok,
    }


def canonical_labelings(n, k):
    """All surjective labelings in canonical (first-occurrence) order."""
    for labels in itertools.product(range(k), repeat=n):
        seen = []
        ok = True
        for b in labels:
            if b not in seen:
                if b != len(seen):
                    ok = False
                    break
                seen.append(b)
        if ok and len(seen) == k:
            yield list(labels)


# ----------------------------------------------------------------------------
# Deterministic integers without floats.
# ----------------------------------------------------------------------------


class Lcg:
    """Tiny deterministic integer generator (Numerical-Recipes constants)."""

    def __init__(self, seed):
        self.state = seed & 0xFFFFFFFF

    def next_int(self, lo, hi):
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return lo + (self.state >> 16) % (hi - lo + 1)


# ----------------------------------------------------------------------------
# Mode: ds11.
# ----------------------------------------------------------------------------


def run_ds11(trials=400):
    rng = Lcg(20260828)
    singular_cases = 0
    multi_solution_cases = 0
    for trial in range(trials):
        d_psi = 1 + rng.next_int(0, 1)
        d_lam = 1 + rng.next_int(0, 1)
        d = d_psi + d_lam
        k_rows = d + rng.next_int(0, 1)
        r = [[Fraction(rng.next_int(-3, 3)) for _ in range(d)] for _ in range(k_rows)]
        if rng.next_int(0, 2) == 0 and d_lam == 2:
            # Force a singular nuisance block: second nuisance column is a
            # multiple of the first.
            c = Fraction(rng.next_int(-2, 2))
            for row in r:
                row[d_psi + 1] = c * row[d_psi]
        info = mat_mul(mat_t(r), r)
        poi = list(range(d_psi))
        nuis = list(range(d_psi, d))
        i_pp = submat(info, poi, poi)
        i_pl = submat(info, poi, nuis)
        i_lp = submat(info, nuis, poi)
        i_ll = submat(info, nuis, nuis)
        # Normal equation B I_ll = I_pl, i.e. I_ll B^T = I_lp.
        bt, kernel = solve_sym(i_ll, i_lp)  # consistency asserts range condition
        b0 = mat_t(bt)

        def value(b):
            return mat_sub(
                mat_sub(i_pp, mat_mul(b, i_lp)),
                mat_sub(mat_mul(i_pl, mat_t(b)), mat_mul(mat_mul(b, i_ll), mat_t(b))),
            )

        v0 = value(b0)
        if det(i_ll) != 0:
            schur = mat_sub(i_pp, mat_mul(mat_mul(i_pl, inv(i_ll)), i_lp))
            assert v0 == schur, "V(B0) != Schur complement on nonsingular block"
        else:
            singular_cases += 1
        if kernel:
            multi_solution_cases += 1
            shift = kernel[0]
            coeffs = [Fraction(rng.next_int(-2, 2)) for _ in range(d_psi)]
            b_alt = [
                [b0[i][j] + coeffs[i] * shift[j] for j in range(d_lam)]
                for i in range(d_psi)
            ]
            assert value(b_alt) == v0, "normal-equation solutions disagree on V"
        for _ in range(3):
            b_rand = [
                [Fraction(rng.next_int(-4, 4), 1 + rng.next_int(0, 2)) for _ in range(d_lam)]
                for _ in range(d_psi)
            ]
            diff = mat_sub(value(b_rand), v0)
            delta = mat_sub(b_rand, b0)
            recon = mat_mul(mat_mul(delta, i_ll), mat_t(delta))
            assert diff == recon, "completion-of-squares identity failed"
            assert is_psd(diff), "V(B) - V(B0) not PSD"
    # Pseudo-inverse discontinuity witness for DS11(a): I_ll(k) = diag(1, 1/k)
    # with I_pl = [1, 1] gives B*_k = [1, k] -> unbounded, while the pseudo-
    # inverse of the singular limit gives [1, 0]. Hence the K->infty statement
    # requires a nonsingular full nuisance block.
    for k in (2, 8, 64):
        i_ll_k = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1, k)]]
        b_k = mat_mul([[Fraction(1), Fraction(1)]], inv(i_ll_k))
        assert b_k[0][1] == k, "discontinuity witness broke"
    return {
        "trials": trials,
        "singular_nuisance_cases": singular_cases,
        "multi_solution_cases": multi_solution_cases,
        "pseudo_inverse_discontinuity_witnessed": True,
    }


# ----------------------------------------------------------------------------
# Mode: ds13.
# ----------------------------------------------------------------------------

DS13_DATASETS = [
    {
        "name": "d2-duplicates-unequal-K3",
        "scores": [(1, 1), (1, 1), (-1, 1), (2, -1), (-2, -1), (0, 2), (0, -2)],
        "weights": ["1/4", "1/8", "1/8", "1/8", "1/8", "1/8", "1/8"],
        "K": 3,
        "poi": [0],
        "nuis": [1],
    },
    {
        # Uncentered on purpose: centered d=2 scores make every K=2 state
        # rank-deficient (U4), so the K=2 probe must shift the POI coordinate.
        "name": "d2-nuisance-symmetric-uncentered-K2",
        "scores": [(-2, 1), (-2, -1), (0, 2), (0, -2), (2, 1), (2, -1), (4, 2), (4, -2)],
        "weights": ["1/8"] * 8,
        "K": 2,
        "poi": [0],
        "nuis": [1],
    },
    {
        "name": "d2-nuisance-symmetric-K3",
        "scores": [(-3, 1), (-3, -1), (-1, 2), (-1, -2), (1, 1), (1, -1), (3, 2), (3, -2)],
        "weights": ["1/8"] * 8,
        "K": 3,
        "poi": [0],
        "nuis": [1],
    },
    {
        "name": "d3-vector-nuisance-K3",
        "scores": [
            (2, 1, 0),
            (-1, 1, 1),
            (0, -2, 1),
            (1, 0, -1),
            (-2, -1, 0),
            (1, 2, 2),
            (-1, -1, -2),
        ],
        "weights": ["1/7"] * 7,
        "K": 3,
        "poi": [0],
        "nuis": [1, 2],
    },
    {
        "name": "d3-vector-poi-K3",
        "scores": [
            (1, 0, 1),
            (0, 1, -1),
            (-1, 1, 0),
            (2, -1, 1),
            (-1, -2, -1),
            (0, 2, 2),
            (-1, -1, -2),
        ],
        "weights": ["1/4", "1/8", "1/8", "1/8", "1/8", "1/8", "1/8"],
        "K": 3,
        "poi": [0, 1],
        "nuis": [2],
    },
]


def run_ds13():
    results = []
    for ds in DS13_DATASETS:
        scores = [tuple(Fraction(x) for x in row) for row in ds["scores"]]
        weights = [Fraction(w) for w in ds["weights"]]
        k, poi, nuis = ds["K"], ds["poi"], ds["nuis"]
        n_feasible = n_stable = n_checked = n_degenerate = 0
        max_ratio = None
        for labels in canonical_labelings(len(scores), k):
            masses, moments, info, det_i, det_l = state(scores, weights, labels, k, poi, nuis)
            if det_i <= 0 or det_l <= 0:
                continue
            n_feasible += 1
            if not is_exchange_stable(scores, weights, labels, k, poi, nuis, det_i, det_l):
                continue
            n_stable += 1
            rep = leverage_report(scores, weights, labels, k, poi, nuis)
            n_checked += rep["checked"]
            n_degenerate += rep["degenerate_destination_moves"]
            if rep["max_ratio"] is not None:
                ratio = Fraction(rep["max_ratio"])
                if max_ratio is None or ratio > max_ratio:
                    max_ratio = ratio
        assert n_stable > 0, f"{ds['name']}: no stable state found"
        results.append(
            {
                "dataset": ds["name"],
                "feasible_states": n_feasible,
                "stable_states": n_stable,
                "moves_checked": n_checked,
                "degenerate_destination_moves": n_degenerate,
                "violations": 0,
                "max_gap_over_bound": None if max_ratio is None else str(max_ratio),
            }
        )
    return results


# ----------------------------------------------------------------------------
# Mode: fixtures.
# ----------------------------------------------------------------------------


def profiled_value(info, poi, nuis):
    """det S_psi = det I / det I_ll; None when the nuisance block is singular."""
    dl = det(submat(info, nuis, nuis))
    if dl == 0:
        return None
    return det(info) / dl


def projected_centroids(info, masses, moments, poi, nuis):
    """e_b = mu_b,psi - B*_q mu_b,lam for scalar-POI d=2 fixtures."""
    b_star = info[poi[0]][nuis[0]] / info[nuis[0]][nuis[0]]
    out = []
    for w, m in zip(masses, moments):
        mu = [x / w for x in m]
        out.append(mu[poi[0]] - b_star * mu[nuis[0]])
    return out


def run_fixtures():
    out = {}
    # --- CE-DS-DEGENERATE-GLOBAL-TIE-001 -----------------------------------
    fx = json.loads((WORKSPACE / "COUNTEREXAMPLES/CE-DS-DEGENERATE-GLOBAL-TIE-001.json").read_text())
    scores = [tuple(Fraction(x) for x in row) for row in fx["scores"]]
    weights = [Fraction(w) for w in fx["weights"]]
    k, poi, nuis = fx["K"], fx["poi_indices"], fx["nuisance_indices"]
    values = []
    infeasible = []
    for labels in canonical_labelings(len(scores), k):
        masses, moments = binned_moments(scores, weights, labels, k)
        info = info_matrix(masses, moments)
        val = profiled_value(info, poi, nuis)
        if val is None:
            infeasible.append((labels, info))
        else:
            values.append((val, labels))
    n_partitions = len(values) + len(infeasible)
    assert n_partitions == 966, n_partitions
    assert len(infeasible) == 2, len(infeasible)
    best = max(v for v, _ in values)
    assert best == Fraction(1083, 4096), best
    ties = [labels for v, labels in values if v == best]
    assert len(ties) == 31, len(ties)
    next_best = max(v for v, _ in values if v != best)
    assert best - next_best == Fraction(237, 16640), best - next_best
    reduced = ({0, 1, 2, 4, 6, 7}, {3, 5})
    coincident = 0
    for labels in ties:
        cells = [set(i for i, b in enumerate(labels) if b == c) for c in range(k)]
        assert all(
            cell <= reduced[0] or cell <= reduced[1] for cell in cells
        ), f"tie {labels} does not refine the reduced bipartition"
        masses, moments = binned_moments(scores, weights, labels, k)
        info = info_matrix(masses, moments)
        cents = projected_centroids(info, masses, moments, poi, nuis)
        if any(cents[i] == cents[j] for i in range(k) for j in range(i + 1, k)):
            coincident += 1
    assert coincident == 31, coincident
    # The infeasible nuisance-mean-equal refinement and its pseudo-inverse value.
    target_cells = ({0, 1, 6}, {2, 4, 7}, {3, 5})
    found = None
    for labels, info in infeasible:
        cells = tuple(
            frozenset(i for i, b in enumerate(labels) if b == c) for c in range(k)
        )
        if set(cells) == {frozenset(c) for c in target_cells}:
            found = info
    assert found is not None, "expected infeasible refinement not found"
    assert found[poi[0]][nuis[0]] == 0 and found[nuis[0]][nuis[0]] == 0
    assert found[poi[0]][poi[0]] == Fraction(1191, 4096), found[poi[0]][poi[0]]
    out["CE-DS-DEGENERATE-GLOBAL-TIE-001"] = {
        "partitions": n_partitions,
        "feasible": len(values),
        "best": str(best),
        "tie_multiplicity": len(ties),
        "gap_to_next": str(best - next_best),
        "coincident_centroid_ties": coincident,
        "pseudo_inverse_value": str(found[poi[0]][poi[0]]),
    }
    # --- CE-DS-POP-WASTED-CELLS-001 ----------------------------------------
    fx = json.loads((WORKSPACE / "COUNTEREXAMPLES/CE-DS-POP-WASTED-CELLS-001.json").read_text())
    scores = [tuple(Fraction(x) for x in row) for row in fx["scores"]]
    weights = [Fraction(w) for w in fx["weights"]]
    poi, nuis = fx["poi_indices"], fx["nuisance_indices"]
    labels4 = fx["labels_before"]
    masses4, moments4 = binned_moments(scores, weights, labels4, 4)
    info4 = info_matrix(masses4, moments4)
    assert info4[nuis[0]][nuis[0]] == Fraction(9, 4)
    assert info4[poi[0]][nuis[0]] == 0
    val4 = profiled_value(info4, poi, nuis)
    assert val4 == Fraction(4), val4
    labels2 = [0 if s[poi[0]] < 0 else 1 for s in scores]
    masses2, moments2 = binned_moments(scores, weights, labels2, 2)
    info2 = info_matrix(masses2, moments2)
    assert info2[nuis[0]][nuis[0]] == 0, "K=2 coarsening nuisance block must be singular"
    assert info2[poi[0]][poi[0]] == Fraction(4)
    cents = projected_centroids(info4, masses4, moments4, poi, nuis)
    assert sorted(cents) == [Fraction(-2), Fraction(-2), Fraction(2), Fraction(2)], cents
    g, h = efficient_semimetric(info4, poi, nuis)
    mus = [[m / w for m in mom] for w, mom in zip(masses4, moments4)]
    violations = 0
    for i, s in enumerate(scores):
        a = labels4[i]
        ua = [s[j] - mus[a][j] for j in range(2)]
        s_aa = quad(ua, g, ua)
        for b in range(4):
            if b == a:
                continue
            ub = [s[j] - mus[b][j] for j in range(2)]
            if s_aa > quad(ub, g, ub):
                violations += 1
    assert violations == 0, violations
    out["CE-DS-POP-WASTED-CELLS-001"] = {
        "profiled_information_k4": str(val4),
        "nuisance_block_k4": str(info4[nuis[0]][nuis[0]]),
        "nuisance_block_k2": str(info2[nuis[0]][nuis[0]]),
        "first_order_violations_k4": violations,
        "projected_centroids_k4": [str(c) for c in sorted(cents)],
    }
    return out


# ----------------------------------------------------------------------------
# Mode: margins.
# ----------------------------------------------------------------------------


def run_margins(n=10, k=3, seeds=(1, 2, 3)):
    poi, nuis = [0], [1]
    results = []
    for seed in seeds:
        rng = Lcg(97 + seed)
        raw = [
            (Fraction(rng.next_int(-8, 8), 4), Fraction(rng.next_int(-8, 8), 4))
            for _ in range(n)
        ]
        mean = [sum(s[j] for s in raw) / n for j in range(2)]
        scores = [tuple(s[j] - mean[j] for j in range(2)) for s in raw]
        weights = [Fraction(1, n)] * n
        best = None
        best_labels = []
        for labels in canonical_labelings(n, k):
            masses, moments = binned_moments(scores, weights, labels, k)
            info = info_matrix(masses, moments)
            val = profiled_value(info, poi, nuis)
            if val is None or det(info) <= 0:
                continue
            if best is None or val > best:
                best, best_labels = val, [labels]
            elif val == best:
                best_labels.append(labels)
        assert best is not None
        labels = best_labels[0]
        masses, moments, info, det_i, det_l = state(scores, weights, labels, k, poi, nuis)
        assert is_exchange_stable(scores, weights, labels, k, poi, nuis, det_i, det_l), (
            "exact global optimum must be exchange-stable"
        )
        rep = leverage_report(scores, weights, labels, k, poi, nuis)
        counts = [labels.count(b) for b in range(k)]
        cents = projected_centroids(info, masses, moments, poi, nuis)
        seps = [abs(cents[i] - cents[j]) for i in range(k) for j in range(i + 1, k)]
        results.append(
            {
                "seed": seed,
                "global_value": str(best),
                "tie_multiplicity": len(best_labels),
                "cell_counts": counts,
                "has_singleton": min(counts) == 1,
                "min_projected_separation": str(min(seps)),
                "leverage": rep,
            }
        )
    return results


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    report = {}
    if mode in ("ds11", "all"):
        report["ds11"] = run_ds11()
    if mode in ("ds13", "all"):
        report["ds13"] = run_ds13()
    if mode in ("fixtures", "all"):
        report["fixtures"] = run_fixtures()
    if mode in ("margins", "all"):
        report["margins"] = run_margins()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
