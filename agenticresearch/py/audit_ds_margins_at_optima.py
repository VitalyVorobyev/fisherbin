"""Independent adversarial falsification suite for the DS15 margins audit.

Audits OPEN-DS-MARGINS-AT-OPTIMA (packet AUDIT-DS-MARGINS-AT-OPTIMA) with
pure-stdlib exact rational arithmetic: no numpy, no floats on claim-relevant
quantities, and no shared code with the researcher's py/ds_margins_at_optima.py
or py/ds_population_bridge.py. Every quantity that decides a claim is a
fractions.Fraction; floats appear only inside the deliberate re-implementation
of the researcher's float screen, whose reliability is itself under audit.

Modes (run as: uv run python agenticresearch/py/audit_ds_margins_at_optima.py <mode> [--out PATH]):

  identities  Proposition 4 attack: the exact projection-tax identity
              Phi(z) = btw(shat; z) - c(z)^2 / I11(z), the sandwich
              btw <= v_K_hat, 1-D contiguity of the scalar optimum over the
              FULL partition lattice, and the singular-nuisance boundary
              (pseudo-inverse branch Phi^+ = btw exactly), on adversarial
              datasets: duplicate atoms, singletons, exact shat ties from a
              nuisance-symmetric law, unequal weights, plus deterministic
              LCG instances.
  vacuity     The K = d_lambda + 1 rank boundary: with exactly centered
              scores rank(I_z) <= K-1, so when K = d_lambda + 1 EVERY
              feasible labeling has profiled value exactly 0 while the
              efficient-score interval optimum is positive - conclusion (i)
              of DS15 fails for d_lambda >= 2 under the recorded "K >= 3"
              assumption. Verifies the minimized N=4 witness (the
              CE-DS-MARGINS-RANK-VACUITY-001 fixture) and random instances,
              and shows K = d_lambda + 2 restores positivity on the same
              data.
  exhaustive  Independent fully exact global optima at N=12 and N=13
              (K=3, d=2, no float screen, no top-k cut; own CLT-rational
              law emulation, own LCG seeds): full-lattice exact tie census,
              min cell mass / singleton census, nuisance block and
              projection tax at the optimum, the exact sandwich, the value
              gap to the best efficient-score interval labeling, and a
              faithful re-implementation of the researcher's float top-64
              screen (FLOAT_GUARD included) diffed against the exhaustive
              truth: float rank of the exact optimum and guard casualties.
  scalar      Exact-rational weighted interval DP at N=1000 anchoring the
              float-only N-DS-SCALAR-MASS evidence: exact optimal K=3
              interval partition of a CLT-rational Gaussian emulation,
              minimum cell mass versus the population value, and agreement
              with the library's float scalar_interval_dp on the same data.
  all         every mode in sequence.

Every mode's report embeds seeds, git revision, script hash, and environment
(protocols/numerical.md storage rule). Exit is nonzero on any violated
claim-relevant identity or bound.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import platform
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
FLOAT_GUARD = 1e-9  # the researcher's screen guard, reproduced for the probe
TOP_KEEP_CANONICAL = 11  # ceil(64 labeled / 3! labelings per canonical class)

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


def clt_rational(rng, denom=1024):
    """Approximately standard-normal exact rational: sum of 12 grid uniforms."""
    total = sum(rng.next_int(0, denom - 1) for _ in range(12))
    return Fraction(total, denom) - 6


def sample_law(law, n, seed):
    """Exact-rational samples emulating the researcher's law families.

    centered06:  jointly (approximately) Gaussian with exact correlation 3/5
                 via the rational rotation (3/5, 4/5) - in DS15's class (L).
    mix3:        3-component location mixture - conditional centering fails.
    """
    rng = Lcg(seed)
    rows = []
    for _ in range(n):
        z1 = clt_rational(rng)
        z2 = clt_rational(rng)
        if law == "centered06":
            rows.append((z1, Fraction(3, 5) * z1 + Fraction(4, 5) * z2))
        elif law == "mix3":
            comp = rng.next_int(0, 2)
            mu = [(-2, 1), (0, -2), (2, 1)][comp]
            rows.append(
                (
                    Fraction(mu[0]) + z1 / 2,
                    Fraction(mu[1]) + z2 / 2,
                )
            )
        else:
            raise ValueError(f"unknown law {law}")
    return rows


def center(rows, weights):
    """Exact weighted centering (the chapter's empirical convention)."""
    total = sum(weights)
    d = len(rows[0])
    mean = [sum(w * r[j] for w, r in zip(weights, rows)) / total for j in range(d)]
    return [tuple(r[j] - mean[j] for j in range(d)) for r in rows]


# ----------------------------------------------------------------------------
# Exact profiled-Ds machinery (d_psi = 1 throughout; d_lambda = 1 or 2).
# ----------------------------------------------------------------------------


def binned_sums(values, weights, labels, k):
    """Per-cell (W_b, sum_b w*x) for a scalar column; cells must be nonempty."""
    masses = [Fraction(0)] * k
    sums = [Fraction(0)] * k
    for x, w, b in zip(values, weights, labels):
        masses[b] += w
        sums[b] += w * x
    if any(m == 0 for m in masses):
        raise ValueError("empty cell")
    return masses, sums


def between_value(values, weights, labels, k):
    masses, sums = binned_sums(values, weights, labels, k)
    return sum(s * s / m for s, m in zip(sums, masses))


def full_second_moment(rows, weights):
    d = len(rows[0])
    total = sum(weights)
    return [
        [sum(w * r[i] * r[j] for w, r in zip(weights, rows)) / total for j in range(d)]
        for i in range(d)
    ]


def efficient_scores(rows, weights):
    """shat_i = s_psi,i - Bhat s_lam,i with the full-sample regression slope.

    d_lambda = 1 only. Returns (shat list, Bhat, sigma2 = weighted E shat^2).
    """
    info = full_second_moment(rows, weights)
    if info[1][1] == 0:
        raise ValueError("degenerate nuisance coordinate")
    bhat = info[0][1] / info[1][1]
    total = sum(weights)
    shat = [r[0] - bhat * r[1] for r in rows]
    sigma2 = sum(w * s * s for w, s in zip(weights, shat)) / total
    # Exact empirical normal equation: sum w shat_i s_lam_i == 0.
    assert sum(w * s * r[1] for w, s, r in zip(weights, shat, rows)) == 0
    return shat, bhat, sigma2


def binned_blocks(rows, weights, labels, k):
    """Binned information blocks (I00, I01 vector, I11 matrix) for d_psi=1."""
    d = len(rows[0])
    masses = [Fraction(0)] * k
    moments = [[Fraction(0)] * d for _ in range(k)]
    for r, w, b in zip(rows, weights, labels):
        masses[b] += w
        for j in range(d):
            moments[b][j] += w * r[j]
    if any(m == 0 for m in masses):
        raise ValueError("empty cell")
    info = [[Fraction(0)] * d for _ in range(d)]
    for wb, mb in zip(masses, moments):
        for i in range(d):
            for j in range(d):
                info[i][j] += mb[i] * mb[j] / wb
    return masses, moments, info


def profiled_value_d2(info):
    """I00 - I01^2/I11 for d=2; None when the nuisance block is singular."""
    if info[1][1] == 0:
        return None
    return info[0][0] - info[0][1] * info[0][1] / info[1][1]


def profiled_value_d3(info):
    """Schur value for d=3, nuisance block 2x2; None when singular."""
    a, b, c = info[1][1], info[1][2], info[2][2]
    det_l = a * c - b * b
    if det_l == 0:
        return None
    p, q = info[0][1], info[0][2]
    # I01 I11^{-1} I10 with the 2x2 adjugate.
    return info[0][0] - (p * (c * p - b * q) + q * (a * q - b * p)) / det_l


def tax_terms(shat, rows, weights, labels, k):
    """(btw(shat; z), c(z), I11(z)) for d_lambda = 1."""
    masses, s_sums = binned_sums(shat, weights, labels, k)
    lam = [r[1] for r in rows]
    _, l_sums = binned_sums(lam, weights, labels, k)
    btw = sum(s * s / m for s, m in zip(s_sums, masses))
    cross = sum(s * ell / m for s, ell, m in zip(s_sums, l_sums, masses))
    i11 = sum(ell * ell / m for ell, m in zip(l_sums, masses))
    return btw, cross, i11


def interval_optimum(values, weights, k):
    """Exact optimal K-grouping between-value over CONTIGUOUS sorted intervals.

    Ties in the values are kept index-adjacent by the stable sort, so the
    contiguity claim tested against the full lattice covers duplicate atoms.
    Returns (best between-value, labels aligned with the input order).
    """
    n = len(values)
    order = sorted(range(n), key=lambda i: values[i])
    best = None
    best_cuts = None
    for cuts in itertools.combinations(range(1, n), k - 1):
        bounds = (0, *cuts, n)
        total = Fraction(0)
        ok = True
        for a, b in zip(bounds, bounds[1:]):
            mass = sum(weights[order[i]] for i in range(a, b))
            if mass == 0:
                ok = False
                break
            sub = sum(weights[order[i]] * values[order[i]] for i in range(a, b))
            total += sub * sub / mass
        if ok and (best is None or total > best):
            best, best_cuts = total, bounds
    labels = [0] * n
    for cell, (a, b) in enumerate(zip(best_cuts, best_cuts[1:])):
        for i in range(a, b):
            labels[order[i]] = cell
    return best, labels


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


def partition_distance(a, b, k):
    """Minimum relabeling disagreements between two labelings."""
    best = None
    for perm in itertools.permutations(range(k)):
        diff = sum(1 for x, y in zip(a, b) if perm[x] != y)
        if best is None or diff < best:
            best = diff
    return best


# ----------------------------------------------------------------------------
# Provenance metadata (protocols/numerical.md: seeds, revision, environment).
# ----------------------------------------------------------------------------


def provenance(mode, params):
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
# Mode: identities.
# ----------------------------------------------------------------------------

IDENTITY_DATASETS = [
    {
        # Duplicate atoms and a forced singleton-friendly layout.
        "name": "duplicates-equal-weights",
        "rows": [(2, 1), (2, 1), (-1, 2), (0, -3), (-1, -1), (-2, 0)],
        "weights": ["1/6"] * 6,
    },
    {
        # Same atoms, unequal positive weights (algebra-only regime: DS15
        # itself assumes equal weights; Proposition 4 is weight-agnostic).
        "name": "duplicates-unequal-weights",
        "rows": [(2, 1), (2, 1), (-1, 2), (0, -3), (-1, -1), (-2, 0)],
        "weights": ["1/4", "1/8", "1/8", "1/8", "1/4", "1/8"],
    },
    {
        # Nuisance-symmetric: Bhat = 0 exactly, so shat = s_psi carries
        # exact duplicate values - the tie attack on the contiguity step.
        "name": "shat-exact-ties",
        "rows": [(1, 1), (1, -1), (-1, 2), (-1, -2), (0, 3), (0, -3)],
        "weights": ["1/6"] * 6,
    },
]


def run_identities(k=3, lcg_instances=5, lcg_n=8):
    datasets = []
    for ds in IDENTITY_DATASETS:
        rows = [tuple(Fraction(x) for x in r) for r in ds["rows"]]
        weights = [Fraction(w) for w in ds["weights"]]
        datasets.append((ds["name"], rows, weights))
    for rep in range(lcg_instances):
        rng = Lcg(20260830 + rep)
        rows = [
            (Fraction(rng.next_int(-8, 8), 4), Fraction(rng.next_int(-8, 8), 4))
            for _ in range(lcg_n)
        ]
        datasets.append((f"lcg-{rep}", rows, [Fraction(1, lcg_n)] * lcg_n))

    results = []
    for name, raw_rows, weights in datasets:
        rows = center(raw_rows, weights)
        shat, bhat, _ = efficient_scores(rows, weights)
        v_k, _ = interval_optimum(shat, weights, k)
        n_feasible = n_singular = 0
        lattice_btw_max = None
        for labels in canonical_labelings(len(rows), k):
            _, _, info = binned_blocks(rows, weights, labels, k)
            btw, cross, i11 = tax_terms(shat, rows, weights, labels, k)
            phi = profiled_value_d2(info)
            if phi is None:
                # Singular nuisance block: PSD forces the cross moment to 0,
                # and the DS11 pseudo-inverse value collapses to btw exactly.
                n_singular += 1
                assert info[0][1] == 0, (name, labels)
                assert cross == 0, (name, labels)
                assert info[0][0] == btw, (name, labels)
            else:
                n_feasible += 1
                assert i11 == info[1][1], (name, labels)
                assert phi == btw - cross * cross / i11, (name, labels)
                assert phi <= btw, (name, labels)
            assert btw <= v_k, (name, labels, str(btw), str(v_k))
            if lattice_btw_max is None or btw > lattice_btw_max:
                lattice_btw_max = btw
        # 1-D contiguity: the full-lattice between optimum is attained by a
        # contiguous grouping of the (stably) sorted shat values.
        assert lattice_btw_max == v_k, (name, str(lattice_btw_max), str(v_k))
        results.append(
            {
                "dataset": name,
                "n": len(rows),
                "bhat": str(bhat),
                "feasible_labelings": n_feasible,
                "singular_labelings": n_singular,
                "interval_optimum": str(v_k),
                "identity_violations": 0,
                "contiguity_confirmed": True,
            }
        )
    return {"provenance": provenance("identities", {"k": k, "lcg_seed_base": 20260830}), "datasets": results}


# ----------------------------------------------------------------------------
# Mode: vacuity.
# ----------------------------------------------------------------------------

# Minimized witness: N=4, d=3 (d_psi=1, d_lambda=2), integer scores with exact
# zero column sums, nonsingular full information. Serialized as
# COUNTEREXAMPLES/CE-DS-MARGINS-RANK-VACUITY-001.json.
VACUITY_WITNESS_ROWS = [(3, 1, 0), (-1, -2, 1), (-1, 1, -2), (-1, 0, 1)]


def vacuity_scan(rows, weights, k):
    """Enumerate all canonical labelings; return (feasible values, singular)."""
    feasible = []
    singular = 0
    for labels in canonical_labelings(len(rows), k):
        _, _, info = binned_blocks(rows, weights, labels, k)
        phi = profiled_value_d3(info)
        if phi is None:
            singular += 1
        else:
            feasible.append((phi, labels))
    return feasible, singular


def run_vacuity():
    n = len(VACUITY_WITNESS_ROWS)
    rows = [tuple(Fraction(x) for x in r) for r in VACUITY_WITNESS_ROWS]
    weights = [Fraction(1, n)] * n
    assert all(sum(r[j] for r in rows) == 0 for j in range(3)), "witness not centered"
    full = full_second_moment(rows, weights)
    det_full = (
        full[0][0] * (full[1][1] * full[2][2] - full[1][2] * full[2][1])
        - full[0][1] * (full[1][0] * full[2][2] - full[1][2] * full[2][0])
        + full[0][2] * (full[1][0] * full[2][1] - full[1][1] * full[2][0])
    )
    assert det_full > 0, "witness full information must be nonsingular"
    # The scalar efficient-score problem is nondegenerate: the projected
    # interval optimum (the DS15 upper object) is strictly positive.
    det_l = full[1][1] * full[2][2] - full[1][2] * full[2][1]
    assert det_l > 0
    b1 = (full[0][1] * full[2][2] - full[0][2] * full[1][2]) / det_l
    b2 = (full[0][2] * full[1][1] - full[0][1] * full[2][1]) / det_l
    shat = [r[0] - b1 * r[1] - b2 * r[2] for r in rows]
    v_k, _ = interval_optimum(shat, weights, 3)
    assert v_k > 0, "witness efficient-score interval optimum must be positive"

    # K = d_lambda + 1 = 3: every feasible labeling has profiled value 0.
    feasible, singular = vacuity_scan(rows, weights, 3)
    assert feasible, "witness must admit a feasible labeling"
    assert all(phi == 0 for phi, _ in feasible), "rank vacuity violated"

    # K = d_lambda + 2 = 4 on the same data (all singletons): the profiled
    # value is positive - the vacuity is a pure cardinality boundary.
    _, _, info4 = binned_blocks(rows, weights, [0, 1, 2, 3], 4)
    phi4 = profiled_value_d3(info4)
    assert phi4 is not None and phi4 > 0, "K = d_lambda + 2 must restore positivity"

    # Random confirmation at N=6..8: same vacuity on LCG instances.
    random_checks = []
    for rep, n_r in enumerate((6, 7, 8)):
        rng = Lcg(4200 + rep)
        raw = [
            tuple(Fraction(rng.next_int(-8, 8), 4) for _ in range(3)) for _ in range(n_r)
        ]
        w_r = [Fraction(1, n_r)] * n_r
        rows_r = center(raw, w_r)
        feas_r, sing_r = vacuity_scan(rows_r, w_r, 3)
        assert all(phi == 0 for phi, _ in feas_r), f"rank vacuity violated at N={n_r}"
        random_checks.append(
            {"n": n_r, "feasible": len(feas_r), "singular": sing_r, "all_zero": True}
        )
    return {
        "provenance": provenance("vacuity", {"witness_rows": VACUITY_WITNESS_ROWS}),
        "witness": {
            "n": n,
            "k": 3,
            "feasible_labelings": len(feasible),
            "singular_labelings": singular,
            "all_feasible_profiled_values_zero": True,
            "interval_optimum_v_k": str(v_k),
            "k4_all_singletons_profiled_value": str(phi4),
        },
        "random_checks": random_checks,
    }


# ----------------------------------------------------------------------------
# Mode: exhaustive.
# ----------------------------------------------------------------------------


def exhaustive_instance(law, n, rep, k=3):
    seed = 20260830 + 1000 * n + rep
    weights = [Fraction(1, n)] * n
    rows = center(sample_law(law, n, seed), weights)
    shat, bhat, _ = efficient_scores(rows, weights)
    v_k, interval_labels = interval_optimum(shat, weights, k)

    # Integer normal forms for the enumeration hot loop.
    def numerators(values):
        denom = 1
        for v in values:
            denom = denom * v.denominator // math.gcd(denom, v.denominator)
        return [int(v * denom) for v in values], denom

    p_num, _ = numerators([r[0] for r in rows])
    l_num, l_den = numerators([r[1] for r in rows])
    s_num, _ = numerators(shat)
    # The researcher's FLOAT_GUARD acts on the natural-units nuisance block
    # I11 = A11 / (N * l_den^2); reproduce that exact semantics.
    guard_scale = float(n) * float(l_den) ** 2

    start = time.time()
    best_phi = None
    best_labels = None
    tie_count = 0
    btw_max = None
    n_feasible = 0
    n_singular = 0
    guard_casualties = 0
    guard_casualty_best = None
    float_values = []  # guarded float profiled values, aligned with labelings
    best_index = None

    for idx, labels in enumerate(canonical_labelings(n, k)):
        counts = [0] * k
        up = [0] * k
        ul = [0] * k
        us = [0] * k
        for i, b in enumerate(labels):
            counts[b] += 1
            up[b] += p_num[i]
            ul[b] += l_num[i]
            us[b] += s_num[i]
        a00 = sum(Fraction(u * u, c) for u, c in zip(up, counts))
        a01 = sum(Fraction(u * v, c) for u, v, c in zip(up, ul, counts))
        a11 = sum(Fraction(v * v, c) for v, c in zip(ul, counts))
        btw_scaled = sum(Fraction(u * u, c) for u, c in zip(us, counts))
        if btw_max is None or btw_scaled > btw_max:
            btw_max = btw_scaled
        if a11 == 0:
            n_singular += 1
            float_values.append(None)
            continue
        n_feasible += 1
        phi_scaled = a00 - a01 * a01 / a11
        # Float screen re-implementation (researcher semantics): guard on the
        # float natural-units nuisance block, rank by the float profiled value.
        f11 = float(a11) / guard_scale
        if f11 <= FLOAT_GUARD:
            guard_casualties += 1
            if guard_casualty_best is None or phi_scaled > guard_casualty_best:
                guard_casualty_best = phi_scaled
            float_values.append(None)
        else:
            float_values.append(float(a00) - float(a01) ** 2 / float(a11))
        if best_phi is None or phi_scaled > best_phi:
            best_phi = phi_scaled
            best_labels = list(labels)
            best_index = idx
            tie_count = 1
        elif phi_scaled == best_phi:
            tie_count += 1
    elapsed = time.time() - start

    # Convert the scaled optimum back to natural units and cross-check the
    # sandwich with the independent Fraction path.
    _, _, info = binned_blocks(rows, weights, best_labels, k)
    phi_best = profiled_value_d2(info)
    btw_best, cross_best, i11_best = tax_terms(shat, rows, weights, best_labels, k)
    assert phi_best == btw_best - cross_best * cross_best / i11_best
    assert btw_best <= v_k
    # Full-lattice contiguity: the between optimum over ALL labelings equals
    # the best contiguous interval labeling, compared in the same scaled units.
    us_int = [0] * k
    counts_int = [0] * k
    for i, b in enumerate(interval_labels):
        counts_int[b] += 1
        us_int[b] += s_num[i]
    interval_scaled = sum(Fraction(u * u, c) for u, c in zip(us_int, counts_int))
    assert btw_max == interval_scaled, "full-lattice between optimum not contiguous"

    # Float-screen diagnostics against the exhaustive truth.
    f_best = float_values[best_index]
    if f_best is None:
        float_rank = None
        screened_finds_optimum = False
    else:
        float_rank = 1 + sum(1 for v in float_values if v is not None and v > f_best)
        screened_finds_optimum = float_rank <= TOP_KEEP_CANONICAL
    counts_best = [best_labels.count(b) for b in range(k)]
    min_mass = Fraction(min(counts_best), n)
    guard_gap = (
        None
        if guard_casualty_best is None or best_phi == 0
        else str(guard_casualty_best / best_phi)
    )
    return {
        "law": law,
        "n": n,
        "rep": rep,
        "seed": seed,
        "canonical_labelings": n_feasible + n_singular,
        "feasible": n_feasible,
        "singular": n_singular,
        "exact_tie_multiplicity": tie_count,
        "min_cell_mass": str(min_mass),
        "has_singleton": min(counts_best) == 1,
        "optimum_value": str(phi_best),
        "optimum_i11": str(i11_best),
        "optimum_abs_cross": str(abs(cross_best)),
        "optimum_tax": str(cross_best * cross_best / i11_best),
        "interval_value_v_k": str(v_k),
        "value_gap": str(v_k - phi_best),
        "relative_value_gap": str((v_k - phi_best) / v_k) if v_k else None,
        "swap_distance_to_interval": partition_distance(best_labels, interval_labels, k),
        "sandwich_exact": True,
        "lattice_contiguity": True,
        "float_rank_of_exact_optimum": float_rank,
        "top64_labeled_screen_finds_optimum": screened_finds_optimum,
        "guard_casualties": guard_casualties,
        "best_guard_casualty_over_optimum": guard_gap,
        "wall_seconds": round(elapsed, 1),
    }


def run_exhaustive(sizes=(12, 13), laws=("centered06", "mix3"), reps=2):
    instances = []
    for law in laws:
        for n in sizes:
            for rep in range(reps):
                instances.append(exhaustive_instance(law, n, rep))
    return {
        "provenance": provenance(
            "exhaustive",
            {"sizes": list(sizes), "laws": list(laws), "reps": reps, "seed_formula": "20260830 + 1000*n + rep"},
        ),
        "instances": instances,
    }


# ----------------------------------------------------------------------------
# Mode: scalar.
# ----------------------------------------------------------------------------


def exact_interval_dp(values, k):
    """Exact equal-weight 1-D K-interval SSE minimization via DP.

    Returns (min within-SSE, cut boundaries) over sorted values, all Fractions.
    """
    xs = sorted(values)
    n = len(xs)
    denom = 1
    for v in xs:
        denom = denom * v.denominator // __import__("math").gcd(denom, v.denominator)
    ints = [int(v * denom) for v in xs]
    pre1 = [0] * (n + 1)
    pre2 = [0] * (n + 1)
    for i, v in enumerate(ints):
        pre1[i + 1] = pre1[i] + v
        pre2[i + 1] = pre2[i] + v * v

    def seg_cost(a, b):
        cnt = b - a
        s1 = pre1[b] - pre1[a]
        s2 = pre2[b] - pre2[a]
        return Fraction(s2 * cnt - s1 * s1, cnt)  # scaled by cnt*denom^2*n... constant

    dp = [[None] * (n + 1) for _ in range(k + 1)]
    arg = [[None] * (n + 1) for _ in range(k + 1)]
    dp[0][0] = Fraction(0)
    for kk in range(1, k + 1):
        for j in range(kk, n - (k - kk) + 1):
            best = None
            best_i = None
            for i in range(kk - 1, j):
                if dp[kk - 1][i] is None:
                    continue
                cand = dp[kk - 1][i] + seg_cost(i, j)
                if best is None or cand < best:
                    best, best_i = cand, i
            dp[kk][j] = best
            arg[kk][j] = best_i
    cuts = []
    j = n
    for kk in range(k, 0, -1):
        i = arg[kk][j]
        cuts.append(i)
        j = i
    cuts = sorted(cuts[:-1])
    # Undo the integer scaling: costs above are sum over segments of
    # (cnt*S2 - S1^2)/cnt in integer units; the true SSE divides by denom^2
    # and weights by 1/n.
    sse = dp[k][n] / (denom * denom) / n
    return sse, cuts, xs


def run_scalar(n=1000, k=3, seed=77):
    rng = Lcg(seed)
    values = [clt_rational(rng) for _ in range(n)]
    mean = sum(values) / n
    values = [v - mean for v in values]
    start = time.time()
    sse, cuts, xs = exact_interval_dp(values, k)
    elapsed = time.time() - start
    bounds = [0, *cuts, n]
    masses = [Fraction(b - a, n) for a, b in zip(bounds, bounds[1:])]
    result = {
        "provenance": provenance("scalar", {"n": n, "k": k, "seed": seed}),
        "exact_min_sse": str(sse),
        "cell_masses": [str(m) for m in masses],
        "min_cell_mass": str(min(masses)),
        "min_cell_mass_float": float(min(masses)),
        "population_min_mass_gauss_k3": 0.2703,
        "wall_seconds": round(elapsed, 1),
    }
    # Anchor the library's float DP on the same data.
    try:
        import numpy as np

        from scorequant.quantizers import scalar_interval_dp

        labels, lib_sse = scalar_interval_dp(
            np.array([float(v) for v in values]), np.full(n, 1.0 / n), k
        )
        lib_masses = sorted(
            float(np.sum(labels == b)) / n for b in range(k)
        )
        result["library_sse"] = lib_sse
        result["library_min_cell_mass"] = lib_masses[0]
        result["library_agrees_within_1e-9"] = abs(lib_sse - float(sse)) <= 1e-9 * max(
            1.0, abs(float(sse))
        )
    except ImportError:
        result["library_sse"] = None
    return result


# ----------------------------------------------------------------------------
# Entry point.
# ----------------------------------------------------------------------------


def main():
    args = sys.argv[1:]
    mode = args[0] if args else "all"
    out_path = None
    if "--out" in args:
        out_path = Path(args[args.index("--out") + 1])
    sizes = (12, 13)
    if "--sizes" in args:
        sizes = tuple(int(x) for x in args[args.index("--sizes") + 1].split(","))
    report = {}
    if mode in ("identities", "all"):
        report["identities"] = run_identities()
    if mode in ("vacuity", "all"):
        report["vacuity"] = run_vacuity()
    if mode in ("exhaustive", "all"):
        report["exhaustive"] = run_exhaustive(sizes=sizes)
    if mode in ("scalar", "all"):
        report["scalar"] = run_scalar()
    text = json.dumps(report, indent=2)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n")
        print(f"wrote {out_path}")
    else:
        print(text)


if __name__ == "__main__":
    main()
