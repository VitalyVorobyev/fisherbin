"""Independent audit instrument for O6 (RETENTION-PLUGIN-CLT-FROZEN-SCALAR).

Built by the AUDIT-SCORE-ORACLE-ROBUSTNESS session without reading the
researcher's ``py/score_oracle_retention_uncertainty.py``. Stages:

``exact``
    ``fractions.Fraction`` identities: the residual-sum-of-squares form of the
    plug-in ratio with ties, duplicates, singleton and empty cells; the
    gradient reduction ``grad g . (T - theta) = psi`` atom by atom; the
    numerator-denominator covariance form of ``sigma^2``; the order-four
    moment expansion of ``sigma_hat^2``; the ``sigma^2 = 0`` laws (two atoms
    per cell at ``eta = 3/4``, a double root at ``c_b = 0``, and the ``eta = 0``
    law with four atoms in one cell) with exhaustive small-sample enumeration.
``popref``
    Closed-form population references for the door3 rungs: the frozen rule
    is rebuilt from the example module, its cuts are mapped through the
    logit to quadratic roots in ``x``, cell probabilities and score moments
    are Gaussian-CDF differences, and ``v``, ``E[S^4]``, ``sigma^2`` and the
    proxy population value come from two independent quadrature routes.
``coverage``
    Fresh-seed Monte Carlo replication of the Wald interval on the rung
    ``n_per_class = 15``, the boundary rung ``n_per_class = 300``, the
    two-atom ``sigma^2 = 0`` law and an atomless ``eta = 0`` law.
``fixtures``
    Serialises the boundary counterexample to ``COUNTEREXAMPLES/``.

Every stage writes a provenance-stamped JSON record under
``AUDITS/artifacts/AUDIT-SCORE-ORACLE-ROBUSTNESS-001/``. Run with
``JAX_ENABLE_X64=1`` for the library stages.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

RESEARCH = Path(__file__).resolve().parents[1]
ROOT = RESEARCH.parent
ARTIFACTS = RESEARCH / "AUDITS" / "artifacts" / "AUDIT-SCORE-ORACLE-ROBUSTNESS-001"
FIXTURE_ID = "CE-O6-ETA-ZERO-MULTIATOM-VARIANCE-001"

# Recorded by the researcher (KNOWN_RESULTS/10-oracle.md, O6.7); six decimals.
RECORDED_RUNG15 = {
    "eta": 0.893663,
    "sigma": 0.235410,
    "eta_proxy": 0.967064,
    "cell_probabilities": [0.4953, 0.1215, 0.2193, 0.1638],
    "fourth_moment": 2.7336,
}

Z975 = 1.959963984540054


def provenance(mode: str, parameters: dict[str, object]) -> dict[str, object]:
    """Return the reproducibility record required by the numerical protocol."""
    script = Path(__file__)
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, check=True, text=True
    ).stdout.strip()
    return {
        "mode": mode,
        "parameters": parameters,
        "git_revision": revision,
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }


def fr(value: Fraction | int) -> str:
    return str(Fraction(value))


def write_record(name: str, record: dict[str, object]) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / f"{name}.json"
    path.write_text(json.dumps(record, indent=1) + "\n")
    print(f"wrote {path.relative_to(ROOT)}")


# --------------------------------------------------------------------------
# Exact algebra (fractions.Fraction)
# --------------------------------------------------------------------------


class Lcg:
    """Small deterministic integer generator, independent of NumPy."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def next(self) -> int:
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state

    def rational(self, span: int = 6, denominator: int = 4) -> Fraction:
        return Fraction(
            self.next() % (2 * span * denominator + 1) - span * denominator, denominator
        )

    def choice(self, n: int) -> int:
        return self.next() % n


def plugin_exact(scores: list[Fraction], labels: list[int], n_bins: int) -> dict[str, object]:
    """Plug-in ratio and influence values of one sample, all in exact arithmetic."""
    n = len(scores)
    counts = [0] * n_bins
    sums = [Fraction(0)] * n_bins
    for s, b in zip(scores, labels, strict=True):
        counts[b] += 1
        sums[b] += s
    means = [sums[b] / counts[b] if counts[b] else Fraction(0) for b in range(n_bins)]
    p_hat = [Fraction(counts[b], n) for b in range(n_bins)]
    m_hat = [sums[b] / n for b in range(n_bins)]
    v_hat = sum(s * s for s in scores) / n
    between = sum(m_hat[b] ** 2 / p_hat[b] for b in range(n_bins) if p_hat[b] > 0)
    eta_moment = between / v_hat if v_hat > 0 else Fraction(0)
    rss = sum((s - means[b]) ** 2 for s, b in zip(scores, labels, strict=True))
    tss = sum(s * s for s in scores)
    eta_rss = 1 - rss / tss if tss > 0 else Fraction(0)
    if v_hat > 0:
        psi = [
            ((1 - eta_moment) * s * s - (s - means[b]) ** 2) / v_hat
            for s, b in zip(scores, labels, strict=True)
        ]
    else:
        psi = [Fraction(0)] * n
    return {
        "n": n,
        "counts": counts,
        "means": means,
        "p_hat": p_hat,
        "m_hat": m_hat,
        "v_hat": v_hat,
        "eta_moment": eta_moment,
        "eta_rss": eta_rss,
        "psi": psi,
        "psi_sum": sum(psi),
        "sigma2_hat": sum(x * x for x in psi) / n,
    }


def sigma2_hat_from_moments(sample: dict[str, object], scores, labels, n_bins) -> Fraction:
    """O6.3: sigma_hat^2 as a polynomial in within-cell moments of order <= 4."""
    n = sample["n"]
    moments = [[Fraction(0)] * 5 for _ in range(n_bins)]
    for s, b in zip(scores, labels, strict=True):
        for k in range(5):
            moments[b][k] += s**k
    for b in range(n_bins):
        for k in range(5):
            moments[b][k] /= n
    eta = sample["eta_moment"]
    v = sample["v_hat"]
    total = Fraction(0)
    for b in range(n_bins):
        c = sample["means"][b]
        m0, m1, m2, m3, m4 = moments[b]
        total += (
            eta**2 * m4 - 4 * eta * c * m3 + (4 + 2 * eta) * c**2 * m2 - 4 * c**3 * m1 + c**4 * m0
        )
    return total / v**2


def law_exact(atoms: list[tuple[Fraction, int, Fraction]], n_bins: int) -> dict[str, object]:
    """Population functionals of an exact atomic law of (S, Z)."""
    assert sum(w for _, _, w in atoms) == 1
    p = [Fraction(0)] * n_bins
    m = [Fraction(0)] * n_bins
    for s, b, w in atoms:
        p[b] += w
        m[b] += w * s
    c = [m[b] / p[b] if p[b] else Fraction(0) for b in range(n_bins)]
    v = sum(w * s * s for s, _, w in atoms)
    mean = sum(w * s for s, _, w in atoms)
    between = sum(m[b] ** 2 / p[b] for b in range(n_bins) if p[b] > 0)
    eta = between / v
    psi = [((1 - eta) * s * s - (s - c[b]) ** 2) / v for s, b, _ in atoms]
    e_psi = sum(w * x for x, (_, _, w) in zip(psi, atoms, strict=True))
    sigma2 = sum(w * x * x for x, (_, _, w) in zip(psi, atoms, strict=True))
    # Numerator/denominator influence values.
    n1 = [2 * c[b] * s - c[b] ** 2 for s, b, _ in atoms]
    d1 = [s * s for s, _, _ in atoms]
    e_n1 = sum(w * x for x, (_, _, w) in zip(n1, atoms, strict=True))
    e_d1 = v
    var_n1 = sum(w * (x - e_n1) ** 2 for x, (_, _, w) in zip(n1, atoms, strict=True))
    var_d1 = sum(w * (x - e_d1) ** 2 for x, (_, _, w) in zip(d1, atoms, strict=True))
    cov = sum(w * (x - e_n1) * (y - e_d1) for x, y, (_, _, w) in zip(n1, d1, atoms, strict=True))
    sigma2_cov_form = (var_n1 - 2 * eta * cov + eta**2 * var_d1) / v**2
    # Gradient reduction atom by atom: grad g . (T - theta).
    grad_dot = []
    for s, b, _ in atoms:
        total = Fraction(0)
        for bb in range(n_bins):
            if p[bb] == 0:
                continue
            ind = Fraction(1 if bb == b else 0)
            total += -(m[bb] ** 2) / (p[bb] ** 2 * v) * (ind - p[bb])
            total += 2 * m[bb] / (p[bb] * v) * (s * ind - m[bb])
        total += -eta / v * (s * s - v)
        grad_dot.append(total)
    return {
        "p": p,
        "m": m,
        "c": c,
        "v": v,
        "mean": mean,
        "eta": eta,
        "psi": psi,
        "E_psi": e_psi,
        "sigma2": sigma2,
        "E_N1": e_n1,
        "eta_v": eta * v,
        "sigma2_cov_form": sigma2_cov_form,
        "grad_dot_minus_psi": [g - x for g, x in zip(grad_dot, psi, strict=True)],
    }


def random_law(rng: Lcg, n_bins: int, n_atoms: int) -> list[tuple[Fraction, int, Fraction]]:
    weights = [Fraction(1 + rng.choice(5)) for _ in range(n_atoms)]
    total = sum(weights)
    atoms = []
    for i in range(n_atoms):
        atoms.append(
            (rng.rational(), i % n_bins if i < n_bins else rng.choice(n_bins), weights[i] / total)
        )
    return atoms


def two_atom_law() -> list[tuple[Fraction, int, Fraction]]:
    """K = 2, eta = 3/4, E[S] = 0, sigma^2 = 0: roots s = c/(1 -+ sqrt(1 - eta))."""
    return [
        (Fraction(2, 3), 0, Fraction(3, 8)),
        (Fraction(2), 0, Fraction(1, 8)),
        (Fraction(-2, 3), 1, Fraction(3, 8)),
        (Fraction(-2), 1, Fraction(1, 8)),
    ]


def double_root_law() -> list[tuple[Fraction, int, Fraction]]:
    """One cell with c_b = 0 (S = 0 a.s.) beside a two-atom cell; eta = 3/4, sigma^2 = 0."""
    return [
        (Fraction(0), 0, Fraction(1, 2)),
        (Fraction(2, 3), 1, Fraction(3, 8)),
        (Fraction(2), 1, Fraction(1, 8)),
    ]


def eta_zero_law() -> list[tuple[Fraction, int, Fraction]]:
    """K = 2, every cell mean zero, four atoms in cell 0: eta = 0 and psi = 0 identically."""
    return [
        (Fraction(-3), 0, Fraction(1, 8)),
        (Fraction(-1), 0, Fraction(1, 8)),
        (Fraction(1), 0, Fraction(1, 8)),
        (Fraction(3), 0, Fraction(1, 8)),
        (Fraction(-2), 1, Fraction(1, 4)),
        (Fraction(2), 1, Fraction(1, 4)),
    ]


def enumerate_law_samples(
    atoms: list[tuple[Fraction, int, Fraction]], n_bins: int, max_n: int
) -> dict[str, object]:
    """Exhaustively enumerate multiplicity vectors of samples of size <= max_n."""
    law = law_exact(atoms, n_bins)
    eta = law["eta"]
    summary = {
        "eta": fr(eta),
        "sigma2": fr(law["sigma2"]),
        "samples": 0,
        "eta_hat_below_eta": 0,
        "eta_hat_equal_eta": 0,
        "sigma_hat_zero": 0,
        "sigma_hat_zero_and_eta_hat_ne_eta": 0,
        "eta_hat_eq_eta_and_sigma_hat_nonzero": 0,
        "max_eta_hat": fr(0),
        "min_eta_hat": fr(1),
        "example_minimum": None,
    }
    k = len(atoms)
    max_eta = Fraction(0)
    min_eta = Fraction(1)
    for n in range(1, max_n + 1):
        for cuts in itertools.combinations(range(n + k - 1), k - 1):
            counts = []
            previous = -1
            for cut in (*cuts, n + k - 1):
                counts.append(cut - previous - 1)
                previous = cut
            scores: list[Fraction] = []
            labels: list[int] = []
            for (s, b, _), count in zip(atoms, counts, strict=True):
                scores.extend([s] * count)
                labels.extend([b] * count)
            sample = plugin_exact(scores, labels, n_bins)
            assert sample["eta_moment"] == sample["eta_rss"]
            summary["samples"] += 1
            eh = sample["eta_moment"]
            if eh < eta:
                summary["eta_hat_below_eta"] += 1
            if eh == eta:
                summary["eta_hat_equal_eta"] += 1
                if sample["sigma2_hat"] != 0:
                    summary["eta_hat_eq_eta_and_sigma_hat_nonzero"] += 1
            if sample["sigma2_hat"] == 0:
                summary["sigma_hat_zero"] += 1
                if eh != eta:
                    summary["sigma_hat_zero_and_eta_hat_ne_eta"] += 1
            if eh > max_eta:
                max_eta = eh
            if eh < min_eta:
                min_eta = eh
                summary["example_minimum"] = {"n": n, "counts": counts, "eta_hat": fr(eh)}
    summary["max_eta_hat"] = fr(max_eta)
    summary["min_eta_hat"] = fr(min_eta)
    return summary


def stage_exact() -> dict[str, object]:
    import scorequant as sq

    record: dict[str, object] = {}
    # 1. Finite identity O6.1 on adversarial samples, against the library.
    samples = {
        "ties_and_duplicates": (
            [
                Fraction(1),
                Fraction(1),
                Fraction(-1, 2),
                Fraction(-1, 2),
                Fraction(3, 2),
                Fraction(0),
            ],
            [0, 1, 1, 0, 2, 2],
            3,
        ),
        "singleton_cell": (
            [Fraction(2), Fraction(-1), Fraction(1, 3), Fraction(5, 4), Fraction(-3, 2)],
            [0, 1, 1, 1, 2],
            3,
        ),
        "empty_declared_cell": (
            [
                Fraction(2),
                Fraction(-1),
                Fraction(1, 3),
                Fraction(5, 4),
                Fraction(-3, 2),
                Fraction(7, 3),
            ],
            [0, 1, 1, 0, 2, 2],
            4,
        ),
        "empty_cell_with_zero_mean_cell": (
            [Fraction(1), Fraction(-1), Fraction(2), Fraction(3)],
            [0, 0, 2, 2],
            3,
        ),
        "eta_hat_zero": ([Fraction(1), Fraction(-1), Fraction(2), Fraction(-2)], [0, 0, 1, 1], 2),
        "eta_hat_one": ([Fraction(1), Fraction(1), Fraction(-2), Fraction(-2)], [0, 0, 1, 1], 2),
    }
    identity: dict[str, object] = {}
    for name, (scores, labels, n_bins) in samples.items():
        sample = plugin_exact(scores, labels, n_bins)
        report = sq.information_report(
            np.array([[float(s)] for s in scores]), np.array(labels), n_bins=n_bins
        )
        fisher = sq.binned_fisher_information(
            np.array([[float(s)] for s in scores]), np.array(labels), n_bins=n_bins
        )
        library = float(report.geometric_mean_retention)
        exact_between = sum(
            sample["m_hat"][b] ** 2 / sample["p_hat"][b]
            for b in range(n_bins)
            if sample["p_hat"][b]
        )
        sigma2_moments = sigma2_hat_from_moments(sample, scores, labels, n_bins)
        identity[name] = {
            "eta_hat_moment": fr(sample["eta_moment"]),
            "eta_hat_rss": fr(sample["eta_rss"]),
            "identity_holds": sample["eta_moment"] == sample["eta_rss"],
            "psi_sum": fr(sample["psi_sum"]),
            "library_geometric_mean_retention": library,
            "library_abs_error": abs(library - float(sample["eta_moment"])),
            "library_binned_fisher_abs_error": abs(float(fisher[0, 0]) / len(scores) - float(exact_between)),
            "sigma2_hat_direct": fr(sample["sigma2_hat"]),
            "sigma2_hat_order4_expansion_holds": sigma2_moments == sample["sigma2_hat"],
            "bin_counts": [int(x) for x in np.asarray(report.bin_counts)],
        }
    # all-zero scores: the target is undefined and the library must refuse.
    try:
        sq.information_report(np.zeros((4, 1)), np.array([0, 0, 1, 1]), n_bins=2)
        identity["all_zero_scores"] = "library returned a report (unexpected)"
    except Exception as error:  # noqa: BLE001 - recording the refusal class is the point
        identity["all_zero_scores"] = f"library refused: {type(error).__name__}: {error}"
    record["identity"] = identity

    # 2. Gradient reduction and covariance form on random exact atomic laws.
    rng = Lcg(20260906)
    laws = []
    violations = 0
    for index in range(60):
        n_bins = 1 + index % 3
        atoms = random_law(rng, n_bins, n_bins + 1 + rng.choice(4))
        law = law_exact(atoms, n_bins)
        ok = (
            law["E_psi"] == 0
            and law["E_N1"] == law["eta_v"]
            and law["sigma2"] == law["sigma2_cov_form"]
            and all(x == 0 for x in law["grad_dot_minus_psi"])
        )
        violations += not ok
        if index < 3:
            laws.append(
                {
                    "atoms": [(fr(s), b, fr(w)) for s, b, w in atoms],
                    "eta": fr(law["eta"]),
                    "sigma2": fr(law["sigma2"]),
                    "checks": ok,
                }
            )
    record["gradient_and_covariance"] = {
        "laws_checked": 60,
        "violations": violations,
        "first_laws": laws,
        "checks": [
            "E[psi] = 0",
            "E[N1] = eta v",
            "E[psi^2] = (Var N1 - 2 eta Cov(N1, S^2) + eta^2 Var S^2) / v^2",
            "grad g . (T(s, b) - theta) = psi(s, b) at every atom",
        ],
    }

    # 3. sigma^2 = 0 laws.
    degenerate: dict[str, object] = {}
    for name, atoms, n_bins, max_n in (
        ("two_atom_eta_3_4", two_atom_law(), 2, 8),
        ("double_root_c_b_zero", double_root_law(), 2, 8),
        ("eta_zero_four_atoms_in_one_cell", eta_zero_law(), 2, 6),
    ):
        law = law_exact(atoms, n_bins)
        entry = {
            "atoms": [(fr(s), b, fr(w)) for s, b, w in atoms],
            "p": [fr(x) for x in law["p"]],
            "c": [fr(x) for x in law["c"]],
            "v": fr(law["v"]),
            "mean_S": fr(law["mean"]),
            "eta": fr(law["eta"]),
            "sigma2": fr(law["sigma2"]),
            "psi_values": [fr(x) for x in law["psi"]],
            "atoms_per_cell": [sum(1 for _, b, _ in atoms if b == cell) for cell in range(n_bins)],
        }
        if 0 < law["eta"] < 1:
            root = 1 - law["eta"]
            entry["root_check"] = [fr((s - law["c"][b]) ** 2 - root * s * s) for s, b, _ in atoms]
            entry["within_cell_second_moment_over_c2"] = [
                fr(sum(w * s * s for s, bb, w in atoms if bb == b) / law["p"][b] / law["c"][b] ** 2)
                if law["c"][b] != 0
                else None
                for b in range(n_bins)
            ]
        entry["enumeration"] = enumerate_law_samples(atoms, n_bins, max_n)
        degenerate[name] = entry
    # Weight formula w = eta / (2 (1 + sqrt(1 - eta))) at eta = 3/4.
    eta = Fraction(3, 4)
    degenerate["two_atom_weight_formula"] = {
        "w_formula": fr(eta / (2 * (1 + Fraction(1, 2)))),
        "w_law": fr(Fraction(1, 8) / Fraction(1, 2)),
    }
    record["degenerate_laws"] = degenerate
    record["provenance"] = provenance("exact", {"lcg_seed": 20260906, "random_laws": 60})
    return record


# --------------------------------------------------------------------------
# Closed-form population references for the door3 rungs
# --------------------------------------------------------------------------


def door3_rule(n_per_class: int) -> dict[str, object]:
    """Rebuild one frozen door3 rung from the example module's public functions."""
    import scorequant as sq
    from examples import door3_classifier as door3

    index = door3.N_PER_CLASS_VALUES.index(n_per_class)
    model = door3.train_classifier(door3.CLASSIFIER_SEED_BASE + index, n_per_class)
    provider = door3.classifier_provider(
        model, description=f"logistic regression, {n_per_class} events per class"
    )
    train = door3.draw_reference_mixture(door3.TRAIN_SEED, door3.N_TRAIN)
    result = sq.fit_quantizer(
        sq.ObservationSample(train),
        provider=provider,
        n_bins=door3.N_BINS,
        criterion=sq.DOptimality(),
        config=sq.DExchangeConfig(seed=door3.SOLVER_SEED),
    )
    test = door3.draw_reference_mixture(door3.TEST_SEED, door3.N_TEST)
    oracle = door3.exact_provider()
    oracle_test = np.asarray(oracle.score(test))
    provider_test = np.asarray(provider.score(test))
    surrogate = float(result.evaluate_scores(provider_test).geometric_mean_retention)
    labels = np.asarray(result.predict_scores(provider_test))
    true = float(
        sq.information_report(oracle_test, labels, n_bins=result.n_bins).geometric_mean_retention
    )
    coef = model.coef_[0]
    logit = (float(model.intercept_[0]), float(coef[0]), float(coef[1]))
    matrix = float(np.asarray(result.transform.matrix)[0, 0])
    centers_transformed = np.asarray(result.centers)[:, 0]
    metric = result.metric
    return {
        "n_per_class": n_per_class,
        "classifier_seed": door3.CLASSIFIER_SEED_BASE + index,
        "logit": logit,
        "transform_matrix": matrix,
        "centers_transformed": centers_transformed,
        "metric": None if metric is None else float(np.asarray(metric)[0, 0]),
        "ladder_reproduction": {"surrogate_retention": surrogate, "true_retention": true},
        "result": result,
        "provider": provider,
        "oracle": oracle,
    }


def closed_form_surrogate(x: np.ndarray, logit: tuple[float, float, float]) -> np.ndarray:
    """s_hat(x) = (u - 1) / (0.3 u + 0.7), u = exp(-logit(x)); logit = a + b x + c x^2."""
    from examples import door3_classifier as door3

    a, b, c = logit
    u = np.exp(-(a + b * x + c * x * x))
    f0, f1 = door3.REFERENCE_FRACTIONS
    return (u - 1) / (f0 * u + f1)


def closed_form_exact_score(x: np.ndarray) -> np.ndarray:
    """s(x) = (phi_sig - phi_bkg) / f(x) for the fraction-of-signal parameter."""
    from examples import door3_classifier as door3

    f0, f1 = door3.REFERENCE_FRACTIONS
    phi_s = door3.signal_pdf(x)
    phi_b = door3.background_pdf(x)
    return (phi_s - phi_b) / (f0 * phi_s + f1 * phi_b)


def mixture_density(x: np.ndarray) -> np.ndarray:
    from examples import door3_classifier as door3

    f0, f1 = door3.REFERENCE_FRACTIONS
    return f0 * door3.signal_pdf(x) + f1 * door3.background_pdf(x)


def gaussian_cdf(x: float, mu: float, sigma: float) -> float:
    from scipy.special import ndtr

    return float(ndtr((x - mu) / sigma))


def cell_geometry(rule: dict[str, object]) -> dict[str, object]:
    """Cuts in s_hat space, their logit images, and the x-intervals per cell."""
    from examples import door3_classifier as door3

    f0, f1 = door3.REFERENCE_FRACTIONS
    centers = np.asarray(rule["centers_transformed"]) / rule["transform_matrix"]
    order = np.argsort(centers)
    sorted_centers = centers[order]
    cuts_s = 0.5 * (sorted_centers[1:] + sorted_centers[:-1])
    a, b, c = rule["logit"]
    roots: list[float] = []
    cut_logits: list[float] = []
    for t in cuts_s:
        u = (1 + f1 * t) / (1 - f0 * t)
        ell = -math.log(u)
        cut_logits.append(ell)
        # c x^2 + b x + (a - ell) = 0
        disc = b * b - 4 * c * (a - ell)
        if disc > 0:
            r = math.sqrt(disc)
            roots.extend([(-b - r) / (2 * c), (-b + r) / (2 * c)])
        elif disc == 0:
            roots.append(-b / (2 * c))
    roots = sorted(roots)
    edges = [-math.inf, *roots, math.inf]
    intervals = []
    for lo, hi in zip(edges[:-1], edges[1:], strict=True):
        if math.isinf(lo) and math.isinf(hi):
            mid = 0.0
        elif math.isinf(lo):
            mid = hi - 1.0
        elif math.isinf(hi):
            mid = lo + 1.0
        else:
            mid = 0.5 * (lo + hi)
        s_mid = closed_form_surrogate(np.array([mid]), rule["logit"])[0]
        cell = int(order[int(np.searchsorted(cuts_s, s_mid))])
        intervals.append({"lo": lo, "hi": hi, "cell": cell})
    return {
        "centers_raw_sorted": sorted_centers.tolist(),
        "cell_order_by_center": order.tolist(),
        "cuts_s_hat": cuts_s.tolist(),
        "cut_logits": cut_logits,
        "roots_x": roots,
        "intervals": intervals,
    }


def label_closed_form(x: np.ndarray, geometry: dict[str, object]) -> np.ndarray:
    roots = np.asarray(geometry["roots_x"])
    cells = np.asarray([item["cell"] for item in geometry["intervals"]])
    return cells[np.searchsorted(roots, x, side="right")]


def population_reference(rule: dict[str, object], geometry: dict[str, object]) -> dict[str, object]:
    """p_b, m_b in closed form; v, E[S^4], sigma^2 and the proxy value by two quadratures."""
    from numpy.polynomial.legendre import leggauss
    from scipy.integrate import quad

    from examples import door3_classifier as door3

    f0, f1 = door3.REFERENCE_FRACTIONS
    n_bins = int(rule["result"].n_bins)
    mu_s, sd_s = door3.SIGNAL_MU, door3.SIGNAL_SIGMA
    mu_b, sd_b = door3.BACKGROUND_MU, door3.BACKGROUND_SIGMA
    p = np.zeros(n_bins)
    m = np.zeros(n_bins)
    for item in geometry["intervals"]:
        lo, hi, cell = item["lo"], item["hi"], item["cell"]
        d_sig = gaussian_cdf(hi, mu_s, sd_s) - gaussian_cdf(lo, mu_s, sd_s)
        d_bkg = gaussian_cdf(hi, mu_b, sd_b) - gaussian_cdf(lo, mu_b, sd_b)
        p[cell] += f0 * d_sig + f1 * d_bkg
        m[cell] += d_sig - d_bkg  # integral of s f = phi_sig - phi_bkg
    c = m / p
    logit = rule["logit"]

    def integrate(fn, route: str, intervals=None) -> float:
        total = 0.0
        limit = 15.0
        for item in geometry["intervals"] if intervals is None else intervals:
            lo = max(item["lo"], -limit)
            hi = min(item["hi"], limit)
            if route == "quad":
                value, _ = quad(
                    lambda t: float(fn(np.array([t]), item["cell"])[0]),
                    lo,
                    hi,
                    epsabs=1e-15,
                    epsrel=1e-13,
                    limit=400,
                )
                total += value
            else:
                nodes, weights = leggauss(64)
                panels = 200
                edges = np.linspace(lo, hi, panels + 1)
                for a, b in zip(edges[:-1], edges[1:], strict=True):
                    t = 0.5 * (b - a) * nodes + 0.5 * (b + a)
                    total += 0.5 * (b - a) * float(np.sum(weights * fn(t, item["cell"])))
        return total

    def f_s2(t, _cell):
        return closed_form_exact_score(t) ** 2 * mixture_density(t)

    def f_s4(t, _cell):
        return closed_form_exact_score(t) ** 4 * mixture_density(t)

    def f_p(t, _cell):
        return mixture_density(t)

    def f_m(t, _cell):
        return closed_form_exact_score(t) * mixture_density(t)

    def f_shat(t, _cell):
        return closed_form_surrogate(t, logit) * mixture_density(t)

    def f_shat2(t, _cell):
        return closed_form_surrogate(t, logit) ** 2 * mixture_density(t)

    out: dict[str, object] = {"p": p.tolist(), "m": m.tolist(), "c": c.tolist()}
    routes: dict[str, dict[str, float]] = {}
    for route in ("quad", "gauss_legendre"):
        v = integrate(f_s2, route)
        s4 = integrate(f_s4, route)
        p_quad = np.zeros(n_bins)
        m_quad = np.zeros(n_bins)
        mt = np.zeros(n_bins)
        for item in geometry["intervals"]:
            cell = item["cell"]
            p_quad[cell] += integrate(f_p, route, [item])
            m_quad[cell] += integrate(f_m, route, [item])
            mt[cell] += integrate(f_shat, route, [item])
        vt = integrate(f_shat2, route)
        eta = float(np.sum(m * m / p) / v)
        eta_proxy = float(np.sum(mt * mt / p) / vt)
        ct = mt / p

        def f_psi2(t, cell, eta=eta, v=v):
            s = closed_form_exact_score(t)
            psi = ((1 - eta) * s * s - (s - c[cell]) ** 2) / v
            return psi * psi * mixture_density(t)

        def f_psi2_proxy(t, cell, eta=eta_proxy, v=vt):
            s = closed_form_surrogate(t, logit)
            psi = ((1 - eta) * s * s - (s - ct[cell]) ** 2) / v
            return psi * psi * mixture_density(t)

        sigma2 = integrate(f_psi2, route)
        sigma2_proxy = integrate(f_psi2_proxy, route)
        routes[route] = {
            "v": v,
            "fourth_moment": s4,
            "eta": eta,
            "sigma": math.sqrt(sigma2),
            "sigma2": sigma2,
            "eta_proxy": eta_proxy,
            "sigma_proxy": math.sqrt(sigma2_proxy),
            "v_proxy": vt,
            "max_abs_p_closed_minus_quadrature": float(np.max(np.abs(p - p_quad))),
            "max_abs_m_closed_minus_quadrature": float(np.max(np.abs(m - m_quad))),
            "m_proxy": mt.tolist(),
        }
    out["routes"] = routes
    out["route_disagreement"] = {
        key: abs(routes["quad"][key] - routes["gauss_legendre"][key])
        for key in ("v", "fourth_moment", "eta", "sigma", "eta_proxy", "sigma_proxy")
    }
    out["sum_p_minus_one"] = float(np.sum(p) - 1)
    out["sum_m"] = float(np.sum(m))  # = E[S], exactly zero in closed form
    tail = 2 * (f1 * gaussian_cdf(-15.0, 0.0, sd_b) + f0 * gaussian_cdf(-14.0, 0.0, sd_s))
    out["tail_mass_beyond_truncation"] = tail
    out["score_bound"] = 1 / f0
    return out


def stage_popref() -> dict[str, object]:
    from examples import door3_classifier as door3

    record: dict[str, object] = {"rungs": {}}
    metrics = json.loads((ROOT / door3.METRICS_PATH).read_text())
    published = {row["n_per_class"]: row for row in metrics["ladder"]}
    for n_per_class in (15, 300):
        rule = door3_rule(n_per_class)
        geometry = cell_geometry(rule)
        # Verify the closed-form maps against the library on a fresh sample.
        rng = np.random.default_rng(20260906 + n_per_class)
        x = door3.draw_reference_mixture(int(rng.integers(0, 2**31)), 1_000_000)
        s_hat_lib = np.asarray(rule["provider"].score(x))[:, 0]
        s_lib = np.asarray(rule["oracle"].score(x))[:, 0]
        labels_lib = np.asarray(rule["result"].predict_scores(s_hat_lib[:, None]))
        labels_cf = label_closed_form(x[:, 0], geometry)
        grid = np.linspace(-1.4, 3.3, 2_000_001)
        grid_labels = np.asarray(rule["result"].predict_scores(grid[:, None]))
        changes = grid[1:][grid_labels[1:] != grid_labels[:-1]]
        reference = population_reference(rule, geometry)
        record["rungs"][str(n_per_class)] = {
            "classifier_seed": rule["classifier_seed"],
            "logit_coefficients_a_b_c": rule["logit"],
            "transform_matrix": rule["transform_matrix"],
            "metric": rule["metric"],
            "ladder_reproduction": rule["ladder_reproduction"],
            "ladder_published": {
                "surrogate_retention": published[n_per_class]["surrogate_retention"],
                "true_retention": published[n_per_class]["true_retention"],
            },
            "geometry": geometry,
            "grid_label_changes_s_hat": changes.tolist(),
            "closed_form_checks": {
                "max_abs_s_hat_error": float(
                    np.max(np.abs(s_hat_lib - closed_form_surrogate(x[:, 0], rule["logit"])))
                ),
                "max_abs_exact_score_error": float(
                    np.max(np.abs(s_lib - closed_form_exact_score(x[:, 0])))
                ),
                "label_disagreements_of_1e6": int(np.sum(labels_lib != labels_cf)),
                "empirical_cell_frequencies": np.bincount(labels_lib, minlength=4).tolist(),
            },
            "reference": reference,
        }
    rung15 = record["rungs"]["15"]["reference"]["routes"]["quad"]
    record["comparison_with_recorded_rung15"] = {
        "eta": rung15["eta"] - RECORDED_RUNG15["eta"],
        "sigma": rung15["sigma"] - RECORDED_RUNG15["sigma"],
        "eta_proxy": rung15["eta_proxy"] - RECORDED_RUNG15["eta_proxy"],
        "fourth_moment": rung15["fourth_moment"] - RECORDED_RUNG15["fourth_moment"],
        "cell_probabilities": [
            a - b
            for a, b in zip(
                record["rungs"]["15"]["reference"]["p"],
                RECORDED_RUNG15["cell_probabilities"],
                strict=True,
            )
        ],
        "note": "recorded values carry four to six decimals; differences below 5e-7 (or 5e-5 for probabilities) are rounding",
    }
    record["provenance"] = provenance(
        "popref", {"rungs": [15, 300], "verification_sample": 1_000_000}
    )
    return record


# --------------------------------------------------------------------------
# Coverage replication with fresh seeds
# --------------------------------------------------------------------------


def wald_statistics(
    scores: np.ndarray, labels: np.ndarray, n_bins: int
) -> tuple[float, float, bool]:
    n = scores.shape[0]
    counts = np.bincount(labels, minlength=n_bins).astype(float)
    sums = np.bincount(labels, weights=scores, minlength=n_bins)
    means = np.divide(sums, counts, out=np.zeros(n_bins), where=counts > 0)
    v = float(np.mean(scores * scores))
    between = (
        float(np.sum(np.divide(sums * sums, counts, out=np.zeros(n_bins), where=counts > 0))) / n
    )
    eta = between / v
    psi = ((1 - eta) * scores * scores - (scores - means[labels]) ** 2) / v
    sigma2 = float(np.mean(psi * psi))
    return eta, math.sqrt(sigma2), bool(np.any(counts == 0))


def skewness(values: np.ndarray) -> float:
    centred = values - values.mean()
    return float(np.mean(centred**3) / np.mean(centred**2) ** 1.5)


def replicate(
    draw,
    n: int,
    replicates: int,
    n_bins: int,
    eta: float,
    sigma: float,
    eta_proxy: float | None,
    seed,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    eta_hat = np.empty(replicates)
    sigma_hat = np.empty(replicates)
    empty = 0
    for r in range(replicates):
        scores, labels = draw(rng, n)
        eta_hat[r], sigma_hat[r], had_empty = wald_statistics(scores, labels, n_bins)
        empty += had_empty
    half = Z975 * sigma_hat / math.sqrt(n)
    covers = np.abs(eta_hat - eta) <= half
    coverage = float(np.mean(covers))
    out: dict[str, object] = {
        "n": n,
        "replicates": replicates,
        "coverage": coverage,
        "coverage_se": math.sqrt(coverage * (1 - coverage) / replicates),
        "sd_eta_hat": float(np.std(eta_hat, ddof=1)),
        "sigma_over_sqrt_n": sigma / math.sqrt(n),
        "mean_sigma_hat_over_sqrt_n": float(np.mean(sigma_hat)) / math.sqrt(n),
        "n_times_bias": n * float(np.mean(eta_hat) - eta),
        "mean_eta_hat": float(np.mean(eta_hat)),
        "leaves_unit_interval": int(np.sum((eta_hat - half < 0) | (eta_hat + half > 1))),
        "empty_cell_replicates": int(empty),
        "fraction_eta_hat_below_eta": float(np.mean(eta_hat < eta)),
        "fraction_sigma_hat_zero": float(np.mean(sigma_hat == 0)),
    }
    if sigma > 0:
        out["rel_rmse_sigma_hat"] = float(np.sqrt(np.mean((sigma_hat / sigma - 1) ** 2)))
        out["skew_studentized_plugin"] = skewness((eta_hat - eta) / (sigma_hat / math.sqrt(n)))
        out["skew_studentized_population"] = skewness((eta_hat - eta) / (sigma / math.sqrt(n)))
        out["sd_studentized_population"] = float(
            np.std((eta_hat - eta) / (sigma / math.sqrt(n)), ddof=1)
        )
    else:
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = (eta_hat - eta) / (sigma_hat / math.sqrt(n))
        finite = ratio[np.isfinite(ratio)]
        out["studentized_quantiles_finite"] = (
            {
                q: float(np.quantile(finite, float(q)))
                for q in ("0.05", "0.25", "0.5", "0.75", "0.95")
            }
            if finite.size
            else {}
        )
        out["n_times_error_quantiles"] = {
            q: float(np.quantile(n * (eta_hat - eta), float(q)))
            for q in ("0.05", "0.5", "0.95", "0.99")
        }
        out["mean_sqrt_n_sigma_hat"] = float(np.mean(sigma_hat)) * math.sqrt(n)
    if eta_proxy is not None:
        out["covers_proxy"] = float(np.mean(np.abs(eta_hat - eta_proxy) <= half))
    return out


def stage_coverage(replicates: int = 4000) -> dict[str, object]:
    from examples import door3_classifier as door3

    popref = json.loads((ARTIFACTS / "popref.json").read_text())
    root_seed = np.random.SeedSequence(20260906)
    record: dict[str, object] = {"laws": {}}
    sizes = (100, 300, 1000, 3000)
    children = iter(root_seed.spawn(64))

    def door3_draw(geometry):
        f0, _ = door3.REFERENCE_FRACTIONS

        def draw(rng, n):
            is_signal = rng.random(n) < f0
            x = np.where(
                is_signal,
                rng.normal(door3.SIGNAL_MU, door3.SIGNAL_SIGMA, n),
                rng.normal(door3.BACKGROUND_MU, door3.BACKGROUND_SIGMA, n),
            )
            return closed_form_exact_score(x), label_closed_form(x, geometry)

        return draw

    for rung in ("15", "300"):
        info = popref["rungs"][rung]
        ref = info["reference"]["routes"]["quad"]
        rows = [
            replicate(
                door3_draw(info["geometry"]),
                n,
                replicates,
                4,
                ref["eta"],
                ref["sigma"],
                ref["eta_proxy"],
                next(children),
            )
            for n in sizes
        ]
        record["laws"][f"door3_rung_{rung}"] = {
            "eta": ref["eta"],
            "sigma": ref["sigma"],
            "eta_proxy": ref["eta_proxy"],
            "rows": rows,
        }

    def two_atom_draw(rng, n):
        cell = rng.integers(0, 2, n)
        high = rng.random(n) < 0.25
        magnitude = np.where(high, 2.0, 2.0 / 3.0)
        return np.where(cell == 0, magnitude, -magnitude), cell

    record["laws"]["two_atom_sigma_zero"] = {
        "eta": 0.75,
        "sigma": 0.0,
        "rows": [
            replicate(two_atom_draw, n, replicates, 2, 0.75, 0.0, None, next(children))
            for n in sizes
        ],
    }

    threshold = 0.6744897501960817  # Phi^{-1}(3/4): two cells of equal probability

    def eta_zero_draw(rng, n):
        s = rng.standard_normal(n)
        return s, (np.abs(s) > threshold).astype(int)

    record["laws"]["atomless_eta_zero"] = {
        "eta": 0.0,
        "sigma": 0.0,
        "description": "S ~ N(0,1), cells {|S| <= 0.6745} and {|S| > 0.6745}: both cell means vanish, so eta = 0 and psi = 0 identically although every cell is atomless",
        "rows": [
            replicate(eta_zero_draw, n, replicates, 2, 0.0, 0.0, None, next(children))
            for n in sizes
        ],
    }
    record["provenance"] = provenance(
        "coverage", {"seed_sequence": 20260906, "replicates": replicates, "sizes": list(sizes)}
    )
    return record


# --------------------------------------------------------------------------
# Fixture
# --------------------------------------------------------------------------


def stage_fixtures() -> dict[str, object]:
    atoms = eta_zero_law()
    law = law_exact(atoms, 2)
    fixture = {
        "id": FIXTURE_ID,
        "criterion": "general",
        "level": "information_accounting",
        "claim_falsified": (
            "The influence variance sigma^2 of the frozen-rule scalar retention plug-in vanishes "
            "only when S | Z = b is supported on at most two atoms per cell; in particular an "
            "atomless (or many-atom) cell of positive probability implies sigma^2 > 0 "
            "(O6.4 wording and the A4 parenthetical of RETENTION-PLUGIN-CLT-FROZEN-SCALAR as "
            "recorded on 5 September 2026)."
        ),
        "scores": [[int(s)] for s, _, _ in atoms],
        "weights": [fr(w) for _, _, w in atoms],
        "K": 2,
        "labels_before": [b for _, b, _ in atoms],
        "labels_after_or_optimum": None,
        "poi_indices": [0],
        "nuisance_indices": [],
        "objective_before": "eta = 0",
        "objective_after": None,
        "exact_quantities": {
            "cell_probabilities": [fr(x) for x in law["p"]],
            "cell_means": [fr(x) for x in law["c"]],
            "v": fr(law["v"]),
            "eta": fr(law["eta"]),
            "psi_values": [fr(x) for x in law["psi"]],
            "sigma2": fr(law["sigma2"]),
            "atoms_in_cell_0": 4,
        },
        "verification": {
            "method": "exact_formula",
            "notes": (
                "Every cell mean is zero, so eta = 0 and psi(s, b) = ((1 - 0) s^2 - (s - 0)^2)/v = 0 "
                "for every s: the root equation (s - c_b)^2 = (1 - eta) s^2 is the identity at eta = 0 "
                "and has no two-atom restriction. Cell 0 carries four atoms. The same holds for any "
                "atomless S with a partition whose cells all have conditional mean zero (e.g. cells "
                "symmetric about 0), see AUDITS/artifacts/AUDIT-SCORE-ORACLE-ROBUSTNESS-001/coverage.json "
                "law atomless_eta_zero. Correct statement: for 0 < eta <= 1 the support is at most two "
                "atoms per cell; for eta = 0 every law has sigma^2 = 0; (A4) is automatic iff eta > 0 "
                "and some positive-probability cell is atomless."
            ),
        },
        "source": "AUDIT-SCORE-ORACLE-ROBUSTNESS",
        "date": "2026-09-05",
    }
    path = RESEARCH / "COUNTEREXAMPLES" / f"{FIXTURE_ID}.json"
    path.write_text(json.dumps(fixture, indent=2) + "\n")
    print(f"wrote {path.relative_to(ROOT)}")
    return {"provenance": provenance("fixtures", {"fixtures": [FIXTURE_ID]}), "fixture": fixture}


STAGES = {
    "exact": stage_exact,
    "popref": stage_popref,
    "coverage": stage_coverage,
    "fixtures": stage_fixtures,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stage", choices=[*STAGES, "all"])
    parser.add_argument("--replicates", type=int, default=4000)
    args = parser.parse_args()
    names = list(STAGES) if args.stage == "all" else [args.stage]
    for name in names:
        record = STAGES[name](args.replicates) if name == "coverage" else STAGES[name]()
        write_record(name, record)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
