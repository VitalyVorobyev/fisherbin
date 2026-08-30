"""Exact census of one-point exchange-stable profiled-Ds labelings.

DS-STABLE-MARGINS-COMPILE packet (OP29, deployment-facing half). DS15 settled
the margin behaviour of exact *global* finite Ds optima on the conditionally
centered class; the library's optimizer returns one-point exchange-stable,
generally non-global states, about which DS15 asserts nothing. This script
measures what those states look like: over full label lattices it classifies
every feasible labeling as exchange-stable or not in exact integer arithmetic,
and records the DS14 margin triple (M2 mass, M3 conditioning via the nuisance
block, M5 projected-centroid separation) together with the information price
v_K - Phi_s at every stable state.

Modes
-----
selftest     Cross-check the integer rank-two move algebra against from-scratch
             recomputation, the Fraction profiled value, and the independent
             audit-stack stability oracle (audit_ds_population_bridge).
census       Full-lattice stable-state census (default N=10..14, K=3,
             centered06 + mix3, 2 reps) with exact sandwich verification and
             DS13 spot checks at stable states.
ascent       Exact best-gain exchange ascent from the efficient-score interval
             seed and random seeds, on the census instances; records which
             stable state each seed reaches and its margins.
adversarial  Hardcoded tie/duplicate/unequal-weight/near-singular configs at
             N<=8, censused through the independent audit-stack oracle (and
             cross-checked against the integer path where weights are equal).
library      Seed-dependence at realistic N through the public scorequant API
             (float; requires the library environment): efficient-score DP
             seed vs k-means++ vs random, N in {100,300,1000}.
all          selftest + census + ascent + adversarial.

Everything claim-relevant runs in exact rational/integer arithmetic; floats
appear only in display columns and in the library mode. Weights are equal in
census/ascent (the DS15 class); adversarial covers unequal weights through the
Fraction path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_ds_margins_at_optima import (  # noqa: E402
    binned_blocks,
    canonical_labelings,
    center,
    efficient_scores,
    interval_optimum,
    partition_distance,
    profiled_value_d2,
    sample_law,
    tax_terms,
)
from audit_ds_population_bridge import (  # noqa: E402
    canonical_labelings as bridge_canonical_labelings,
)
from audit_ds_population_bridge import (  # noqa: E402
    is_exchange_stable,
    leverage_report,
    state as bridge_state,
)

WORKSPACE = Path(__file__).resolve().parents[1]
SEED_BASE = 20260830  # matches the audit exhaustive convention -> shared instances
MAX_STATE_ROWS = 20000  # per-instance cap on serialized compact stable-state rows
MAX_EXACT_SANDWICH = 20000  # per-instance cap on exact sandwich verifications
LEVERAGE_SAMPLE = 200  # DS13 leverage_report spot checks per instance


def provenance(mode, params):
    """Seeds/revision/environment record (protocols/numerical.md)."""
    script = Path(__file__)
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=script.parent,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        revision = "unknown"
    return {
        "mode": mode,
        "params": params,
        "git_revision": revision,
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }


# ----------------------------------------------------------------------------
# Integer normal-form lattice machinery (equal weights, d = 2, d_psi = 1).
#
# With centered rational rows scaled to integer coordinates c_i = (p_i, l_i)
# = D0 * s_i and PLCM = lcm(1..N), the binned information of a labeling with
# cell counts n_b and integer sums (P_b, L_b) is I = T / (N * D0^2 * PLCM)
# where T is the integer matrix
#     T = sum_b (PLCM / n_b) * (P_b, L_b)(P_b, L_b)^T .
# The profiled value is Phi = det I / I_11 = det T / (t11 * N * D0^2 * PLCM),
# so comparisons of Phi within one instance are integer cross-multiplications
# det T * t11' vs det T' * t11, and a one-point move only touches two cells of
# T. This is the exact rank-two relocation of D2/DS12 in integer form; the
# selftest pins it against from-scratch recomputation and the audit oracle.
# ----------------------------------------------------------------------------


def integer_normal_form(rows):
    """Scale exact-rational 2-d rows to integer coordinates; return (coords, D0)."""
    denom = 1
    for row in rows:
        for value in row:
            denom = denom * value.denominator // math.gcd(denom, value.denominator)
    coords = [(int(row[0] * denom), int(row[1] * denom)) for row in rows]
    return coords, denom


class Lattice:
    """Precomputed integer machinery for one equal-weight instance."""

    def __init__(self, rows, k):
        self.n = len(rows)
        self.k = k
        self.rows = rows
        self.weights = [Fraction(1, self.n)] * self.n
        self.coords, self.d0 = integer_normal_form(rows)
        self.plcm = math.lcm(*range(1, self.n + 1))
        self.mult = [0] + [self.plcm // c for c in range(1, self.n + 1)]
        # I (natural units) = T / self.scale.
        self.scale = self.n * self.d0 * self.d0 * self.plcm

    def cell_sums(self, labels):
        counts = [0] * self.k
        psum = [0] * self.k
        lsum = [0] * self.k
        for i, b in enumerate(labels):
            counts[b] += 1
            p, ell = self.coords[i]
            psum[b] += p
            lsum[b] += ell
        return counts, psum, lsum

    def t_entries(self, counts, psum, lsum):
        t00 = t01 = t11 = 0
        for c, p, ell in zip(counts, psum, lsum):
            m = self.mult[c]
            t00 += m * p * p
            t01 += m * p * ell
            t11 += m * ell * ell
        return t00, t01, t11

    def move_t(self, counts, psum, lsum, t00, t01, t11, i, a, b):
        """T entries after relocating point i from cell a to cell b."""
        p, ell = self.coords[i]
        ma, mb = self.mult[counts[a]], self.mult[counts[b]]
        ma2, mb2 = self.mult[counts[a] - 1], self.mult[counts[b] + 1]
        pa, la, pb, lb = psum[a], lsum[a], psum[b], lsum[b]
        pa2, la2, pb2, lb2 = pa - p, la - ell, pb + p, lb + ell
        t00n = t00 - ma * pa * pa - mb * pb * pb + ma2 * pa2 * pa2 + mb2 * pb2 * pb2
        t01n = t01 - ma * pa * la - mb * pb * lb + ma2 * pa2 * la2 + mb2 * pb2 * lb2
        t11n = t11 - ma * la * la - mb * lb * lb + ma2 * la2 * la2 + mb2 * lb2 * lb2
        return t00n, t01n, t11n

    def phi_fraction(self, t00, t01, t11):
        """Exact profiled value in natural units (None when I_11 singular)."""
        if t11 == 0:
            return None
        return Fraction(t00 * t11 - t01 * t01, t11 * self.scale)

    def has_improving_move(self, labels, counts, psum, lsum, t00, t01, t11, det_t):
        """Whether any admissible one-point move strictly raises Phi."""
        for i in range(self.n):
            a = labels[i]
            if counts[a] < 2:
                continue
            for b in range(self.k):
                if b == a:
                    continue
                t00n, t01n, t11n = self.move_t(counts, psum, lsum, t00, t01, t11, i, a, b)
                if t11n == 0:
                    continue  # infeasible destination state never improves
                det_n = t00n * t11n - t01n * t01n
                if det_n * t11 > det_t * t11n:
                    return True
        return False

    def best_move(self, labels, counts, psum, lsum, t00, t01, t11, det_t):
        """Best strictly improving move as (i, b) or None; ties by smallest (i, b)."""
        best = None
        best_det, best_t11 = det_t, t11
        for i in range(self.n):
            a = labels[i]
            if counts[a] < 2:
                continue
            for b in range(self.k):
                if b == a:
                    continue
                t00n, t01n, t11n = self.move_t(counts, psum, lsum, t00, t01, t11, i, a, b)
                if t11n == 0:
                    continue
                det_n = t00n * t11n - t01n * t01n
                if det_n * best_t11 > best_det * t11n:
                    best = (i, b)
                    best_det, best_t11 = det_n, t11n
        return best

    def max_residual_gain(self, labels, counts, psum, lsum, t00, t01, t11, det_t):
        """Exact max Phi' - Phi over admissible moves (<= 0 at a stable state)."""
        best = None
        for i in range(self.n):
            a = labels[i]
            if counts[a] < 2:
                continue
            for b in range(self.k):
                if b == a:
                    continue
                t00n, t01n, t11n = self.move_t(counts, psum, lsum, t00, t01, t11, i, a, b)
                if t11n == 0:
                    continue
                det_n = t00n * t11n - t01n * t01n
                gain = Fraction(det_n * t11 - det_t * t11n, t11n * t11 * self.scale)
                if best is None or gain > best:
                    best = gain
        return best

    def margin_row(self, labels, counts, psum, lsum, t00, t01, t11):
        """Exact margin quantities at one feasible labeling."""
        i00 = Fraction(t00, self.scale)
        i01 = Fraction(t01, self.scale)
        i11 = Fraction(t11, self.scale)
        det_i = i00 * i11 - i01 * i01
        trace = i00 + i11
        phi = det_i / i11
        # 2x2 PSD bounds: det/trace <= lambda_min <= min diagonal <= I_11.
        lam_lo = det_i / trace if trace > 0 else Fraction(0)
        lam_hi = min(i00, i11)
        min_count = min(counts)
        slope = i01 / i11
        centroids = [
            Fraction(p, c) / self.d0 - slope * Fraction(ell, c) / self.d0
            for c, p, ell in zip(counts, psum, lsum)
        ]
        sep = min(
            abs(centroids[x] - centroids[y])
            for x in range(self.k)
            for y in range(x + 1, self.k)
        )
        return {
            "phi": phi,
            "i11": i11,
            "det": det_i,
            "trace": trace,
            "lambda_min_lower": lam_lo,
            "lambda_min_upper": lam_hi,
            "min_count": min_count,
            "min_mass": Fraction(min_count, self.n),
            "proj_sep": sep,
        }


def canonical_form(labels):
    """First-occurrence canonical relabeling."""
    mapping = {}
    out = []
    for b in labels:
        if b not in mapping:
            mapping[b] = len(mapping)
        out.append(mapping[b])
    return out


def quantiles(values):
    if not values:
        return None
    ordered = sorted(values)

    def q(p):
        idx = min(len(ordered) - 1, max(0, round(p * (len(ordered) - 1))))
        return ordered[idx]

    return {
        "min": ordered[0],
        "q10": q(0.10),
        "q25": q(0.25),
        "median": q(0.50),
        "q75": q(0.75),
        "q90": q(0.90),
        "max": ordered[-1],
    }


# ----------------------------------------------------------------------------
# Mode: census.
# ----------------------------------------------------------------------------


def census_instance(law, n, rep, k=3):
    seed = SEED_BASE + 1000 * n + rep
    weights = [Fraction(1, n)] * n
    rows = center(sample_law(law, n, seed), weights)
    lattice = Lattice(rows, k)
    shat, bhat, _ = efficient_scores(rows, weights)
    v_k, interval_labels = interval_optimum(shat, weights, k)
    interval_canonical = canonical_form(interval_labels)

    start = time.time()
    n_feasible = 0
    n_singular = 0
    stable_records = []  # (labels, counts, psum, lsum, t00, t01, t11)
    best_det, best_t11 = None, None
    best_labels = None
    tie_count = 0

    for labels in canonical_labelings(n, k):
        counts, psum, lsum = lattice.cell_sums(labels)
        t00, t01, t11 = lattice.t_entries(counts, psum, lsum)
        if t11 == 0:
            n_singular += 1
            continue
        n_feasible += 1
        det_t = t00 * t11 - t01 * t01
        if best_det is None or det_t * best_t11 > best_det * t11:
            best_det, best_t11 = det_t, t11
            best_labels = list(labels)
            tie_count = 1
        elif det_t * best_t11 == best_det * t11:
            tie_count += 1
        if not lattice.has_improving_move(labels, counts, psum, lsum, t00, t01, t11, det_t):
            stable_records.append((list(labels), counts, psum, lsum, t00, t01, t11))
    scan_seconds = time.time() - start

    # The exact global optimum must be exchange-stable; cross-check it.
    gc, gp, gl = lattice.cell_sums(best_labels)
    gt00, gt01, gt11 = lattice.t_entries(gc, gp, gl)
    assert not lattice.has_improving_move(
        best_labels, gc, gp, gl, gt00, gt01, gt11, gt00 * gt11 - gt01 * gt01
    ), "global optimum not exchange-stable"
    global_phi = lattice.phi_fraction(gt00, gt01, gt11)
    # Independent Fraction cross-check of the integer objective path.
    _, _, info_best = binned_blocks(rows, weights, best_labels, k)
    assert profiled_value_d2(info_best) == global_phi

    # Per-stable-state exact records, sandwich verification, DS13 spot checks.
    rows_out = []
    gaps_rel = []
    i11s = []
    min_masses = []
    seps = []
    n_sandwich = 0
    n_leverage = 0
    witnesses = {}
    leverage_stride = max(1, len(stable_records) // LEVERAGE_SAMPLE)

    def witness_update(name, key, record, margin, keep_max):
        cur = witnesses.get(name)
        if cur is None or (key > cur["_key"]) == keep_max and key != cur["_key"]:
            witnesses[name] = {"_key": key, "record": record, "margin": margin}

    for idx, (labels, counts, psum, lsum, t00, t01, t11) in enumerate(stable_records):
        margin = lattice.margin_row(labels, counts, psum, lsum, t00, t01, t11)
        phi = margin["phi"]
        is_global = phi == global_phi
        gap = v_k - phi
        if idx < MAX_EXACT_SANDWICH:
            btw, cross, i11_tax = tax_terms(shat, rows, weights, labels, k)
            assert phi == btw - cross * cross / i11_tax, "projection-tax identity failed"
            assert btw <= v_k, "sandwich upper bound failed"
            assert i11_tax == margin["i11"]
            n_sandwich += 1
        if idx % leverage_stride == 0 and margin["det"] > 0:
            # DS13 assumes nonsingular I at the current state, so skip phi = 0
            # stable states (det I = 0), where the bound is not asserted.
            # leverage_report raises AssertionError on any DS13 violation.
            leverage_report(rows, weights, labels, k, [0], [1])
            n_leverage += 1
        dist = partition_distance(labels, interval_labels, k)
        row = {
            "labels": "".join(str(b) for b in labels),
            "phi": float(phi),
            "gap_rel": float(gap / v_k) if v_k else None,
            "i11": float(margin["i11"]),
            "lambda_min_lower": float(margin["lambda_min_lower"]),
            "min_mass": float(margin["min_mass"]),
            "min_count": margin["min_count"],
            "proj_sep": float(margin["proj_sep"]),
            "dist_to_interval": dist,
            "is_global": is_global,
        }
        rows_out.append(row)
        gaps_rel.append(row["gap_rel"])
        i11s.append(row["i11"])
        min_masses.append(row["min_mass"])
        seps.append(row["proj_sep"])
        exact_record = {
            "labels": list(labels),
            "phi": str(phi),
            "gap": str(gap),
            "i11": str(margin["i11"]),
            "det": str(margin["det"]),
            "min_mass": str(margin["min_mass"]),
            "proj_sep": str(margin["proj_sep"]),
            "dist_to_interval": dist,
            "is_global": is_global,
        }
        margin_key = {
            "i11": margin["i11"],
            "gap": gap,
            "phi": phi,
        }
        if not is_global:
            witness_update("stable_nonglobal_max_i11", margin_key["i11"], exact_record, margin, True)
            witness_update("stable_nonglobal_min_gap", margin_key["gap"], exact_record, margin, False)
        witness_update("stable_min_i11", margin_key["i11"], exact_record, margin, False)

    # Residual-gain certificate at the witnesses (exact max gain <= 0).
    for name, wit in witnesses.items():
        labels = wit["record"]["labels"]
        counts, psum, lsum = lattice.cell_sums(labels)
        t00, t01, t11 = lattice.t_entries(counts, psum, lsum)
        gain = lattice.max_residual_gain(
            labels, counts, psum, lsum, t00, t01, t11, t00 * t11 - t01 * t01
        )
        assert gain is None or gain <= 0
        wit["record"]["max_residual_gain"] = None if gain is None else str(gain)
        del wit["_key"]
        del wit["margin"]

    # Is the efficient-score DP interval labeling itself exchange-stable?
    ic, ip, il = lattice.cell_sums(interval_canonical)
    it00, it01, it11 = lattice.t_entries(ic, ip, il)
    if it11 == 0:
        interval_report = {"feasible": False, "stable": None}
    else:
        idet = it00 * it11 - it01 * it01
        i_stable = not lattice.has_improving_move(
            interval_canonical, ic, ip, il, it00, it01, it11, idet
        )
        i_margin = lattice.margin_row(interval_canonical, ic, ip, il, it00, it01, it11)
        i_gain = lattice.max_residual_gain(
            interval_canonical, ic, ip, il, it00, it01, it11, idet
        )
        interval_report = {
            "feasible": True,
            "stable": i_stable,
            "phi": str(i_margin["phi"]),
            "gap": str(v_k - i_margin["phi"]),
            "i11": str(i_margin["i11"]),
            "best_improving_gain": str(i_gain) if i_gain is not None and i_gain > 0 else None,
        }

    global_margin = lattice.margin_row(best_labels, gc, gp, gl, gt00, gt01, gt11)
    n_stable = len(stable_records)
    stable_nonglobal = sum(1 for row in rows_out if not row["is_global"])
    return {
        "law": law,
        "n": n,
        "rep": rep,
        "seed": seed,
        "k": k,
        "canonical_labelings": n_feasible + n_singular,
        "feasible": n_feasible,
        "singular": n_singular,
        "stable": n_stable,
        "stable_nonglobal": stable_nonglobal,
        "stable_fraction_of_feasible": n_stable / n_feasible if n_feasible else None,
        "exact_tie_multiplicity": tie_count,
        "global": {
            "labels": best_labels,
            "phi": str(global_phi),
            "gap": str(v_k - global_phi),
            "gap_rel": float((v_k - global_phi) / v_k) if v_k else None,
            "i11": str(global_margin["i11"]),
            "min_mass": str(global_margin["min_mass"]),
            "proj_sep": str(global_margin["proj_sep"]),
            "dist_to_interval": partition_distance(best_labels, interval_labels, k),
        },
        "interval_value_v_k": str(v_k),
        "slope_bhat": str(bhat),
        "interval_labeling": interval_report,
        "stable_quantiles": {
            "gap_rel": quantiles(gaps_rel),
            "i11": quantiles(i11s),
            "min_mass": quantiles(min_masses),
            "proj_sep": quantiles(seps),
        },
        "witnesses": witnesses,
        "stable_rows": rows_out[:MAX_STATE_ROWS],
        "stable_rows_truncated": len(rows_out) > MAX_STATE_ROWS,
        "exact_sandwich_verified": n_sandwich,
        "ds13_leverage_checked": n_leverage,
        "wall_seconds": round(scan_seconds, 1),
    }


def run_census(laws, sizes, reps):
    instances = []
    for law in laws:
        for n in sizes:
            for rep in range(1, reps + 1):
                instance = census_instance(law, n, rep)
                instances.append(instance)
                print(
                    f"[census] {law} N={n} rep={rep}: "
                    f"feasible={instance['feasible']} stable={instance['stable']} "
                    f"(nonglobal {instance['stable_nonglobal']}) "
                    f"interval_stable={instance['interval_labeling'].get('stable')} "
                    f"wall={instance['wall_seconds']}s",
                    flush=True,
                )
    return {
        "provenance": provenance("census", {"laws": laws, "sizes": sizes, "reps": reps}),
        "instances": instances,
    }


# ----------------------------------------------------------------------------
# Mode: ascent.
# ----------------------------------------------------------------------------


def exact_ascent(lattice, labels):
    """Exact best-gain exchange ascent; returns (terminal_labels, steps)."""
    labels = list(labels)
    steps = 0
    while True:
        counts, psum, lsum = lattice.cell_sums(labels)
        t00, t01, t11 = lattice.t_entries(counts, psum, lsum)
        if t11 == 0:
            raise ValueError("ascent entered an infeasible state")
        det_t = t00 * t11 - t01 * t01
        move = lattice.best_move(labels, counts, psum, lsum, t00, t01, t11, det_t)
        if move is None:
            return labels, steps
        labels[move[0]] = move[1]
        steps += 1


def random_surjective_labels(rng, n, k):
    while True:
        labels = [rng.next_int(0, k - 1) for _ in range(n)]
        if len(set(labels)) == k:
            return labels


def ascent_instance(law, n, rep, k=3, n_random=20):
    from audit_ds_margins_at_optima import Lcg

    seed = SEED_BASE + 1000 * n + rep
    weights = [Fraction(1, n)] * n
    rows = center(sample_law(law, n, seed), weights)
    lattice = Lattice(rows, k)
    shat, _, _ = efficient_scores(rows, weights)
    v_k, interval_labels = interval_optimum(shat, weights, k)

    def terminal_record(seed_kind, start_labels):
        terminal, steps = exact_ascent(lattice, start_labels)
        counts, psum, lsum = lattice.cell_sums(terminal)
        t00, t01, t11 = lattice.t_entries(counts, psum, lsum)
        margin = lattice.margin_row(terminal, counts, psum, lsum, t00, t01, t11)
        return {
            "seed_kind": seed_kind,
            "steps": steps,
            "labels": "".join(str(b) for b in canonical_form(terminal)),
            "phi": float(margin["phi"]),
            "gap_rel": float((v_k - margin["phi"]) / v_k) if v_k else None,
            "gap": str(v_k - margin["phi"]),
            "i11": float(margin["i11"]),
            "i11_exact": str(margin["i11"]),
            "min_mass": float(margin["min_mass"]),
            "proj_sep": float(margin["proj_sep"]),
        }

    records = [terminal_record("interval", canonical_form(interval_labels))]
    rng = Lcg(seed * 7919 + 13)
    for _ in range(n_random):
        records.append(terminal_record("random", random_surjective_labels(rng, n, k)))
    return {
        "law": law,
        "n": n,
        "rep": rep,
        "seed": seed,
        "interval_value_v_k": str(v_k),
        "terminals": records,
    }


def run_ascent(laws, sizes, reps, n_random=20):
    instances = []
    for law in laws:
        for n in sizes:
            for rep in range(1, reps + 1):
                instance = ascent_instance(law, n, rep, n_random=n_random)
                instances.append(instance)
                terminals = instance["terminals"]
                interval_terminal = terminals[0]
                random_i11 = [t["i11"] for t in terminals[1:]]
                print(
                    f"[ascent] {law} N={n} rep={rep}: interval-seed terminal "
                    f"gap_rel={interval_terminal['gap_rel']:.4f} "
                    f"i11={interval_terminal['i11']:.4f}; random-seed i11 "
                    f"min={min(random_i11):.4f} max={max(random_i11):.4f}",
                    flush=True,
                )
    return {
        "provenance": provenance(
            "ascent", {"laws": laws, "sizes": sizes, "reps": reps, "n_random": n_random}
        ),
        "instances": instances,
    }


# ----------------------------------------------------------------------------
# Mode: adversarial (N <= 8; Fraction path through the audit-stack oracle).
# ----------------------------------------------------------------------------

ADVERSARIAL_DATASETS = [
    {
        "name": "duplicate_atoms_equal_weights",
        "rows": [(2, 1), (2, 1), (-1, 2), (-1, -1), (-1, -1), (-1, -2)],
        "weights": ["1/6"] * 6,
    },
    {
        "name": "unequal_weights",
        "rows": [(3, 1), (1, -2), (-1, 2), (-2, -1), (0, 3), (-1, -3)],
        "weights": ["1/4", "1/8", "1/8", "1/8", "1/4", "1/8"],
    },
    {
        "name": "nuisance_symmetric_exact_ties",
        "rows": [(2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 3), (-2, -3), (2, 2), (2, -2)],
        "weights": ["1/8"] * 8,
    },
    {
        "name": "near_singular_nuisance",
        "rows": [
            (3, Fraction(1, 10000)),
            (1, Fraction(-2, 10000)),
            (-1, Fraction(2, 10000)),
            (-2, Fraction(-1, 10000)),
            (0, Fraction(3, 10000)),
            (-1, Fraction(-3, 10000)),
        ],
        "weights": ["1/6"] * 6,
    },
    {
        "name": "tiny_cell_pressure",
        "rows": [(4, 2), (-4, -2), (1, -1), (-1, 1), (2, -2), (-2, 2), (3, 3)],
        "weights": ["1/2", "1/12", "1/12", "1/12", "1/12", "1/12", "1/12"],
    },
]


def adversarial_dataset(config, k=3):
    weights = [Fraction(w) for w in config["weights"]]
    total = sum(weights)
    weights = [w / total for w in weights]
    rows = center([tuple(Fraction(v) for v in r) for r in config["rows"]], weights)
    n = len(rows)
    equal = len(set(weights)) == 1

    lattice = Lattice(rows, k) if equal else None
    n_feasible = 0
    n_singular = 0
    stable = []
    cross_checked = 0
    for labels in bridge_canonical_labelings(n, k):
        masses, moments, info, det_i, det_l = bridge_state(rows, weights, labels, k, [0], [1])
        if det_l == 0:
            n_singular += 1
            continue
        n_feasible += 1
        oracle = is_exchange_stable(rows, weights, labels, k, [0], [1], det_i, det_l)
        if equal:
            counts, psum, lsum = lattice.cell_sums(labels)
            t00, t01, t11 = lattice.t_entries(counts, psum, lsum)
            mine = not lattice.has_improving_move(
                list(labels), counts, psum, lsum, t00, t01, t11, t00 * t11 - t01 * t01
            )
            assert mine == oracle, f"stability disagreement on {config['name']} at {labels}"
            cross_checked += 1
        if oracle:
            i11 = info[1][1]
            phi = info[0][0] - info[0][1] * info[0][1] / i11
            slope = info[0][1] / i11
            centroids = [
                moments[b][0] / masses[b] - slope * moments[b][1] / masses[b] for b in range(k)
            ]
            sep = min(
                abs(centroids[x] - centroids[y]) for x in range(k) for y in range(x + 1, k)
            )
            if det_i > 0:
                # Raises AssertionError on any DS13 violation.
                leverage_report(rows, weights, labels, k, [0], [1])
            stable.append(
                {
                    "labels": "".join(str(b) for b in labels),
                    "phi": str(phi),
                    "i11": str(i11),
                    "min_mass": str(min(masses)),
                    "proj_sep": str(sep),
                }
            )
    shat, _, _ = efficient_scores(rows, weights)
    v_k, _ = interval_optimum(shat, weights, k)
    phis = [Fraction(s["phi"]) for s in stable]
    best_phi = max(phis)
    return {
        "name": config["name"],
        "n": n,
        "equal_weights": equal,
        "feasible": n_feasible,
        "singular": n_singular,
        "stable": len(stable),
        "integer_path_cross_checked": cross_checked,
        "interval_value_v_k": str(v_k),
        "global_phi": str(best_phi),
        "global_is_multiple": phis.count(best_phi) > 1,
        "stable_states": stable,
    }


def run_adversarial():
    reports = [adversarial_dataset(config) for config in ADVERSARIAL_DATASETS]
    for report in reports:
        print(
            f"[adversarial] {report['name']}: feasible={report['feasible']} "
            f"stable={report['stable']} cross_checked={report['integer_path_cross_checked']}",
            flush=True,
        )
    return {"provenance": provenance("adversarial", {}), "datasets": reports}


# ----------------------------------------------------------------------------
# Mode: selftest.
# ----------------------------------------------------------------------------


def run_selftest():
    from audit_ds_margins_at_optima import Lcg

    checked_moves = 0
    checked_states = 0
    for trial in range(4):
        rng = Lcg(9000 + trial)
        n, k = (6, 3) if trial % 2 == 0 else (7, 3)
        raw = [
            (Fraction(rng.next_int(-8, 8), 4), Fraction(rng.next_int(-8, 8), 4))
            for _ in range(n)
        ]
        weights = [Fraction(1, n)] * n
        rows = center(raw, weights)
        lattice = Lattice(rows, k)
        for labels in canonical_labelings(n, k):
            counts, psum, lsum = lattice.cell_sums(labels)
            t00, t01, t11 = lattice.t_entries(counts, psum, lsum)
            # Integer objective path vs the independent Fraction path.
            phi_int = lattice.phi_fraction(t00, t01, t11)
            try:
                _, _, info = binned_blocks(rows, weights, labels, k)
                phi_frac = profiled_value_d2(info)
            except ValueError:
                phi_frac = None
            assert phi_int == phi_frac
            if t11 == 0:
                continue
            det_t = t00 * t11 - t01 * t01
            # Delta move update vs from-scratch recomputation, all moves.
            for i in range(n):
                a = labels[i]
                if counts[a] < 2:
                    continue
                for b in range(k):
                    if b == a:
                        continue
                    moved = list(labels)
                    moved[i] = b
                    mc, mp, ml = lattice.cell_sums(moved)
                    expected = lattice.t_entries(mc, mp, ml)
                    got = lattice.move_t(counts, psum, lsum, t00, t01, t11, i, a, b)
                    assert got == expected
                    checked_moves += 1
            # Stability verdict vs the independent audit-stack oracle.
            _, _, _, det_i, det_l = bridge_state(rows, weights, labels, k, [0], [1])
            oracle = is_exchange_stable(rows, weights, labels, k, [0], [1], det_i, det_l)
            mine = not lattice.has_improving_move(
                list(labels), counts, psum, lsum, t00, t01, t11, det_t
            )
            assert mine == oracle
            checked_states += 1
    print(f"[selftest] PASS: {checked_states} states, {checked_moves} move updates", flush=True)
    return {"states": checked_states, "moves": checked_moves, "result": "PASS"}


# ----------------------------------------------------------------------------
# Mode: library (E2 seed dependence; requires numpy + scorequant).
# ----------------------------------------------------------------------------


def library_margins(scores, labels, k):
    import numpy as np

    n = scores.shape[0]
    info = np.zeros((2, 2))
    masses = []
    centroids = []
    for b in range(k):
        mask = labels == b
        w_b = mask.sum() / n
        masses.append(w_b)
        m_b = scores[mask].sum(axis=0) / n
        info += np.outer(m_b, m_b) / w_b
        centroids.append(m_b / w_b)
    eigs = np.linalg.eigvalsh(info)
    slope = info[0, 1] / info[1, 1] if info[1, 1] > 0 else float("nan")
    proj = [c[0] - slope * c[1] for c in centroids]
    sep = min(abs(proj[x] - proj[y]) for x in range(k) for y in range(x + 1, k))
    return {
        "min_mass": float(min(masses)),
        "i11": float(info[1, 1]),
        "lambda_min": float(eigs[0]),
        "proj_sep": float(sep),
    }


def run_library(sizes=(100, 300, 1000), reps=3, k=3):
    import numpy as np

    from scorequant import (
        DExchangeConfig,
        ProfiledDOptimality,
        efficient_score_bound,
        optimize_partition,
    )

    runs = []
    for law in ("gauss06", "mix3"):
        for n in sizes:
            for rep in range(1, reps + 1):
                seed = SEED_BASE + 100000 + 1000 * n + rep
                rng = np.random.default_rng(seed)
                if law == "gauss06":
                    cov = np.array([[1.0, 0.6], [0.6, 1.0]])
                    scores = rng.multivariate_normal([0.0, 0.0], cov, size=n)
                else:
                    comp = rng.integers(0, 3, size=n)
                    mus = np.array([[-2.0, 1.0], [0.0, -2.0], [2.0, 1.0]])
                    scores = mus[comp] + rng.normal(size=(n, 2)) / 2.0
                scores = scores - scores.mean(axis=0)  # DS15 empirical centering
                bound = efficient_score_bound(scores, interest=(0,), n_bins=k)
                seedings = {
                    "efficient": {"initial_labels": np.asarray(bound.labels)},
                    "kmeans": {"config": DExchangeConfig(seed=seed, solver_restarts=1)},
                    "random": {
                        "config": DExchangeConfig(seed=seed, solver_restarts=1, init="random")
                    },
                }
                for seed_kind, kwargs in seedings.items():
                    config = kwargs.pop("config", DExchangeConfig(seed=seed, solver_restarts=1))
                    result = optimize_partition(
                        scores,
                        n_bins=k,
                        criterion=ProfiledDOptimality(interest=(0,)),
                        config=config,
                        **kwargs,
                    )
                    margins = library_margins(scores, np.asarray(result.labels), k)
                    runs.append(
                        {
                            "law": law,
                            "n": n,
                            "rep": rep,
                            "seed": seed,
                            "seed_kind": seed_kind,
                            "objective_log": float(result.objective),
                            "upper_bound_log": float(bound.upper_bound),
                            "gap_log": float(bound.upper_bound - result.objective),
                            "exchange_stable": bool(result.exchange_stable),
                            **margins,
                        }
                    )
                    print(
                        f"[library] {law} N={n} rep={rep} {seed_kind}: "
                        f"gap_log={runs[-1]['gap_log']:.5f} "
                        f"i11={margins['i11']:.4f} lam_min={margins['lambda_min']:.5f} "
                        f"min_mass={margins['min_mass']:.3f} "
                        f"stable={runs[-1]['exchange_stable']}",
                        flush=True,
                    )
    return {
        "provenance": provenance("library", {"sizes": sizes, "reps": reps}),
        "runs": runs,
    }


# ----------------------------------------------------------------------------
# CLI.
# ----------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "mode",
        choices=["selftest", "census", "ascent", "adversarial", "library", "all"],
        nargs="?",
        default="all",
    )
    parser.add_argument("--laws", default="centered06,mix3")
    parser.add_argument("--sizes", default="10,11,12,13,14")
    parser.add_argument("--reps", type=int, default=2)
    parser.add_argument("--library-sizes", default="100,300,1000")
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    laws = args.laws.split(",")
    sizes = [int(s) for s in args.sizes.split(",")]
    report = {}
    if args.mode in ("selftest", "all"):
        report["selftest"] = run_selftest()
    if args.mode in ("census", "all"):
        report["census"] = run_census(laws, sizes, args.reps)
    if args.mode in ("ascent", "all"):
        report["ascent"] = run_ascent(laws, sizes, args.reps)
    if args.mode in ("adversarial", "all"):
        report["adversarial"] = run_adversarial()
    if args.mode == "library":
        library_sizes = tuple(int(s) for s in args.library_sizes.split(","))
        report["library"] = run_library(sizes=library_sizes, reps=args.reps)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=1))
        print(f"wrote {out_path}", flush=True)
    else:
        summary = {
            key: (len(value.get("instances", value.get("datasets", value.get("runs", []))))
                  if isinstance(value, dict) else value)
            for key, value in report.items()
        }
        print(json.dumps(summary, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
