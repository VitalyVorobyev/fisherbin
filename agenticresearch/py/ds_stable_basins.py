"""Population fixed points and inhabitation numerics for DS-STABLE-BASINS (OP30).

Decides, numerically and before any proof is trusted, the population side of the
inhabitation question: which laws admit self-consistent efficient-Voronoi strip
rules with nondegenerate nuisance blocks (the DS14 limit objects of
margin-certified exchange-stable sequences), and which cannot.

Modes
-----
selftest   exact 8-atom sign-split rationals, popref anchor for the scalar
           Lloyd reference, and a Gauss-Legendre cross-check of the closed-form
           strip moments through the public ``scorequant.IntegrationSource``.
popfix     Gaussian residual/rank scans (the LCM obstruction's finite face:
           the fixed-point residual r(beta) is zero-free and I_q(beta) is
           rank one for every tilt), the Moebius iteration orbit, and the full
           (beta, cuts) self-consistency search on non-LCM candidate laws
           (product bimodal-nuisance sweep, mix3).
signsplit  the merged-variant escape on the canonical Gaussian: the v-family of
           nuisance-split stationary configurations, its exact value 2/pi and
           nuisance block, and the coincident projected centroids.
hessian    second-order behavior of the population value at found non-LCM fixed
           points (rule-family Hessian and relocation-margin profile).
geometry   classify recorded finite stable states (DS16 ascent terminals and
           the margin-retaining witness) against the strip picture.
library    seeded public-API ascent on the candidate law and the Gaussian
           control (fixed-point seeding vs documented seeds).

All population arithmetic is closed-form Gaussian-mixture algebra (Phi/phi via
scipy.stats.norm); no sampling enters a population quantity. Monte Carlo
appears only in the explicitly-labeled violation scans and library runs, with
deterministic seeds. Artifacts under WORK/artifacts/DS-STABLE-BASINS/.
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
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.stats import norm

SEED_BASE = 20260831
ARTIFACT_DIR = Path(__file__).resolve().parents[1] / "WORK" / "artifacts" / "DS-STABLE-BASINS"


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
    }


# ----------------------------------------------------------------------------
# Gaussian-mixture laws and closed-form strip moments.
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class MixtureLaw:
    """Centered planar Gaussian mixture: weights, means, covariances."""

    name: str
    weights: tuple[float, ...]
    means: tuple[tuple[float, float], ...]
    covs: tuple[tuple[tuple[float, float], tuple[float, float]], ...]

    def __post_init__(self) -> None:
        mean = np.einsum("j,jd->d", np.array(self.weights), np.array(self.means))
        if not np.allclose(mean, 0.0, atol=1e-12):
            raise ValueError(f"law {self.name} is not centered: mean={mean}")

    @property
    def full_info(self) -> np.ndarray:
        info = np.zeros((2, 2))
        for pi, mu, cov in zip(self.weights, self.means, self.covs, strict=True):
            mu_v = np.array(mu)
            info += pi * (np.array(cov) + np.outer(mu_v, mu_v))
        return info

    @property
    def b_star_pop(self) -> float:
        info = self.full_info
        return info[0, 1] / info[1, 1]


def gaussian_law(a: float, c: float, d: float, name: str | None = None) -> MixtureLaw:
    return MixtureLaw(
        name or f"gauss(a={a},c={c},d={d})",
        (1.0,),
        ((0.0, 0.0),),
        (((a, c), (c, d)),),
    )


def bimodal_law(m: float, s: float) -> MixtureLaw:
    """S_psi ~ N(0,1) independent of S_lam ~ (1/2)N(-m,s^2)+(1/2)N(m,s^2)."""
    cov = ((1.0, 0.0), (0.0, s * s))
    return MixtureLaw(f"bimodal(m={m},s={s})", (0.5, 0.5), ((0.0, -m), (0.0, m)), (cov, cov))


def xcorr_law(c: float) -> MixtureLaw:
    """Dependent class-(L) law: equal mixture of +-c correlated standard Gaussians.

    E[S_lam | S_psi] = 0 by the branch symmetry (so (L) holds and shat = S_psi ~ N(0,1)),
    but conditional means along a tilt are nonlinear: LCM fails for beta != 0.
    """
    return MixtureLaw(
        f"xcorr(c={c})",
        (0.5, 0.5),
        ((0.0, 0.0), (0.0, 0.0)),
        (((1.0, c), (c, 1.0)), ((1.0, -c), (-c, 1.0))),
    )


def mix3_law() -> MixtureLaw:
    cov = ((0.25, 0.0), (0.0, 0.25))
    return MixtureLaw(
        "mix3",
        (1 / 3, 1 / 3, 1 / 3),
        ((-2.0, 1.0), (0.0, -2.0), (2.0, 1.0)),
        (cov, cov, cov),
    )


def strip_moments(
    law: MixtureLaw, beta: float, cuts: list[float]
) -> tuple[np.ndarray, np.ndarray]:
    """Exact masses W_b and moments m_b = E[S 1{T in cell}] for T = S_psi - beta S_lam.

    Cells are the K = len(cuts)+1 intervals of T at the given cut points.
    Per mixture component, (S, T) is jointly Gaussian, so every cell moment is
    a Phi/phi expression; no quadrature or sampling is involved.
    """
    w = np.array([1.0, -beta])
    edges = np.concatenate([[-np.inf], np.asarray(cuts, dtype=float), [np.inf]])
    k = len(edges) - 1
    masses = np.zeros(k)
    moments = np.zeros((k, 2))
    for pi, mu, cov in zip(law.weights, law.means, law.covs, strict=True):
        mu_v = np.array(mu)
        cov_m = np.array(cov)
        nu = float(w @ mu_v)
        tau = math.sqrt(float(w @ cov_m @ w))
        cov_st = cov_m @ w  # Cov(S, T) within the component
        alpha = (edges - nu) / tau
        cdf = norm.cdf(alpha)
        pdf = norm.pdf(alpha)
        for b in range(k):
            prob = cdf[b + 1] - cdf[b]
            masses[b] += pi * prob
            moments[b] += pi * (mu_v * prob + cov_st * (pdf[b] - pdf[b + 1]) / tau)
    return masses, moments


def binned_info(masses: np.ndarray, moments: np.ndarray) -> np.ndarray:
    info = np.zeros((2, 2))
    for w_b, m_b in zip(masses, moments, strict=True):
        if w_b > 0:
            info += np.outer(m_b, m_b) / w_b
    return info


def profiled_value(info: np.ndarray, tol: float = 1e-13) -> tuple[float, bool]:
    """DS11 pseudo-inverse profiled value and a nuisance-degeneracy flag."""
    if info[1, 1] > tol:
        return float(info[0, 0] - info[0, 1] ** 2 / info[1, 1]), False
    return float(info[0, 0]), True


def rule_quantities(law: MixtureLaw, beta: float, cuts: list[float]) -> dict:
    masses, moments = strip_moments(law, beta, cuts)
    info = binned_info(masses, moments)
    value, degenerate = profiled_value(info)
    with np.errstate(divide="ignore", invalid="ignore"):
        centroids = moments / masses[:, None]
    b_star = float(info[0, 1] / info[1, 1]) if info[1, 1] > 1e-13 else float("nan")
    proj = centroids[:, 0] - b_star * centroids[:, 1] if not math.isnan(b_star) else None
    sep = (
        float(min(abs(proj[x] - proj[y]) for x in range(len(proj)) for y in range(x + 1, len(proj))))
        if proj is not None
        else float("nan")
    )
    eigs = np.linalg.eigvalsh(info)
    return {
        "masses": masses,
        "moments": moments,
        "centroids": centroids,
        "info": info,
        "value": value,
        "degenerate": degenerate,
        "b_star": b_star,
        "projected": proj,
        "proj_sep": sep,
        "lambda_min": float(eigs[0]),
        "i11": float(info[1, 1]),
    }


# ----------------------------------------------------------------------------
# Scalar mixture Lloyd reference (v_K of the efficient-score marginal).
# ----------------------------------------------------------------------------


def scalar_components(law: MixtureLaw, direction: np.ndarray) -> list[tuple[float, float, float]]:
    comps = []
    for pi, mu, cov in zip(law.weights, law.means, law.covs, strict=True):
        nu = float(direction @ np.array(mu))
        tau = math.sqrt(float(direction @ np.array(cov) @ direction))
        comps.append((pi, nu, tau))
    return comps


def scalar_cell(comps, lo: float, hi: float) -> tuple[float, float]:
    """Mass and first moment of the scalar mixture on (lo, hi]."""
    mass = 0.0
    first = 0.0
    for pi, nu, tau in comps:
        a_lo = (lo - nu) / tau
        a_hi = (hi - nu) / tau
        prob = norm.cdf(a_hi) - norm.cdf(a_lo)
        mass += pi * prob
        first += pi * (nu * prob + tau * (norm.pdf(a_lo) - norm.pdf(a_hi)))
    return mass, first


def lloyd_stationary_points(
    comps,
    k: int,
    n_init: int = 24,
    iters: int = 20000,
    atol: float = 1e-13,
    extra_inits: list[list[float]] | None = None,
) -> list[dict]:
    """All distinct Lloyd-stationary K-interval quantizers of a scalar mixture found
    from deterministic multi-start (centroid-midpoint fixed points, not only optima)."""
    spread = max(abs(nu) + 3 * tau for _, nu, tau in comps)
    inits: list[np.ndarray] = [np.linspace(-spread / 2, spread / 2, k - 1)]
    for init in range(1, n_init):
        rng = np.random.default_rng(SEED_BASE + init)
        inits.append(np.sort(rng.uniform(-spread, spread, size=k - 1)))
    for extra in extra_inits or []:
        inits.append(np.sort(np.asarray(extra, dtype=float)))
    found: list[dict] = []
    for edges in inits:
        alive = True
        for _ in range(iters):
            full = np.concatenate([[-np.inf], edges, [np.inf]])
            cells = [scalar_cell(comps, full[b], full[b + 1]) for b in range(k)]
            if any(mass <= 1e-12 for mass, _ in cells):
                alive = False
                break
            centroids = np.array([first / mass for mass, first in cells])
            new_edges = 0.5 * (centroids[:-1] + centroids[1:])
            done = np.allclose(new_edges, edges, rtol=0, atol=atol)
            edges = new_edges
            if done:
                break
        if not alive:
            continue
        full = np.concatenate([[-np.inf], edges, [np.inf]])
        cells = [scalar_cell(comps, full[b], full[b + 1]) for b in range(k)]
        if any(mass <= 1e-12 for mass, _ in cells):
            continue
        masses = np.array([mass for mass, _ in cells])
        centroids = np.array([first / mass for mass, first in cells])
        record = {
            "edges": edges.tolist(),
            "masses": masses.tolist(),
            "centroids": centroids.tolist(),
            "value": float(np.sum(masses * centroids**2)),
        }
        if all(np.max(np.abs(np.array(record["edges"]) - np.array(r["edges"]))) > 1e-7 for r in found):
            found.append(record)
    if not found:
        raise RuntimeError("scalar Lloyd failed on every start")
    return found


def scalar_lloyd(comps, k: int, n_init: int = 5, iters: int = 20000, atol: float = 1e-13) -> dict:
    """Best K-interval quantizer of a scalar centered Gaussian mixture (Lloyd, multi-start)."""
    points = lloyd_stationary_points(comps, k, n_init=n_init, iters=iters, atol=atol)
    return max(points, key=lambda r: r["value"])


def efficient_interval_value(law: MixtureLaw, k: int) -> dict:
    """v_K of law(shat), shat = S_psi - B*_pop S_lam."""
    direction = np.array([1.0, -law.b_star_pop])
    return scalar_lloyd(scalar_components(law, direction), k)


# ----------------------------------------------------------------------------
# Self-consistency search and diagnostics.
# ----------------------------------------------------------------------------


def selfconsistency_iterate(
    law: MixtureLaw,
    beta0: float,
    cuts0: list[float],
    iters: int = 4000,
    damping: float = 0.5,
    tol: float = 1e-12,
) -> dict:
    """Iterate beta <- B*(I_q), cuts <- projected-centroid midpoints; report the terminal."""
    beta = float(beta0)
    cuts = np.array(sorted(cuts0), dtype=float)
    status = "running"
    residual = float("inf")
    quants: dict = {}
    for _ in range(iters):
        quants = rule_quantities(law, beta, list(cuts))
        if np.any(quants["masses"] < 1e-10):
            status = "cell_death"
            break
        if quants["i11"] < 1e-12:
            status = "nuisance_degenerate"
            break
        beta_new = quants["b_star"]
        # Project with the CURRENT tilt: then e_b = E[T_beta | cell] exactly, so the
        # midpoint update is scalar Lloyd in T_beta and coincidence means merged cells.
        proj = np.sort(quants["centroids"][:, 0] - beta * quants["centroids"][:, 1])
        if np.min(np.diff(proj)) < 1e-10:
            status = "coincident_projected_centroids"
            break
        cuts_new = 0.5 * (proj[:-1] + proj[1:])
        residual = max(abs(beta_new - beta), float(np.max(np.abs(cuts_new - cuts))))
        beta = beta + damping * (beta_new - beta)
        cuts = cuts + damping * (cuts_new - cuts)
        if residual < tol:
            status = "fixed_point"
            break
    if status == "running":
        status = "no_convergence"
    return {
        "law": law.name,
        "status": status,
        "beta": float(beta),
        "cuts": [float(x) for x in cuts],
        "residual": float(residual),
        "value": quants.get("value"),
        "i11": quants.get("i11"),
        "lambda_min": quants.get("lambda_min"),
        "proj_sep": quants.get("proj_sep"),
        "min_mass": float(np.min(quants["masses"])) if "masses" in quants else None,
    }


def sample_mixture(law: MixtureLaw, n: int, rng: np.random.Generator) -> np.ndarray:
    comp = rng.choice(len(law.weights), p=np.array(law.weights), size=n)
    out = np.empty((n, 2))
    for j, (mu, cov) in enumerate(zip(law.means, law.covs, strict=True)):
        mask = comp == j
        if mask.any():
            out[mask] = rng.multivariate_normal(np.array(mu), np.array(cov), size=int(mask.sum()))
    return out


def violation_scan(
    law: MixtureLaw, beta: float, cuts: list[float], n: int = 200000, seed: int = SEED_BASE
) -> dict:
    """Monte Carlo mass of first-variation violations of the strip rule (diagnostic only)."""
    quants = rule_quantities(law, beta, cuts)
    if math.isnan(quants["b_star"]):
        return {"violated_mass": float("nan"), "note": "nuisance-degenerate rule"}
    rng = np.random.default_rng(seed)
    pts = sample_mixture(law, n, rng)
    t_val = pts[:, 0] - beta * pts[:, 1]
    strip_cell = np.searchsorted(np.asarray(cuts), t_val, side="right")
    e_val = pts[:, 0] - quants["b_star"] * pts[:, 1]
    nearest = np.argmin(np.abs(e_val[:, None] - quants["projected"][None, :]), axis=1)
    violated = float(np.mean(strip_cell != nearest))
    return {"violated_mass": violated, "n": n, "seed": seed}


# ----------------------------------------------------------------------------
# Mode: selftest.
# ----------------------------------------------------------------------------


def signsplit_eight_atom_exact() -> dict:
    """K=3 sign-split on the CE-DS-POP-WASTED-CELLS-001 8-atom law, exact rationals."""
    atoms = [(-3, 1), (-3, -1), (-1, 2), (-1, -2), (1, 1), (1, -1), (3, 2), (3, -2)]
    w = Fraction(1, 8)
    labels = [0 if (s < 0 and t > 0) else 1 if (s < 0 and t <= 0) else 2 for s, t in atoms]
    masses = [Fraction(0)] * 3
    moments = [[Fraction(0), Fraction(0)] for _ in range(3)]
    for (s, t), lab in zip(atoms, labels, strict=True):
        masses[lab] += w
        moments[lab][0] += w * s
        moments[lab][1] += w * t
    info = [[Fraction(0)] * 2 for _ in range(2)]
    for b in range(3):
        for i in range(2):
            for j in range(2):
                info[i][j] += moments[b][i] * moments[b][j] / masses[b]
    value = info[0][0] - info[0][1] * info[1][0] / info[1][1]
    slope = info[0][1] / info[1][1]
    projected = [moments[b][0] / masses[b] - slope * moments[b][1] / masses[b] for b in range(3)]
    return {
        "labels": labels,
        "masses": [str(x) for x in masses],
        "info": [[str(info[i][j]) for j in range(2)] for i in range(2)],
        "profiled_value": str(value),
        "nuisance_block": str(info[1][1]),
        "cross_block": str(info[0][1]),
        "projected_centroids": [str(p) for p in projected],
    }


def run_selftest() -> dict:
    failures = []

    # 1) Exact 8-atom K=3 sign-split: I_q = diag(4, 9/8), coincident e-pair.
    exact = signsplit_eight_atom_exact()
    if exact["info"] != [["4", "0"], ["0", "9/8"]]:
        failures.append(f"eight-atom info mismatch: {exact['info']}")
    if exact["profiled_value"] != "4":
        failures.append(f"eight-atom profiled value: {exact['profiled_value']}")
    if exact["projected_centroids"] != ["-2", "-2", "2"]:
        failures.append(f"eight-atom projected centroids: {exact['projected_centroids']}")

    # 2) Scalar Lloyd anchor: N(0,1), K=3 has cuts +-0.612003 and value 1 - W_3 = 0.809826.
    ref = scalar_lloyd([(1.0, 0.0, 1.0)], 3)
    if abs(ref["value"] - 0.809826) > 2e-5 or abs(abs(ref["edges"][0]) - 0.612003) > 1e-5:
        failures.append(f"scalar Lloyd anchor off: {ref}")

    # 3) Strip moments on N(0, I2) at beta=0: interval masses/moments of N(0,1).
    law = gaussian_law(1.0, 0.0, 1.0, name="gauss_iid")
    masses, moments = strip_moments(law, 0.0, ref["edges"])
    if not np.allclose(masses, ref["masses"], atol=1e-12):
        failures.append("beta=0 strip masses disagree with scalar reference")
    if not np.allclose(moments[:, 0] / masses, ref["centroids"], atol=1e-10):
        failures.append("beta=0 strip centroids disagree with scalar reference")
    if not np.allclose(moments[:, 1], 0.0, atol=1e-12):
        failures.append("beta=0 nuisance moments must vanish on the product law")

    # 4) Gauss-Legendre cross-check of strip moments via the public library.
    from scorequant import GaussLegendreConfig, IntegrationSource

    blaw = bimodal_law(1.5, 0.4)
    beta, cuts = 0.7, [-0.9, 0.8]

    def density(points: np.ndarray) -> np.ndarray:
        out = np.zeros(points.shape[0])
        for pi, mu, cov in zip(blaw.weights, blaw.means, blaw.covs, strict=True):
            diff = points - np.array(mu)
            inv = np.linalg.inv(np.array(cov))
            det = np.linalg.det(np.array(cov))
            expo = -0.5 * np.einsum("nd,de,ne->n", diff, inv, diff)
            out += pi * np.exp(expo) / (2 * math.pi * math.sqrt(det))
        return out

    # Integrate each cell over its own box in the rotated (T, s_lam) coordinates
    # (unit Jacobian; the strip indicator becomes a box, so the integrand is smooth).
    edges_t = [-14.0, *cuts, 14.0]
    lam_lo, lam_hi = -10.0, 10.0
    masses_q = np.zeros(3)
    moments_q = np.zeros((3, 2))
    for b in range(3):

        def rotated_density(points: np.ndarray) -> np.ndarray:
            s = np.stack([points[:, 0] + beta * points[:, 1], points[:, 1]], axis=1)
            return density(s)

        box = np.array([[edges_t[b], edges_t[b + 1]], [lam_lo, lam_hi]])
        sample = IntegrationSource(
            box, density=rotated_density, quadrature=GaussLegendreConfig(order=120, max_points=20000)
        ).materialize()
        pts_rot = np.asarray(sample.observations, dtype=float)
        wts = np.asarray(sample.weights, dtype=float)
        pts = np.stack([pts_rot[:, 0] + beta * pts_rot[:, 1], pts_rot[:, 1]], axis=1)
        masses_q[b] = wts.sum()
        moments_q[b] = (wts[:, None] * pts).sum(axis=0)
    masses_c, moments_c = strip_moments(blaw, beta, cuts)
    if not np.allclose(masses_q, masses_c, atol=1e-9):
        failures.append(f"GL mass cross-check: {masses_q} vs {masses_c}")
    if not np.allclose(moments_q, moments_c, atol=1e-8):
        failures.append(f"GL moment cross-check: {moments_q} vs {moments_c}")

    result = "PASS" if not failures else "FAIL"
    print(f"[selftest] {result}" + (f" failures={failures}" if failures else ""), flush=True)
    return {"result": result, "failures": failures, "eight_atom": exact}


# ----------------------------------------------------------------------------
# Mode: popfix.
# ----------------------------------------------------------------------------


def gaussian_residual_scan(a: float, c: float, d: float, n_beta: int = 241) -> dict:
    """Fixed-point residual, rank, and value along the tilt for a Gaussian law."""
    law = gaussian_law(a, c, d)
    ref = efficient_interval_value(law, 3)
    betas = np.linspace(-6.0, 6.0, n_beta)
    rows = []
    max_lambda_min = 0.0
    zero_crossings = 0
    prev_r = None
    prev_denom = None
    for beta in betas:
        comps = scalar_components(law, np.array([1.0, -beta]))
        lloyd = scalar_lloyd(comps, 3, n_init=1)
        quants = rule_quantities(law, float(beta), lloyd["edges"])
        denom = c - beta * d
        r_analytic = beta - (a - beta * c) / denom if abs(denom) > 1e-12 else float("nan")
        r_numeric = beta - quants["b_star"] if not math.isnan(quants["b_star"]) else float("nan")
        # A sign flip across the pole of the Moebius map is not a root: require the
        # denominator to keep its sign between neighboring grid points.
        if (
            prev_r is not None
            and prev_denom is not None
            and not math.isnan(r_numeric)
            and prev_r * r_numeric < 0
            and prev_denom * denom > 0
        ):
            zero_crossings += 1
        prev_r = r_numeric if not math.isnan(r_numeric) else None
        prev_denom = denom
        max_lambda_min = max(max_lambda_min, quants["lambda_min"])
        rows.append(
            {
                "beta": float(beta),
                "residual_numeric": r_numeric,
                "residual_analytic": r_analytic,
                "lambda_min": quants["lambda_min"],
                "i11": quants["i11"],
                "value": quants["value"],
            }
        )
    discriminant = 4 * (c * c - a * d)
    return {
        "law": law.name,
        "v3_efficient": ref["value"],
        "discriminant": discriminant,
        "max_lambda_min_over_tilts": max_lambda_min,
        "residual_zero_crossings": zero_crossings,
        "rows": rows,
    }


def moebius_orbit(a: float, c: float, d: float, beta0: float, steps: int = 200) -> dict:
    orbit = [beta0]
    beta = beta0
    for _ in range(steps):
        denom = c - beta * d
        if abs(denom) < 1e-14:
            break
        beta = (a - beta * c) / denom
        orbit.append(beta)
        if abs(beta) > 1e12:
            break
    return {
        "beta0": beta0,
        "steps": len(orbit) - 1,
        "converged": bool(len(orbit) > 2 and abs(orbit[-1] - orbit[-2]) < 1e-10),
        "tail": orbit[-6:],
    }


def tilt_branches(law: MixtureLaw, beta: float, guides: list[list[float]] | None = None) -> list[dict]:
    """Every Lloyd-stationary K=3 interval quantizer of law(T_beta), with its B* residual.

    A self-consistent strip rule is exactly a pair (beta, stationary cuts) with
    B*(I_q) = beta: at such a pair the projected centroids equal the T-cell means,
    so the companion nearest-centroid cuts are the Lloyd midpoints automatically.
    """
    comps = scalar_components(law, np.array([1.0, -beta]))
    branches = lloyd_stationary_points(comps, 3, extra_inits=guides)
    out = []
    for br in branches:
        quants = rule_quantities(law, beta, br["edges"])
        residual = (
            quants["b_star"] - beta if not math.isnan(quants["b_star"]) else float("nan")
        )
        out.append({"edges": br["edges"], "residual": residual, "quants": quants})
    return out


def _nearest_branch(branches: list[dict], guide: list[float]) -> dict | None:
    finite = [b for b in branches if not math.isnan(b["residual"])]
    if not finite:
        return None
    return min(finite, key=lambda b: max(abs(x - y) for x, y in zip(b["edges"], guide, strict=True)))


def _edge_dist(edges: list[float], guide: list[float]) -> float:
    return max(abs(x - y) for x, y in zip(edges, guide, strict=True))


def _bisect_branch(law: MixtureLaw, b_lo: float, b_hi: float, guide: list[float]) -> dict | None:
    lo_branch = _nearest_branch(tilt_branches(law, b_lo, [guide]), guide)
    if lo_branch is None:
        return None
    r_lo = lo_branch["residual"]
    guide = lo_branch["edges"]
    mid = 0.5 * (b_lo + b_hi)
    branch = None
    for _ in range(60):
        mid = 0.5 * (b_lo + b_hi)
        branch = _nearest_branch(tilt_branches(law, mid, [guide]), guide)
        if branch is None or _edge_dist(branch["edges"], guide) > 1.0:
            return None
        guide = branch["edges"]
        if branch["residual"] * r_lo > 0:
            b_lo, r_lo = mid, branch["residual"]
        else:
            b_hi = mid
        if b_hi - b_lo < 1e-13:
            break
    if branch is None or abs(branch["residual"]) > 1e-6:
        return None
    quants = branch["quants"]
    return {
        "beta": mid,
        "cuts": branch["edges"],
        "value": quants["value"],
        "i11": quants["i11"],
        "lambda_min": quants["lambda_min"],
        "proj_sep": quants["proj_sep"],
        "min_mass": float(np.min(quants["masses"])),
        "residual": branch["residual"],
        "rank_one": bool(quants["lambda_min"] < 1e-8),
    }


def selfconsistent_roots(
    law: MixtureLaw, beta_lo: float = -2.5, beta_hi: float = 2.5, n_grid: int = 101
) -> dict:
    """Scan the tilt for all self-consistent strip rules via branch-tracked sign changes."""
    ref = efficient_interval_value(law, 3)
    grid = np.linspace(beta_lo, beta_hi, n_grid)
    prev_beta: float | None = None
    prev_branches: list[dict] = []
    roots: list[dict] = []
    n_branches_seen = 0
    for beta in grid:
        guides = [b["edges"] for b in prev_branches]
        branches = tilt_branches(law, float(beta), guides or None)
        n_branches_seen = max(n_branches_seen, len(branches))
        if prev_beta is not None:
            for pb in prev_branches:
                if math.isnan(pb["residual"]):
                    continue
                cb = _nearest_branch(branches, pb["edges"])
                if cb is None or _edge_dist(cb["edges"], pb["edges"]) > 1.0:
                    continue
                if pb["residual"] * cb["residual"] < 0:
                    root = _bisect_branch(law, prev_beta, float(beta), pb["edges"])
                    if root is not None and all(
                        abs(root["beta"] - r["beta"]) > 1e-6
                        or _edge_dist(root["cuts"], r["cuts"]) > 1e-6
                        for r in roots
                    ):
                        root["violated_mass"] = violation_scan(law, root["beta"], root["cuts"])[
                            "violated_mass"
                        ]
                        root["price"] = ref["value"] - root["value"]
                        roots.append(root)
        prev_beta = float(beta)
        prev_branches = branches
    nondegenerate = [r for r in roots if not r["rank_one"]]
    best = max(nondegenerate, key=lambda r: r["value"]) if nondegenerate else None
    label = f"beta={best['beta']:.4f} lam_min={best['lambda_min']:.4f}" if best else "none"
    print(
        f"[popfix] {law.name}: {len(roots)} self-consistent roots "
        f"({len(nondegenerate)} rank-2); best nondegenerate {label}",
        flush=True,
    )
    return {
        "law": law.name,
        "v3_efficient": ref["value"],
        "roots": roots,
        "fixed_point": best,
        "max_branches_per_tilt": n_branches_seen,
    }


def run_popfix() -> dict:
    gauss = []
    for a, c, d in ((1.0, 0.0, 1.0), (1.0, 0.6, 1.0), (1.0, 0.9, 1.0), (2.0, 0.5, 0.75)):
        scan = gaussian_residual_scan(a, c, d)
        summary = {k: scan[k] for k in scan if k != "rows"}
        print(
            f"[popfix] {scan['law']}: max lambda_min over tilts "
            f"{scan['max_lambda_min_over_tilts']:.3e}, residual zero crossings "
            f"{scan['residual_zero_crossings']}, discriminant {scan['discriminant']:.3f}",
            flush=True,
        )
        gauss.append({**summary, "rows": scan["rows"]})
    orbits = [moebius_orbit(1.0, 0.6, 1.0, b0) for b0 in (-2.0, -0.3, 0.3, 2.0)]
    bimodal = []
    for m in (0.75, 1.0, 1.5, 2.0, 3.0):
        record = selfconsistent_roots(bimodal_law(m, 0.4))
        record["m"] = m
        record["s"] = 0.4
        bimodal.append(record)
    xcorr = [selfconsistent_roots(xcorr_law(c)) for c in (0.5, 0.8, 0.95)]
    mix3 = selfconsistent_roots(mix3_law())
    return {
        "provenance": provenance("popfix", {}),
        "gaussian_scans": gauss,
        "moebius_orbits": orbits,
        "bimodal": bimodal,
        "xcorr": xcorr,
        "mix3": mix3,
    }


# ----------------------------------------------------------------------------
# Mode: signsplit.
# ----------------------------------------------------------------------------


def signsplit_family(v_values: tuple[float, ...]) -> dict:
    """The v-family of stationary nuisance-split configurations on N(0, I2)."""
    sqrt_2_over_pi = math.sqrt(2.0 / math.pi)
    rows = []
    for v in v_values:
        upper = 1.0 - norm.cdf(v)
        lower = norm.cdf(v)
        mu_lam_upper = norm.pdf(v) / upper
        mu_lam_lower = -norm.pdf(v) / lower
        masses = np.array([0.5 * upper, 0.5 * lower, 0.5])
        moments = np.array(
            [
                [0.5 * upper * (-sqrt_2_over_pi), 0.5 * upper * mu_lam_upper],
                [0.5 * lower * (-sqrt_2_over_pi), 0.5 * lower * mu_lam_lower],
                [0.5 * sqrt_2_over_pi, 0.0],
            ]
        )
        info = binned_info(masses, moments)
        value, _ = profiled_value(info)
        eigs = np.linalg.eigvalsh(info)
        rows.append(
            {
                "v": v,
                "min_mass": float(masses.min()),
                "i11": float(info[1, 1]),
                "i01": float(info[0, 1]),
                "lambda_min": float(eigs[0]),
                "value": value,
                "value_minus_two_over_pi": value - 2.0 / math.pi,
            }
        )
    ref = scalar_lloyd([(1.0, 0.0, 1.0)], 3)
    ref2 = scalar_lloyd([(1.0, 0.0, 1.0)], 2)
    return {
        "provenance": provenance("signsplit", {"v_values": list(v_values)}),
        "two_over_pi": 2.0 / math.pi,
        "one_over_pi": 1.0 / math.pi,
        "v3": ref["value"],
        "v2": ref2["value"],
        "merged_branch_price_v3_minus_v2": ref["value"] - ref2["value"],
        "family": rows,
        "eight_atom_exact": signsplit_eight_atom_exact(),
    }


def run_signsplit() -> dict:
    out = signsplit_family((-1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0))
    at0 = next(r for r in out["family"] if r["v"] == 0.0)
    print(
        f"[signsplit] v=0: value={at0['value']:.6f} (2/pi={out['two_over_pi']:.6f}), "
        f"i11={at0['i11']:.6f} (1/pi={out['one_over_pi']:.6f}), "
        f"v2={out['v2']:.6f}, v3={out['v3']:.6f}, "
        f"merged price v3-v2={out['merged_branch_price_v3_minus_v2']:.6f}",
        flush=True,
    )
    return out


# ----------------------------------------------------------------------------
# Mode: hessian.
# ----------------------------------------------------------------------------


def family_value(law: MixtureLaw, params: np.ndarray) -> float:
    beta = float(params[0])
    cuts = sorted(float(x) for x in params[1:])
    quants = rule_quantities(law, beta, cuts)
    return quants["value"]


def run_hessian(popfix: dict | None = None) -> dict:
    if popfix is None:
        popfix = run_popfix()
    reports = []
    candidates = [rec for rec in popfix["bimodal"] if rec["fixed_point"]]
    if popfix["mix3"].get("fixed_point"):
        candidates.append({"law": "mix3", "fixed_point": popfix["mix3"]["fixed_point"], "m": None})
    for rec in candidates:
        term = rec["fixed_point"]
        law = mix3_law() if rec["law"] == "mix3" else bimodal_law(rec["m"], rec.get("s", 0.4))
        x0 = np.array([term["beta"], *term["cuts"]])
        h = 1e-4
        dim = x0.size
        hess = np.zeros((dim, dim))
        f0 = family_value(law, x0)
        grad = np.zeros(dim)
        for i in range(dim):
            ei = np.zeros(dim)
            ei[i] = h
            grad[i] = (family_value(law, x0 + ei) - family_value(law, x0 - ei)) / (2 * h)
        for i in range(dim):
            for j in range(i, dim):
                ei = np.zeros(dim)
                ej = np.zeros(dim)
                ei[i] = h
                ej[j] = h
                val = (
                    family_value(law, x0 + ei + ej)
                    - family_value(law, x0 + ei - ej)
                    - family_value(law, x0 - ei + ej)
                    + family_value(law, x0 - ei - ej)
                ) / (4 * h * h)
                hess[i, j] = hess[j, i] = val
        eigs = np.linalg.eigvalsh(hess)
        reports.append(
            {
                "law": law.name,
                "beta": term["beta"],
                "cuts": term["cuts"],
                "value": f0,
                "family_gradient": grad.tolist(),
                "family_hessian_eigs": eigs.tolist(),
                "family_local_max": bool(np.all(eigs < 1e-6)),
            }
        )
        print(
            f"[hessian] {law.name}: grad_norm={np.linalg.norm(grad):.2e} "
            f"hessian eigs={np.round(eigs, 4).tolist()} local_max={reports[-1]['family_local_max']}",
            flush=True,
        )
    return {"provenance": provenance("hessian", {}), "reports": reports}


# ----------------------------------------------------------------------------
# Mode: geometry.
# ----------------------------------------------------------------------------


def state_geometry(scores: np.ndarray, labels: np.ndarray, k: int) -> dict:
    n = scores.shape[0]
    info = np.zeros((2, 2))
    masses = np.zeros(k)
    cents = np.zeros((k, 2))
    for b in range(k):
        mask = labels == b
        w_b = mask.sum() / n
        masses[b] = w_b
        m_b = scores[mask].sum(axis=0) / n
        info += np.outer(m_b, m_b) / w_b
        cents[b] = m_b / w_b
    if info[1, 1] <= 0:
        return {"degenerate": True}
    b_star = info[0, 1] / info[1, 1]
    proj = cents[:, 0] - b_star * cents[:, 1]
    e_val = scores[:, 0] - b_star * scores[:, 1]
    nearest = np.argmin(np.abs(e_val[:, None] - proj[None, :]), axis=1)
    eigs = np.linalg.eigvalsh(info)
    sep = min(abs(proj[x] - proj[y]) for x in range(k) for y in range(x + 1, k))
    return {
        "degenerate": False,
        "b_star": float(b_star),
        "i11": float(info[1, 1]),
        "lambda_min": float(eigs[0]),
        "min_mass": float(masses.min()),
        "proj_sep": float(sep),
        "companion_disagreement": float(np.mean(nearest != labels)),
    }


def run_geometry() -> dict:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from audit_ds_margins_at_optima import center, sample_law

    fixture = json.loads(
        (root / "COUNTEREXAMPLES" / "CE-DS-STABLE-MARGIN-RETAINING-001.json").read_text()
    )
    scores = np.array([[float(Fraction(x)) for x in row] for row in fixture["scores"]])
    labels = np.array(fixture["labels_before"])
    witness = state_geometry(scores, labels, fixture["K"])
    print(
        f"[geometry] witness: disagreement={witness['companion_disagreement']:.3f} "
        f"proj_sep={witness['proj_sep']:.4f} b_star={witness['b_star']:.4f}",
        flush=True,
    )

    summary_path = root / "WORK" / "artifacts" / "DS-STABLE-MARGINS-COMPILE" / "census-summary.json"
    census = json.loads(summary_path.read_text())
    terminals = []
    for inst in census["ascent"]["instances"]:
        rows = sample_law(inst["law"], inst["n"], inst["seed"])
        weights = [Fraction(1, inst["n"])] * inst["n"]
        centered = center(rows, weights)
        arr = np.array([[float(x) for x in row] for row in centered])
        for term in inst["terminals"]:
            lab = np.array([int(ch) for ch in term["labels"]])
            geo = state_geometry(arr, lab, 3)
            if geo.get("degenerate"):
                continue
            terminals.append(
                {
                    "law": inst["law"],
                    "n": inst["n"],
                    "rep": inst["rep"],
                    "seed_kind": term["seed_kind"],
                    **geo,
                }
            )
    agree = [t for t in terminals if t["companion_disagreement"] == 0.0]
    print(
        f"[geometry] {len(terminals)} ascent terminals; "
        f"{len(agree)} agree exactly with their companion rule; "
        f"median disagreement "
        f"{np.median([t['companion_disagreement'] for t in terminals]):.3f}",
        flush=True,
    )
    return {
        "provenance": provenance("geometry", {}),
        "witness": witness,
        "terminals": terminals,
    }


# ----------------------------------------------------------------------------
# Mode: library (Phase 2; public API only).
# ----------------------------------------------------------------------------


def induced_labels(scores: np.ndarray, beta: float, cuts: list[float]) -> np.ndarray:
    t_val = scores[:, 0] - beta * scores[:, 1]
    return np.searchsorted(np.asarray(cuts), t_val, side="right")


def run_library(
    sizes: tuple[int, ...] = (300, 1000, 3000), reps: int = 3, fixed_points: dict | None = None
) -> dict:
    from scorequant import (
        DExchangeConfig,
        ProfiledDOptimality,
        efficient_score_bound,
        optimize_partition,
    )

    laws: list[tuple[str, MixtureLaw, dict | None]] = []
    if fixed_points:
        for rec in fixed_points.get("bimodal", []):
            if rec["fixed_point"]:
                laws.append((rec["law"], bimodal_law(rec["m"], rec["s"]), rec["fixed_point"]))
        if fixed_points.get("mix3", {}).get("fixed_point"):
            laws.append(("mix3", mix3_law(), fixed_points["mix3"]["fixed_point"]))
    laws.append(("gauss06", gaussian_law(1.0, 0.6, 1.0, name="gauss06"), None))

    runs = []
    for law_name, law, fp in laws:
        for n in sizes:
            for rep in range(1, reps + 1):
                seed = SEED_BASE + 1000 * n + rep
                rng = np.random.default_rng(seed)
                scores = sample_mixture(law, n, rng)
                scores = scores - scores.mean(axis=0)
                bound = efficient_score_bound(scores, interest=(0,), n_bins=3)
                seedings: dict[str, dict] = {
                    "efficient": {"initial_labels": np.asarray(bound.labels)},
                    "kmeans": {},
                    "random": {"config": DExchangeConfig(seed=seed, solver_restarts=1, init="random")},
                }
                if fp is not None:
                    lab = induced_labels(scores, fp["beta"], fp["cuts"])
                    if len(np.unique(lab)) == 3:
                        seedings["fixedpoint"] = {"initial_labels": lab}
                for seed_kind, kwargs in seedings.items():
                    config = kwargs.pop("config", DExchangeConfig(seed=seed, solver_restarts=1))
                    result = optimize_partition(
                        scores,
                        n_bins=3,
                        criterion=ProfiledDOptimality(interest=(0,)),
                        config=config,
                        **kwargs,
                    )
                    geo = state_geometry(scores, np.asarray(result.labels), 3)
                    start_geo = (
                        state_geometry(scores, np.asarray(kwargs["initial_labels"]), 3)
                        if "initial_labels" in kwargs
                        else None
                    )
                    runs.append(
                        {
                            "law": law_name,
                            "n": n,
                            "rep": rep,
                            "seed": seed,
                            "seed_kind": seed_kind,
                            "objective_log": float(result.objective),
                            "upper_bound_log": float(bound.upper_bound),
                            "gap_log": float(bound.upper_bound - result.objective),
                            "exchange_stable": bool(result.exchange_stable),
                            "terminal": geo,
                            "seed_state": start_geo,
                        }
                    )
                    print(
                        f"[library] {law_name} N={n} rep={rep} {seed_kind}: "
                        f"gap_log={runs[-1]['gap_log']:.5f} "
                        f"i11={geo.get('i11', float('nan')):.4f} "
                        f"lam_min={geo.get('lambda_min', float('nan')):.5f} "
                        f"sep={geo.get('proj_sep', float('nan')):.4f} "
                        f"stable={runs[-1]['exchange_stable']}",
                        flush=True,
                    )
    return {"provenance": provenance("library", {"sizes": list(sizes), "reps": reps}), "runs": runs}


# ----------------------------------------------------------------------------
# CLI.
# ----------------------------------------------------------------------------


def json_default(obj):
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, Fraction):
        return str(obj)
    raise TypeError(f"unserializable: {type(obj)}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "mode",
        choices=["selftest", "popfix", "signsplit", "hessian", "geometry", "library", "all"],
    )
    args = parser.parse_args(argv)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    results: dict = {}
    popfix_result = None
    if args.mode in ("selftest", "all"):
        results["selftest"] = run_selftest()
    if args.mode in ("popfix", "all", "hessian", "library"):
        popfix_result = run_popfix()
        results["popfix"] = popfix_result
    if args.mode in ("signsplit", "all"):
        results["signsplit"] = run_signsplit()
    if args.mode in ("hessian", "all"):
        results["hessian"] = run_hessian(popfix_result)
    if args.mode in ("geometry", "all"):
        results["geometry"] = run_geometry()
    if args.mode in ("library", "all"):
        results["library"] = run_library(fixed_points=popfix_result)
    out = ARTIFACT_DIR / (f"{args.mode}.json" if args.mode != "all" else "summary.json")
    out.write_text(json.dumps(results, indent=1, default=json_default))
    print(f"[done] wrote {out}", flush=True)


if __name__ == "__main__":
    main()
