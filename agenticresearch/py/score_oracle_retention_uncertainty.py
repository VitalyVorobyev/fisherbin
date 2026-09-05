"""Frozen-rule scalar retention uncertainty for SCORE-ORACLE-ROBUSTNESS (OP27 special case).

Instrument for KNOWN_RESULTS/10-oracle.md section O6. Conditional on one frozen
imperfect provider and quantizer from ``examples/door3_classifier.py`` (the
``n_per_class = 15`` ladder rung), it studies the ordinary plug-in ratio

    eta_hat = sum_b m_hat_b^2 / p_hat_b / v_hat,
    p_hat_b = #{Z=b}/n,  m_hat_b = mean(S 1{Z=b}),  v_hat = mean(S^2),

computed on an independent evaluation sample with *true* scalar scores S, and the
delta-method variance estimate built from the influence function

    psi = ((1 - eta) S^2 - (S - c_Z)^2) / v,   c_b = m_b / p_b.

Modes
-----
selftest   exact finite-sample identities on a small deterministic sample: the
           residual-sum-of-squares form of eta_hat, the closed-form influence
           function against Gateaux finite differences of the plug-in functional,
           the exact zero mean of psi_hat, and agreement with the public
           ``scorequant.information_report`` retention.
popref     population references for the frozen rule by controlled 1-D
           integration of the reference mixture: cell boundaries in x located by
           bisection, then composite Gauss-Legendre per piece for p_b, m_b, v,
           E[S], E[S^4], sigma^2 and the proxy-surrogate population value, on
           two independent routes (range, panel count, order). The reported
           integration error is their disagreement plus an analytic tail bound;
           the true score uses a tail-stable closed form checked against the
           example's exact provider.
coverage   one seeded Monte Carlo coverage experiment over independent evaluation
           samples: Wald intervals for eta at several n, studentized
           distribution, variance-estimate consistency, and the separation between
           evaluation uncertainty and the proxy-surrogate bias.

Nothing here is a proof. Artifacts under WORK/artifacts/SCORE-ORACLE-ROBUSTNESS/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.stats import norm

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scorequant as sq  # noqa: E402
from examples import door3_classifier as door3  # noqa: E402

SEED_BASE = 20260905
RUNG_INDEX = 0  # n_per_class = 15: the rung with the largest published proxy gap
N_PER_CLASS = door3.N_PER_CLASS_VALUES[RUNG_INDEX]
ARTIFACT_DIR = Path(__file__).resolve().parents[1] / "WORK" / "artifacts" / "SCORE-ORACLE-ROBUSTNESS"
Z_95 = float(norm.ppf(0.975))


def provenance(mode: str, params: dict) -> dict:
    script = Path(__file__).resolve()
    rev = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=script.parent,
        check=False,
    ).stdout.strip()
    return {
        "mode": mode,
        "params": params,
        "git_revision": rev,
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "scorequant": getattr(sq, "__version__", "unknown"),
    }


# ----------------------------------------------------------------------------
# The estimator and its influence function
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class PlugIn:
    eta: float
    sigma2: float
    v: float
    cell_means: np.ndarray
    counts: np.ndarray
    psi: np.ndarray

    @property
    def n_empty(self) -> int:
        return int(np.sum(self.counts == 0))


def plugin_retention(scores: np.ndarray, labels: np.ndarray, n_bins: int) -> PlugIn:
    """Plug-in eta_hat, its influence-function variance estimate, and the pieces.

    Empty cells contribute nothing (0/0 := 0), which is exactly what the
    residual-sum-of-squares identity gives.
    """
    s = np.asarray(scores, dtype=float).reshape(-1)
    z = np.asarray(labels).reshape(-1)
    n = s.shape[0]
    counts = np.bincount(z, minlength=n_bins).astype(float)
    sums = np.bincount(z, weights=s, minlength=n_bins)
    means = np.divide(sums, counts, out=np.zeros(n_bins), where=counts > 0)
    v = float(np.mean(s * s))
    between = float(np.sum(sums * means)) / n  # sum_b m_hat_b^2 / p_hat_b
    eta = between / v
    psi = ((1.0 - eta) * s * s - (s - means[z]) ** 2) / v
    sigma2 = float(np.mean(psi * psi))
    return PlugIn(eta, sigma2, v, means, counts, psi)


def weighted_functional(scores: np.ndarray, labels: np.ndarray, weights: np.ndarray, n_bins: int) -> float:
    """The same functional on a weighted empirical measure (for Gateaux differences)."""
    w = np.asarray(weights, dtype=float)
    w = w / w.sum()
    s = np.asarray(scores, dtype=float).reshape(-1)
    p = np.bincount(labels, weights=w, minlength=n_bins)
    m = np.bincount(labels, weights=w * s, minlength=n_bins)
    v = float(np.sum(w * s * s))
    between = float(np.sum(np.divide(m * m, p, out=np.zeros(n_bins), where=p > 0)))
    return between / v


def wald_interval(fit: PlugIn, n: int, z: float = Z_95) -> tuple[float, float]:
    half = z * math.sqrt(fit.sigma2 / n)
    return fit.eta - half, fit.eta + half


# ----------------------------------------------------------------------------
# Frozen rule
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class FrozenRule:
    provider: sq.DensityRatioScore
    oracle: sq.ScoreFunction
    result: sq.QuantizerResult
    n_bins: int

    def true_scores(self, x: np.ndarray) -> np.ndarray:
        return np.asarray(self.oracle.score(x))[:, 0]

    def proxy_scores(self, x: np.ndarray) -> np.ndarray:
        return np.asarray(self.provider.score(x))[:, 0]

    def labels(self, x: np.ndarray) -> np.ndarray:
        proxy = np.asarray(self.provider.score(x))
        return np.asarray(self.result.predict_scores(proxy)).astype(int)


def freeze_rule() -> tuple[FrozenRule, dict]:
    """Reproduce the door3 rung exactly as ``door3._run_rungs`` builds it."""
    model = door3.train_classifier(door3.CLASSIFIER_SEED_BASE + RUNG_INDEX, N_PER_CLASS)
    provider = door3.classifier_provider(
        model, description=f"logistic regression, {N_PER_CLASS} events per class"
    )
    train_observations = door3.draw_reference_mixture(door3.TRAIN_SEED, door3.N_TRAIN)
    result = sq.fit_quantizer(
        sq.ObservationSample(train_observations),
        provider=provider,
        n_bins=door3.N_BINS,
        criterion=sq.DOptimality(),
        config=sq.DExchangeConfig(seed=door3.SOLVER_SEED),
    )
    rule = FrozenRule(provider, door3.exact_provider(), result, door3.N_BINS)
    # Sanity anchor against the published ladder on door3's own test sample.
    test = door3.draw_reference_mixture(door3.TEST_SEED, door3.N_TEST)
    labels = rule.labels(test)
    anchor = {
        "n_per_class": int(N_PER_CLASS),
        "classifier_seed": int(door3.CLASSIFIER_SEED_BASE + RUNG_INDEX),
        "surrogate_retention_door3_test": float(
            result.evaluate_scores(np.asarray(provider.score(test))).geometric_mean_retention
        ),
        "true_retention_door3_test": float(
            sq.information_report(
                np.asarray(rule.oracle.score(test)), labels, n_bins=door3.N_BINS
            ).geometric_mean_retention
        ),
        "plugin_eta_door3_test": plugin_retention(rule.true_scores(test), labels, door3.N_BINS).eta,
        "information_kind": result.information_kind,
        "centers": np.asarray(result.centers).reshape(-1).tolist(),
    }
    return rule, anchor


# ----------------------------------------------------------------------------
# selftest
# ----------------------------------------------------------------------------


def run_selftest() -> dict:
    rng = np.random.default_rng(SEED_BASE)
    n, n_bins = 40, 4
    s = rng.standard_t(df=5, size=n) + 0.3 * rng.integers(0, 2, size=n)
    z = rng.integers(0, n_bins, size=n)
    z[z == 3] = 1  # leave one cell empty on purpose
    fit = plugin_retention(s, z, n_bins)

    rss = float(np.sum((s - fit.cell_means[z]) ** 2))
    identity_gap = abs(fit.eta - (1.0 - rss / float(np.sum(s * s))))
    psi_sum = abs(float(np.sum(fit.psi)))

    eps = 1e-6
    base = np.ones(n)
    fd = np.empty(n)
    for j in range(n):
        plus, minus = base.copy(), base.copy()
        # (1-eps) P_n + eps delta_j  <=>  weights (1-eps)/n + eps 1{j}
        plus *= (1 - eps) / n
        plus[j] += eps
        minus *= (1 + eps) / n
        minus[j] -= eps
        fd[j] = (
            weighted_functional(s, z, plus, n_bins) - weighted_functional(s, z, minus, n_bins)
        ) / (2 * eps)
    influence_gap = float(np.max(np.abs(fd - fit.psi)))

    library = float(sq.information_report(s[:, None], z, n_bins=n_bins).geometric_mean_retention)
    library_gap = abs(library - fit.eta)

    report = {
        "provenance": provenance("selftest", {"n": n, "n_bins": n_bins, "eps": eps}),
        "eta_hat": fit.eta,
        "sigma2_hat": fit.sigma2,
        "n_empty": fit.n_empty,
        "rss_identity_gap": identity_gap,
        "psi_sum_abs": psi_sum,
        "influence_vs_gateaux_fd_max_gap": influence_gap,
        "library_retention_gap": library_gap,
        "pass": bool(identity_gap < 1e-12 and psi_sum < 1e-10 and influence_gap < 1e-7 and library_gap < 1e-10),
    }
    return report


# ----------------------------------------------------------------------------
# popref
# ----------------------------------------------------------------------------


def reference_density(x: np.ndarray) -> np.ndarray:
    f_sig, f_bkg = door3.REFERENCE_FRACTIONS
    return f_sig * door3.signal_pdf(x) + f_bkg * door3.background_pdf(x)


def stable_true_score(x: np.ndarray) -> np.ndarray:
    """Closed-form mixture-fraction score, stable in both tails.

    Equals ``door3.exact_provider().score`` wherever the latter is finite:
    s = (phi_sig - phi_bkg) / (f_sig phi_sig + f_bkg phi_bkg), evaluated
    through log densities so the tails converge to -1/f_bkg instead of 0/0.
    """
    f_sig, f_bkg = door3.REFERENCE_FRACTIONS
    a = norm.logpdf(x, door3.SIGNAL_MU, door3.SIGNAL_SIGMA)
    b = norm.logpdf(x, door3.BACKGROUND_MU, door3.BACKGROUND_SIGMA)
    top = np.maximum(a, b)
    ea, eb = np.exp(a - top), np.exp(b - top)
    return (ea - eb) / (f_sig * ea + f_bkg * eb)


def locate_boundaries(rule: FrozenRule, lo: float, hi: float, n_grid: int) -> tuple[list[float], list[int]]:
    grid = np.linspace(lo, hi, n_grid)
    labels = rule.labels(grid[:, None])
    change = np.nonzero(labels[1:] != labels[:-1])[0]
    boundaries: list[float] = []
    for k in change:
        a, b = float(grid[k]), float(grid[k + 1])
        la = int(labels[k])
        for _ in range(60):
            mid = 0.5 * (a + b)
            if int(rule.labels(np.array([[mid]]))[0]) == la:
                a = mid
            else:
                b = mid
        boundaries.append(0.5 * (a + b))
    piece_labels = [int(labels[0])] + [int(labels[k + 1]) for k in change]
    return boundaries, piece_labels


def _gauss_legendre_route(
    rule: FrozenRule,
    boundaries: list[float],
    piece_labels: list[int],
    *,
    lo: float,
    hi: float,
    panels_per_piece: int,
    order: int,
) -> dict:
    """Composite Gauss-Legendre moments on [lo, hi], split at the cell boundaries.

    Every integrand is evaluated in one vectorized call per piece; the true
    score is the stable closed form, the proxy score the frozen provider.
    """
    n_bins = rule.n_bins
    nodes, weights = np.polynomial.legendre.leggauss(order)
    edges = [lo, *boundaries, hi]
    p = np.zeros(n_bins)
    m = np.zeros(n_bins)
    m_proxy = np.zeros(n_bins)
    v = v_proxy = mean_s = fourth = 0.0
    per_piece: list[tuple[int, np.ndarray, np.ndarray, np.ndarray]] = []
    label_mismatch = 0
    for lab, a, b in zip(piece_labels, edges[:-1], edges[1:], strict=True):
        panels = np.linspace(a, b, panels_per_piece + 1)
        half = 0.5 * (panels[1:] - panels[:-1])
        mid = 0.5 * (panels[1:] + panels[:-1])
        x = (half[:, None] * nodes[None, :] + mid[:, None]).reshape(-1)
        w = (half[:, None] * weights[None, :]).reshape(-1)
        fx = reference_density(x)
        sx = stable_true_score(x)
        sp = rule.proxy_scores(x[:, None])
        label_mismatch += int(np.sum(rule.labels(x[:, None]) != lab))
        wf = w * fx
        p[lab] += float(np.sum(wf))
        m[lab] += float(np.sum(wf * sx))
        m_proxy[lab] += float(np.sum(wf * sp))
        v += float(np.sum(wf * sx * sx))
        v_proxy += float(np.sum(wf * sp * sp))
        mean_s += float(np.sum(wf * sx))
        fourth += float(np.sum(wf * sx**4))
        per_piece.append((lab, wf, sx, sp))
    c = m / p
    eta = float(np.sum(m * m / p) / v)
    eta_proxy = float(np.sum(m_proxy * m_proxy / p) / v_proxy)
    sigma2 = 0.0
    for lab, wf, sx, _sp in per_piece:
        psi = ((1.0 - eta) * sx * sx - (sx - c[lab]) ** 2) / v
        sigma2 += float(np.sum(wf * psi * psi))
    return {
        "lo": lo,
        "hi": hi,
        "panels_per_piece": panels_per_piece,
        "order": order,
        "label_mismatch_nodes": label_mismatch,
        "p": p,
        "m": m,
        "m_proxy": m_proxy,
        "v": v,
        "v_proxy": v_proxy,
        "mean_s": mean_s,
        "fourth_moment": fourth,
        "eta": eta,
        "eta_proxy": eta_proxy,
        "sigma2": sigma2,
    }


def run_popref(rule: FrozenRule, *, lo: float = -14.0, hi: float = 14.0, n_grid: int = 400_001) -> dict:
    boundaries, piece_labels = locate_boundaries(rule, lo, hi, n_grid)

    # Stable closed-form score vs the example's own exact provider, where finite.
    probe = np.linspace(-8.0, 8.0, 4001)
    oracle_probe = rule.true_scores(probe[:, None])
    score_formula_gap = float(np.max(np.abs(oracle_probe - stable_true_score(probe))))

    route_a = _gauss_legendre_route(rule, boundaries, piece_labels, lo=lo, hi=hi, panels_per_piece=3000, order=24)
    route_b = _gauss_legendre_route(rule, boundaries, piece_labels, lo=lo - 4.0, hi=hi + 4.0, panels_per_piece=5000, order=16)
    cross_check = max(
        float(np.max(np.abs(route_a["p"] - route_b["p"]))),
        float(np.max(np.abs(route_a["m"] - route_b["m"]))),
        abs(route_a["v"] - route_b["v"]),
        abs(route_a["eta"] - route_b["eta"]),
        abs(route_a["sigma2"] - route_b["sigma2"]),
        abs(route_a["eta_proxy"] - route_b["eta_proxy"]),
    )
    # Mass beyond [lo, hi]; the true score is bounded by 1/min(f), so every
    # truncated moment integrand is bounded by this mass times a constant.
    f_sig, f_bkg = door3.REFERENCE_FRACTIONS
    tail_mass = float(
        f_sig * (norm.sf((hi - door3.SIGNAL_MU) / door3.SIGNAL_SIGMA) + norm.cdf((lo - door3.SIGNAL_MU) / door3.SIGNAL_SIGMA))
        + f_bkg * (norm.sf((hi - door3.BACKGROUND_MU) / door3.BACKGROUND_SIGMA) + norm.cdf((lo - door3.BACKGROUND_MU) / door3.BACKGROUND_SIGMA))
    )
    score_bound = 1.0 / min(f_sig, f_bkg)

    a = route_a
    return {
        "provenance": provenance("popref", {"lo": lo, "hi": hi, "n_grid": n_grid}),
        "boundaries_x": boundaries,
        "piece_labels": piece_labels,
        "p": a["p"].tolist(),
        "m": a["m"].tolist(),
        "cell_means": (a["m"] / a["p"]).tolist(),
        "v": a["v"],
        "mean_s": a["mean_s"],
        "fourth_moment": a["fourth_moment"],
        "eta": a["eta"],
        "sigma2": a["sigma2"],
        "sigma": math.sqrt(a["sigma2"]),
        "eta_proxy_population": a["eta_proxy"],
        "proxy_gap": a["eta_proxy"] - a["eta"],
        "integration_error": {
            "route_a": {k: a[k] for k in ("lo", "hi", "panels_per_piece", "order", "label_mismatch_nodes")},
            "route_b": {k: route_b[k] for k in ("lo", "hi", "panels_per_piece", "order", "label_mismatch_nodes")},
            "cross_check_max_abs_gap": cross_check,
            "truncated_tail_mass": tail_mass,
            "truncated_tail_moment_bound": tail_mass * score_bound**4,
            "score_formula_vs_oracle_max_gap": score_formula_gap,
            "note": "Two composite Gauss-Legendre routes with different ranges, panel counts and orders; the reported gap is their observed disagreement, not a rigorous bound. Tail mass outside [lo, hi] bounds the truncation of every moment up to order four via |S| <= 1/min(f).",
        },
    }


# ----------------------------------------------------------------------------
# coverage
# ----------------------------------------------------------------------------


def draw_reference(rng: np.random.Generator, n: int) -> np.ndarray:
    f_sig = door3.REFERENCE_FRACTIONS[0]
    is_signal = rng.random(n) < f_sig
    x = np.where(
        is_signal,
        rng.normal(door3.SIGNAL_MU, door3.SIGNAL_SIGMA, n),
        rng.normal(door3.BACKGROUND_MU, door3.BACKGROUND_SIGMA, n),
    )
    return x[:, None]


def _moments(values: np.ndarray) -> dict:
    v = np.asarray(values, dtype=float)
    mu = float(np.mean(v))
    sd = float(np.std(v, ddof=1))
    centred = (v - mu) / sd
    return {
        "mean": mu,
        "sd": sd,
        "skew": float(np.mean(centred**3)),
        "excess_kurtosis": float(np.mean(centred**4) - 3.0),
    }


def run_coverage(
    rule: FrozenRule,
    popref: dict,
    *,
    sizes: tuple[int, ...] = (100, 300, 1000, 3000),
    reps: int = 2000,
) -> dict:
    eta = float(popref["eta"])
    sigma = float(popref["sigma"])
    eta_proxy = float(popref["eta_proxy_population"])
    n_bins = rule.n_bins
    seeds = np.random.SeedSequence(SEED_BASE).spawn(len(sizes))
    rows = []
    for n, seed in zip(sizes, seeds, strict=True):
        rng = np.random.default_rng(seed)
        x = draw_reference(rng, reps * n)
        s = rule.true_scores(x).reshape(reps, n)
        s_proxy = rule.proxy_scores(x).reshape(reps, n)
        z = rule.labels(x).reshape(reps, n)
        eta_hat = np.empty(reps)
        sigma_hat = np.empty(reps)
        eta_proxy_hat = np.empty(reps)
        n_empty = np.zeros(reps, dtype=int)
        for r in range(reps):
            fit = plugin_retention(s[r], z[r], n_bins)
            eta_hat[r] = fit.eta
            sigma_hat[r] = math.sqrt(fit.sigma2)
            n_empty[r] = fit.n_empty
            eta_proxy_hat[r] = plugin_retention(s_proxy[r], z[r], n_bins).eta
        half = Z_95 * sigma_hat / math.sqrt(n)
        lower, upper = eta_hat - half, eta_hat + half
        covers = (lower <= eta) & (eta <= upper)
        covers_proxy = (lower <= eta_proxy) & (eta_proxy <= upper)
        t = (eta_hat - eta) / (sigma_hat / math.sqrt(n))
        oracle_t = (eta_hat - eta) / (sigma / math.sqrt(n))
        cov = float(np.mean(covers))
        rows.append(
            {
                "n": int(n),
                "reps": int(reps),
                "seed_entropy": int(seed.entropy) if isinstance(seed.entropy, int) else str(seed.entropy),
                "coverage_95": cov,
                "coverage_se": math.sqrt(cov * (1 - cov) / reps),
                "covers_proxy_population_value": float(np.mean(covers_proxy)),
                "interval_leaves_unit": float(np.mean((lower < 0) | (upper > 1))),
                "any_empty_cell": float(np.mean(n_empty > 0)),
                "eta_hat": _moments(eta_hat),
                "eta_hat_bias_times_n": float(n * (np.mean(eta_hat) - eta)),
                "sd_eta_hat_vs_sigma_over_sqrt_n": {
                    "empirical_sd": float(np.std(eta_hat, ddof=1)),
                    "population_sigma_over_sqrt_n": sigma / math.sqrt(n),
                    "mean_sigma_hat_over_sqrt_n": float(np.mean(sigma_hat)) / math.sqrt(n),
                },
                "sigma_hat_relative_rmse": float(np.sqrt(np.mean((sigma_hat / sigma - 1.0) ** 2))),
                "studentized": _moments(t),
                "oracle_studentized": _moments(oracle_t),
                "studentized_abs_gt_z95": float(np.mean(np.abs(t) > Z_95)),
                "eta_proxy_hat_mean": float(np.mean(eta_proxy_hat)),
            }
        )
    return {
        "provenance": provenance("coverage", {"sizes": list(sizes), "reps": reps, "seed_base": SEED_BASE}),
        "population": {"eta": eta, "sigma": sigma, "eta_proxy": eta_proxy},
        "rows": rows,
    }


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------


def _dump(name: str, payload: dict) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["selftest", "popref", "coverage", "all"])
    parser.add_argument("--reps", type=int, default=2000)
    parser.add_argument("--sizes", type=int, nargs="+", default=[100, 300, 1000, 3000])
    args = parser.parse_args(argv)

    summary: dict = {}
    if args.mode in ("selftest", "all"):
        report = run_selftest()
        _dump("selftest", report)
        summary["selftest"] = {k: v for k, v in report.items() if k != "provenance"}
        print("selftest:", json.dumps(summary["selftest"], indent=1))
        if not report["pass"]:
            return 1
    if args.mode in ("popref", "coverage", "all"):
        rule, anchor = freeze_rule()
        print("frozen rule anchor:", json.dumps(anchor, indent=1))
        if args.mode == "coverage":
            popref = json.loads((ARTIFACT_DIR / "popref.json").read_text())
        else:
            popref = run_popref(rule)
            popref["anchor"] = anchor
            _dump("popref", popref)
            summary["popref"] = {k: v for k, v in popref.items() if k not in ("provenance", "anchor")}
            print("popref:", json.dumps(summary["popref"], indent=1))
        if args.mode in ("coverage", "all"):
            cov = run_coverage(rule, popref, sizes=tuple(args.sizes), reps=args.reps)
            _dump("coverage", cov)
            summary["coverage"] = cov["rows"]
            for row in cov["rows"]:
                print(
                    f"n={row['n']:5d} coverage={row['coverage_95']:.4f}±{row['coverage_se']:.4f} "
                    f"covers_proxy={row['covers_proxy_population_value']:.3f} "
                    f"sd={row['sd_eta_hat_vs_sigma_over_sqrt_n']['empirical_sd']:.5f} "
                    f"sigma/sqrt(n)={row['sd_eta_hat_vs_sigma_over_sqrt_n']['population_sigma_over_sqrt_n']:.5f} "
                    f"mean sigma_hat/sqrt(n)={row['sd_eta_hat_vs_sigma_over_sqrt_n']['mean_sigma_hat_over_sqrt_n']:.5f} "
                    f"t: mean={row['studentized']['mean']:+.3f} sd={row['studentized']['sd']:.3f} "
                    f"skew={row['studentized']['skew']:+.3f} empty={row['any_empty_cell']:.3f}"
                )
    if args.mode == "all":
        summary["provenance"] = provenance("all", {"reps": args.reps, "sizes": args.sizes})
        _dump("summary", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
