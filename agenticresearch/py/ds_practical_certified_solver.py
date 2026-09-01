"""Exact falsification harness for the practical profiled-Ds certificate packet.

Two deliberately separate commands are provided:

``dual-search``
    Rebuild the support-minimal rational tilt-duality-gap witness, its exact
    two-quadratic lower certificate, and a small tie/duplicate/singularity
    battery.  This is theorem-facing exact arithmetic.

``ds18-search``
    Probe the proposed strip-DP primal on exact samples from the DS18 law and
    verify the empirical projection-tax identity on every finite partition.
    The beta sweep is explicitly recorded as a finite probe, never as a
    consistency verdict.

Every claim-relevant quantity uses :class:`fractions.Fraction`.  Floating
point appears only in the human-readable summaries and runtime metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

F = Fraction
N_BINS = 3
RESEARCH = Path(__file__).resolve().parents[1]
WORKSPACE = RESEARCH.parent
ARTIFACTS = RESEARCH / "WORK" / "artifacts" / "DS-PRACTICAL-CERTIFIED-SOLVER"
DUAL_OUTPUT = ARTIFACTS / "dual-search.json"
DS18_OUTPUT = ARTIFACTS / "ds18-search.json"
DUAL_FIXTURE = RESEARCH / "COUNTEREXAMPLES" / "CE-DS-TILT-DUAL-GAP-001.json"

Score = tuple[Fraction, Fraction]
Information = tuple[Fraction, Fraction, Fraction]
Quadratic = tuple[Fraction, Fraction, Fraction]


def canonical_partitions(size: int, bins: int = N_BINS) -> Iterator[tuple[int, ...]]:
    """Yield label-permutation-canonical surjective partitions."""
    if size < bins:
        return
    for labels in product(range(bins), repeat=size):
        if labels[0] != 0 or len(set(labels)) != bins:
            continue
        if all(labels[index] <= max(labels[:index]) + 1 for index in range(1, size)):
            yield labels


def canonicalize(labels: Sequence[int]) -> tuple[int, ...]:
    """Canonicalize one labeling by first occurrence."""
    mapping: dict[int, int] = {}
    out = []
    for label in labels:
        if label not in mapping:
            mapping[label] = len(mapping)
        out.append(mapping[label])
    return tuple(out)


def binned_information(
    scores: Sequence[Score],
    weights: Sequence[Fraction],
    labels: Sequence[int],
    bins: int = N_BINS,
) -> Information:
    """Return ``(I_psi_psi, I_psi_lambda, I_lambda_lambda)`` exactly."""
    masses = [F(0)] * bins
    poi = [F(0)] * bins
    nuisance = [F(0)] * bins
    for (psi, lam), weight, label in zip(scores, weights, labels, strict=True):
        masses[label] += weight
        poi[label] += weight * psi
        nuisance[label] += weight * lam
    if any(mass == 0 for mass in masses):
        raise ValueError("all cells must have positive mass")
    return (
        sum(first * first / mass for first, mass in zip(poi, masses, strict=True)),
        sum(
            first * second / mass
            for first, second, mass in zip(poi, nuisance, masses, strict=True)
        ),
        sum(second * second / mass for second, mass in zip(nuisance, masses, strict=True)),
    )


def profiled_value(information: Information) -> tuple[Fraction, bool]:
    """Return the DS11 pseudo-inverse value and DS9 regularity flag."""
    poi, cross, nuisance = information
    if nuisance == 0:
        if cross != 0:
            raise AssertionError("PSD binned information cannot have cross != 0 at I_ll = 0")
        return poi, False
    return poi - cross * cross / nuisance, True


def tilt_quadratic(information: Information) -> Quadratic:
    """Return coefficients of ``between(S_psi-beta S_lambda; z)``."""
    poi, cross, nuisance = information
    return nuisance, -2 * cross, poi


def quadratic_value(quadratic: Quadratic, beta: Fraction) -> Fraction:
    """Evaluate ``A beta^2 + B beta + C`` exactly."""
    a, b, c = quadratic
    return a * beta * beta + b * beta + c


def quadratic_minimum(quadratic: Quadratic) -> tuple[Fraction, Fraction]:
    """Return the exact vertex and minimum of one convex quadratic."""
    a, b, c = quadratic
    if a == 0:
        if b != 0:
            raise ValueError("a nonconstant affine function has no finite global minimum")
        return F(0), c
    beta = -b / (2 * a)
    return beta, quadratic_value(quadratic, beta)


def mix_quadratics(
    first: Quadratic, second: Quadratic, alpha: Fraction
) -> Quadratic:
    """Return ``alpha * first + (1-alpha) * second``."""
    return tuple(
        alpha * left + (1 - alpha) * right
        for left, right in zip(first, second, strict=True)
    )  # type: ignore[return-value]


def global_profiled_report(
    scores: Sequence[Score], weights: Sequence[Fraction], bins: int = N_BINS
) -> dict[str, object]:
    """Exhaust both finite comparison domains exactly."""
    regular: list[tuple[Fraction, tuple[int, ...]]] = []
    pseudo: list[tuple[Fraction, tuple[int, ...]]] = []
    singular = 0
    count = 0
    for labels in canonical_partitions(len(scores), bins):
        count += 1
        value, is_regular = profiled_value(binned_information(scores, weights, labels, bins))
        pseudo.append((value, labels))
        if is_regular:
            regular.append((value, labels))
        else:
            singular += 1
    best_pseudo = max(value for value, _ in pseudo)
    best_regular = None if not regular else max(value for value, _ in regular)
    return {
        "canonical_partitions": count,
        "regular_partitions": len(regular),
        "singular_partitions": singular,
        "global_pseudo_inverse_value": best_pseudo,
        "global_pseudo_inverse_labels": [
            list(labels) for value, labels in pseudo if value == best_pseudo
        ],
        "global_regular_value": best_regular,
        "global_regular_labels": (
            []
            if best_regular is None
            else [list(labels) for value, labels in regular if value == best_regular]
        ),
    }


def between_value(
    values: Sequence[Fraction],
    weights: Sequence[Fraction],
    labels: Sequence[int],
    bins: int = N_BINS,
) -> Fraction:
    """Return the exact uncentered scalar between-cell second moment."""
    masses = [F(0)] * bins
    moments = [F(0)] * bins
    for value, weight, label in zip(values, weights, labels, strict=True):
        masses[label] += weight
        moments[label] += weight * value
    if any(mass == 0 for mass in masses):
        raise ValueError("all cells must have positive mass")
    return sum(moment * moment / mass for moment, mass in zip(moments, masses, strict=True))


def _tie_orders(values: Sequence[Fraction]) -> Iterator[tuple[int, ...]]:
    """Yield every total order consistent with the scalar weak order."""
    groups: list[tuple[int, ...]] = []
    for value in sorted(set(values)):
        groups.append(tuple(index for index, candidate in enumerate(values) if candidate == value))
    choices = [tuple(permutations(group)) for group in groups]
    for ordered_groups in product(*choices):
        yield tuple(index for group in ordered_groups for index in group)


def scalar_interval_optimum(
    values: Sequence[Fraction], weights: Sequence[Fraction], bins: int = N_BINS
) -> tuple[Fraction, list[tuple[int, ...]], int]:
    """Solve the row-assignment scalar problem, exhausting all exact tie orders."""
    best: Fraction | None = None
    labels_at_best: set[tuple[int, ...]] = set()
    order_count = 0
    for order in _tie_orders(values):
        order_count += 1
        for cuts in combinations(range(1, len(values)), bins - 1):
            bounds = (0, *cuts, len(values))
            labels = [0] * len(values)
            for cell, (start, stop) in enumerate(zip(bounds, bounds[1:], strict=False)):
                for position in range(start, stop):
                    labels[order[position]] = cell
            canonical = canonicalize(labels)
            value = between_value(values, weights, canonical, bins)
            if best is None or value > best:
                best = value
                labels_at_best = {canonical}
            elif value == best:
                labels_at_best.add(canonical)
    if best is None:
        raise ValueError("no nonempty scalar interval partition")
    return best, sorted(labels_at_best), order_count


def scalar_brute_optimum(
    values: Sequence[Fraction], weights: Sequence[Fraction], bins: int = N_BINS
) -> Fraction:
    """Return the full row-assignment scalar optimum for a small exact table."""
    return max(
        between_value(values, weights, labels, bins)
        for labels in canonical_partitions(len(values), bins)
    )


def weak_duality_report(
    scores: Sequence[Score],
    weights: Sequence[Fraction],
    betas: Sequence[Fraction],
    bins: int = N_BINS,
) -> dict[str, object]:
    """Attack weak duality on every partition at the requested tilts."""
    rows = []
    violations = 0
    for beta in betas:
        values = [psi - beta * lam for psi, lam in scores]
        scalar = scalar_brute_optimum(values, weights, bins)
        interval, _, tie_orders = scalar_interval_optimum(values, weights, bins)
        local_violations = 0
        minimum_slack: Fraction | None = None
        for labels in canonical_partitions(len(scores), bins):
            information = binned_information(scores, weights, labels, bins)
            value, _ = profiled_value(information)
            tilted = quadratic_value(tilt_quadratic(information), beta)
            slack = scalar - value
            if not (value <= tilted <= scalar):
                local_violations += 1
            if minimum_slack is None or slack < minimum_slack:
                minimum_slack = slack
        violations += local_violations
        rows.append(
            {
                "beta": beta,
                "scalar_brute": scalar,
                "scalar_interval": interval,
                "contiguity_agrees": scalar == interval,
                "tie_orders": tie_orders,
                "minimum_dual_slack": minimum_slack,
                "violations": local_violations,
            }
        )
    return {"betas": rows, "violations": violations}


def dual_witness() -> tuple[dict[str, object], dict[str, object]]:
    """Build and prove the support-minimal exact rational dual-gap witness."""
    scores: tuple[Score, ...] = (
        (F(-11, 2), F(39, 8)),
        (F(3, 2), F(-65, 8)),
        (F(7, 2), F(31, 8)),
        (F(9, 2), F(-49, 8)),
    )
    weights = (F(1, 4),) * 4
    first = (0, 0, 1, 2)
    optimum = (0, 1, 2, 2)
    first_information = binned_information(scores, weights, first)
    optimum_information = binned_information(scores, weights, optimum)
    first_value, first_regular = profiled_value(first_information)
    optimum_value, optimum_regular = profiled_value(optimum_information)
    first_quadratic = tilt_quadratic(first_information)
    optimum_quadratic = tilt_quadratic(optimum_information)
    alpha = F(14, 25)
    mixture = mix_quadratics(first_quadratic, optimum_quadratic, alpha)
    mixture_beta, mixture_lower = quadratic_minimum(mixture)
    global_report = global_profiled_report(scores, weights)
    global_value = global_report["global_pseudo_inverse_value"]
    assert isinstance(global_value, Fraction)
    gap = mixture_lower - global_value

    assert first_regular and optimum_regular
    assert global_report["canonical_partitions"] == 6
    assert global_report["regular_partitions"] == 6
    assert global_value == optimum_value == F(116805, 11816)
    assert first_quadratic == (F(925, 64), F(15, 4), F(81, 8))
    assert optimum_quadratic == (F(1477, 64), F(24), F(129, 8))
    assert mixture_beta == F(-10128, 29197)
    assert mixture_lower == F(61717893, 5839400)
    assert gap == F(105329256, 154014175) > 0

    weak = weak_duality_report(
        scores, weights, (F(-1), mixture_beta, F(0), F(1))
    )
    assert weak["violations"] == 0

    fixture = {
        "id": "CE-DS-TILT-DUAL-GAP-001",
        "criterion": "Ds",
        "level": "finite_assignment",
        "claim_falsified": (
            "The scalar-interest tilt-dual bracket is always exact: "
            "min_beta max_z between(S_psi-beta S_lambda; z) equals the exact "
            "global profiled-Ds value. FALSE: two explicit tilt quadratics give "
            "a rational lower certificate strictly above the exhaustive global optimum."
        ),
        "scores": scores,
        "weights": weights,
        "K": N_BINS,
        "labels_before": first,
        "labels_after_or_optimum": optimum,
        "poi_indices": [0],
        "nuisance_indices": [1],
        "objective_before": first_value,
        "objective_after": optimum_value,
        "comparison_domain": (
            "All six label-permutation-canonical nonempty K=3 row assignments; "
            "every nuisance block is nonsingular, so DS9 in-bin and DS11 "
            "pseudo-inverse domains coincide."
        ),
        "exact_quantities": {
            "canonical_partitions": 6,
            "regular_partitions": 6,
            "global_profiled_value": global_value,
            "first_information": first_information,
            "optimum_information": optimum_information,
            "first_tilt_quadratic_ABC": first_quadratic,
            "optimum_tilt_quadratic_ABC": optimum_quadratic,
            "convex_mixture_alpha_on_first": alpha,
            "mixture_quadratic_ABC": mixture,
            "mixture_vertex_beta": mixture_beta,
            "mixture_global_minimum": mixture_lower,
            "certified_duality_gap_lower_bound": gap,
            "certificate_inequality": (
                "max_z q_z(beta) >= (14/25) q_first(beta) + "
                "(11/25) q_optimum(beta) for every real beta"
            ),
            "support_minimality": (
                "For K=3, N=3 has only the singleton partition up to relabeling, "
                "so its tilt dual closes exactly; N=4 is minimal."
            ),
        },
        "duplication_scope": [
            "Splitting every weight among identical duplicate rows preserves the witness "
            "under ScoreQuant's duplicate-collapsed atom semantics.",
            "No preservation claim is made for an unmerged row-assignment domain, which "
            "can split identical rows across cells."
        ],
        "order_one_family": {
            "construction": (
                "For integer r>=2, give each displayed atom weight (1-1/r)/4 and add "
                "r distinct bounded rational atoms, row j having score "
                "(j/(r+1)^2,j/(r+1)^3) and weight 1/r^2. The added mass is exactly 1/r."
            ),
            "proof": (
                "On every compact beta set, an added-only cell contributes O(1/r) by "
                "cellwise Cauchy-Schwarz, while a cell containing a base atom has mass "
                "bounded below and its quadratic changes by O(1/r). The displayed "
                "coercive mixed quadratic keeps all dual minimizers in one common compact "
                "interval. The same cellwise bounds in the scalar generalized Schur formula "
                "give d_r->d and g_r^+->g^+, so the gap remains bounded below by a positive "
                "constant."
            ),
            "does_not_use": "unrestricted split-duplicate invariance",
        },
        "verification": {
            "method": "exact rational exhaustive enumeration plus convex-mixture lower certificate",
            "notes": (
                "All arithmetic is fractions.Fraction. The certificate does not need "
                "the generally algebraic exact minimizer of the full quadratic envelope."
            ),
        },
        "source": "DS-PRACTICAL-CERTIFIED-SOLVER falsification search",
        "date": "2026-09-01",
    }
    artifact_case = {
        "fixture": fixture["id"],
        "global": global_report,
        "certificate": fixture["exact_quantities"],
        "weak_duality": weak,
        "result": "EXACT_POSITIVE_DUALITY_GAP",
    }
    return fixture, artifact_case


def collapse_duplicate_scores(
    scores: Sequence[Score], weights: Sequence[Fraction]
) -> tuple[list[Score], list[Fraction]]:
    """Pool identical full-score atoms exactly."""
    pooled: dict[Score, Fraction] = {}
    for score, weight in zip(scores, weights, strict=True):
        pooled[score] = pooled.get(score, F(0)) + weight
    atoms = sorted(pooled)
    return atoms, [pooled[atom] for atom in atoms]


def adversarial_cases() -> list[tuple[str, list[Score], list[Fraction]]]:
    """Return the tie/duplicate/weight/singularity cases for the exact battery."""
    unequal_raw = [F(1), F(2), F(3), F(4)]
    unequal_weights = [weight / sum(unequal_raw) for weight in unequal_raw]
    return [
        (
            "duplicate_atoms",
            [(F(-1), F(0)), (F(-1), F(0)), (F(0), F(1)), (F(1), F(0)), (F(1), F(0))],
            [F(1, 5)] * 5,
        ),
        (
            "exact_tilt_ties",
            [(F(-1), F(-1)), (F(0), F(0)), (F(1), F(1)), (F(2), F(0))],
            [F(1, 4)] * 4,
        ),
        (
            "unequal_weights",
            [
                (F(-3, 4), F(-5, 16)),
                (F(-1, 4), F(-25, 16)),
                (F(1, 4), F(3, 16)),
                (F(3, 4), F(27, 16)),
            ],
            unequal_weights,
        ),
        (
            "singular_nuisance",
            [(F(-1), F(0)), (F(0), F(0)), (F(1), F(0))],
            [F(1, 3)] * 3,
        ),
        (
            "near_singular_nuisance",
            [(F(-1), F(0)), (F(-1, 2), F(1, 1000)), (F(1, 2), F(-1, 1000)), (F(1), F(0))],
            [F(1, 4)] * 4,
        ),
    ]


def adversarial_report(max_size: int = 10) -> dict[str, object]:
    """Run the exact weak-duality and contiguity battery through ``max_size``."""
    reports = []
    violations = 0
    contiguity_disagreements = 0
    cases = adversarial_cases()
    for size in range(3, max_size + 1):
        scores, weights = ds18_midpoint(size)
        cases.append((f"ds18_midpoint_n{size}", scores, weights))
    for size in range(6, max_size + 1, 2):
        scores, weights = ds18_product(size)
        cases.append((f"ds18_product_n{size}", scores, weights))
    for name, scores, weights in cases:
        weak = weak_duality_report(scores, weights, (F(-1), F(0), F(1)))
        global_report = global_profiled_report(scores, weights)
        local_disagreements = sum(
            not row["contiguity_agrees"] for row in weak["betas"]
        )
        reports.append(
            {
                "name": name,
                "rows": len(scores),
                "global": global_report,
                "weak_duality": weak,
                "contiguity_disagreements": local_disagreements,
            }
        )
        violations += int(weak["violations"])
        contiguity_disagreements += local_disagreements

    fixture, _ = dual_witness()
    duplicated_scores = [score for score in fixture["scores"] for _ in range(2)]
    duplicated_weights = [weight / 2 for weight in fixture["weights"] for _ in range(2)]
    collapsed_scores, collapsed_weights = collapse_duplicate_scores(
        duplicated_scores, duplicated_weights
    )
    base_scores = [tuple(row) for row in fixture["scores"]]
    base_weights = list(fixture["weights"])
    collapsed_invariant = (
        collapsed_scores == sorted(base_scores)
        and sorted(zip(collapsed_scores, collapsed_weights, strict=True))
        == sorted(zip(base_scores, base_weights, strict=True))
    )
    return {
        "cases": reports,
        "max_size": max_size,
        "canonical_partitions": sum(
            int(report["global"]["canonical_partitions"]) for report in reports
        ),
        "weak_duality_violations": violations,
        "contiguity_disagreements": contiguity_disagreements,
        "split_weight_duplication_after_atom_collapse": collapsed_invariant,
    }


def ds18_score(x_value: Fraction, z_value: Fraction) -> Score:
    """Return one exact row from ``S=(X,3X^2-1+Z)``."""
    return x_value, 3 * x_value * x_value - 1 + z_value


def ds18_midpoint(size: int) -> tuple[list[Score], list[Fraction]]:
    """Return a symmetric exact midpoint sample with ``Z=0``."""
    xs = [F(2 * index + 1 - size, size) for index in range(size)]
    return [ds18_score(x_value, F(0)) for x_value in xs], [F(1, size)] * size


def ds18_product(size: int) -> tuple[list[Score], list[Fraction]]:
    """Return the existing exact X-midpoint by Z=+-1/2 product family."""
    x_count = size // 2
    xs = [F(2 * index + 1 - x_count, x_count) for index in range(x_count)]
    scores = [
        ds18_score(x_value, z_value)
        for x_value in xs
        for z_value in (F(-1, 2), F(1, 2))
    ]
    return scores, [F(1, size)] * size


def empirical_projection(
    scores: Sequence[Score], weights: Sequence[Fraction]
) -> tuple[Fraction, list[Fraction]]:
    """Return empirical full-sample slope and efficient scores exactly."""
    cross = sum(weight * psi * lam for (psi, lam), weight in zip(scores, weights, strict=True))
    nuisance = sum(weight * lam * lam for (_, lam), weight in zip(scores, weights, strict=True))
    if nuisance == 0:
        raise ValueError("empirical nuisance second moment is singular")
    beta = cross / nuisance
    efficient = [psi - beta * lam for psi, lam in scores]
    assert sum(
        weight * value * lam
        for value, (_, lam), weight in zip(efficient, scores, weights, strict=True)
    ) == 0
    return beta, efficient


def projection_tax(
    scores: Sequence[Score],
    weights: Sequence[Fraction],
    labels: Sequence[int],
    beta: Fraction,
    bins: int = N_BINS,
) -> tuple[Fraction, Fraction, Fraction, Fraction, bool]:
    """Return ``(profiled, between, cross, nuisance, regular)`` exactly."""
    information = binned_information(scores, weights, labels, bins)
    value, regular = profiled_value(information)
    poi, cross_raw, nuisance = information
    between = poi - 2 * beta * cross_raw + beta * beta * nuisance
    cross = cross_raw - beta * nuisance
    expected = between if nuisance == 0 else between - cross * cross / nuisance
    if value != expected:
        raise AssertionError("empirical projection-tax identity failed")
    return value, between, cross, nuisance, regular


def beta_probe_points(scores: Sequence[Score], beta_hat: Fraction) -> list[Fraction]:
    """Return crossings, order-cell midpoints, exterior probes, zero, and beta_hat."""
    crossings = {
        (scores[first][0] - scores[second][0])
        / (scores[first][1] - scores[second][1])
        for first, second in combinations(range(len(scores)), 2)
        if scores[first][1] != scores[second][1]
    }
    ordered = sorted(crossings)
    points = set(ordered)
    points.update((F(0), beta_hat))
    if ordered:
        points.update((ordered[0] - 1, ordered[-1] + 1))
        points.update(
            (left + right) / 2
            for left, right in zip(ordered, ordered[1:], strict=False)
        )
    return sorted(points)


def ds18_case_report(
    name: str, scores: Sequence[Score], weights: Sequence[Fraction]
) -> dict[str, object]:
    """Run one exact tax census and finite beta probe."""
    beta_hat, efficient = empirical_projection(scores, weights)
    partitions = list(canonical_partitions(len(scores)))
    tax_violations = 0
    regular = 0
    for labels in partitions:
        try:
            _, _, _, _, is_regular = projection_tax(scores, weights, labels, beta_hat)
        except AssertionError:
            tax_violations += 1
            continue
        regular += int(is_regular)

    efficient_upper, _, efficient_tie_orders = scalar_interval_optimum(efficient, weights)
    active_labels: set[tuple[int, ...]] = set()
    contiguity_disagreements = 0
    probe_rows = []
    for beta in beta_probe_points(scores, beta_hat):
        values = [psi - beta * lam for psi, lam in scores]
        interval, labels, tie_orders = scalar_interval_optimum(values, weights)
        brute = scalar_brute_optimum(values, weights)
        if interval != brute:
            contiguity_disagreements += 1
        active_labels.update(labels)
        probe_rows.append(
            {
                "beta": beta,
                "scalar_value": interval,
                "tie_orders": tie_orders,
                "optimal_labels": [list(candidate) for candidate in labels],
            }
        )

    pseudo_candidates = []
    regular_candidates = []
    for labels in active_labels:
        value, is_regular = profiled_value(binned_information(scores, weights, labels))
        pseudo_candidates.append((value, labels))
        if is_regular:
            regular_candidates.append((value, labels))
    pseudo_primal = max(pseudo_candidates)
    regular_primal = None if not regular_candidates else max(regular_candidates)
    return {
        "name": name,
        "rows": len(scores),
        "canonical_partitions": len(partitions),
        "regular_partitions": regular,
        "tax_identity_violations": tax_violations,
        "empirical_beta_hat": beta_hat,
        "efficient_score_scalar_upper": efficient_upper,
        "efficient_score_tie_orders": efficient_tie_orders,
        "beta_probe_scope": (
            "finite exact crossings+order-cell-midpoints probe; not an exact "
            "parametric-envelope computation and not a consistency verdict"
        ),
        "beta_probe_count": len(probe_rows),
        "contiguity_disagreements": contiguity_disagreements,
        "active_probe_labels": len(active_labels),
        "pseudo_primal_probe_value": pseudo_primal[0],
        "pseudo_primal_probe_labels": list(pseudo_primal[1]),
        "regular_primal_probe_value": None if regular_primal is None else regular_primal[0],
        "regular_primal_probe_labels": (
            None if regular_primal is None else list(regular_primal[1])
        ),
        "efficient_minus_regular_primal_probe": (
            None if regular_primal is None else efficient_upper - regular_primal[0]
        ),
        "probe": probe_rows,
    }


def ds18_search(max_size: int = 10) -> dict[str, object]:
    """Run the bounded exact DS18 tax/primal probe matrix."""
    cases: list[tuple[str, list[Score], list[Fraction]]] = []
    for size in range(4, max_size + 1):
        scores, weights = ds18_midpoint(size)
        cases.append((f"midpoint_n{size}", scores, weights))
    for size in range(6, max_size + 1, 2):
        scores, weights = ds18_product(size)
        cases.append((f"product_n{size}", scores, weights))
    boundary_x = [F(-3, 4), F(-1, 4), F(1, 4), F(3, 4)]
    boundary_z = [F(-1), F(-3, 4), F(1), F(1)]
    cases.append(
        (
            "population_cut_boundary_n4",
            [
                ds18_score(x_value, z_value)
                for x_value, z_value in zip(boundary_x, boundary_z, strict=True)
            ],
            [F(1, 4)] * 4,
        )
    )
    reports = [ds18_case_report(name, scores, weights) for name, scores, weights in cases]
    return {
        "cases": reports,
        "summary": {
            "tables": len(reports),
            "partitions": sum(int(row["canonical_partitions"]) for row in reports),
            "tax_identity_violations": sum(int(row["tax_identity_violations"]) for row in reports),
            "contiguity_disagreements": sum(
                int(row["contiguity_disagreements"]) for row in reports
            ),
            "positive_probe_gaps": sum(
                row["efficient_minus_regular_primal_probe"] is not None
                and row["efficient_minus_regular_primal_probe"] > 0
                for row in reports
            ),
        },
        "result": "MEASURED_FINITE_PROBE_ONLY",
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=WORKSPACE, capture_output=True, check=True, text=True
    ).stdout.strip()


def provenance(command: str, started: float) -> dict[str, object]:
    """Return the numerical-protocol provenance envelope."""
    script = Path(__file__).resolve()
    return {
        "schema_version": 1,
        "command": command,
        "created_utc": datetime.now(UTC).isoformat(),
        "git_revision_before_commit": _git("rev-parse", "HEAD"),
        "git_status_short": _git("status", "--short"),
        "script_sha256": _sha256(script),
        "uv_lock_sha256": _sha256(WORKSPACE / "uv.lock"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "runtime_seconds": time.monotonic() - started,
        "arithmetic": "fractions.Fraction for every claim-relevant quantity",
    }


def _json_default(value: object) -> str:
    if isinstance(value, Fraction):
        return str(value)
    raise TypeError(f"cannot serialize {type(value)}")


def write_json(path: Path, payload: dict[str, object]) -> None:
    """Write an exact-rational JSON artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=_json_default) + "\n",
        encoding="utf-8",
    )


def run_dual(output: Path, fixture_path: Path, max_size: int) -> None:
    """Run and serialize the exact tilt-duality falsification battery."""
    started = time.monotonic()
    fixture, witness = dual_witness()
    battery = adversarial_report(max_size)
    assert battery["weak_duality_violations"] == 0
    assert battery["contiguity_disagreements"] == 0
    assert battery["split_weight_duplication_after_atom_collapse"] is True
    write_json(fixture_path, fixture)
    payload = {
        "provenance": provenance("dual-search", started),
        "artifact_id": "N-DS-PRACTICAL-DUAL-SEARCH",
        "witness": witness,
        "adversarial": battery,
        "summary": {
            "exact_positive_gap": fixture["exact_quantities"]["certified_duality_gap_lower_bound"],
            "weak_duality_violations": 0,
            "contiguity_disagreements": 0,
        },
        "result": "PASS_WITH_EXACT_COUNTEREXAMPLE",
    }
    write_json(output, payload)
    print(f"dual-search: exact gap={payload['summary']['exact_positive_gap']} wrote={output}")


def run_ds18(output: Path, max_size: int) -> None:
    """Run and serialize the bounded exact DS18 tax/primal probe."""
    started = time.monotonic()
    search = ds18_search(max_size)
    assert search["summary"]["tax_identity_violations"] == 0
    assert search["summary"]["contiguity_disagreements"] == 0
    payload = {
        "provenance": provenance("ds18-search", started),
        "artifact_id": "N-DS-PRACTICAL-DS18-SEARCH",
        **search,
    }
    write_json(output, payload)
    print(
        "ds18-search: "
        f"tables={payload['summary']['tables']} "
        f"partitions={payload['summary']['partitions']} "
        f"positive_probe_gaps={payload['summary']['positive_probe_gaps']} "
        f"wrote={output}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run one exact-search command."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="command", required=True)
    dual = subparsers.add_parser("dual-search", help="serialize the exact dual-gap attack")
    dual.add_argument("--out", type=Path, default=DUAL_OUTPUT)
    dual.add_argument("--fixture", type=Path, default=DUAL_FIXTURE)
    dual.add_argument("--max-size", type=int, default=10)
    ds18 = subparsers.add_parser("ds18-search", help="run the exact DS18 tax/primal probe")
    ds18.add_argument("--out", type=Path, default=DS18_OUTPUT)
    ds18.add_argument("--max-size", type=int, default=10)
    arguments = parser.parse_args(argv)
    if arguments.max_size < 3:
        parser.error("--max-size must be at least 3")
    if arguments.command == "dual-search":
        run_dual(arguments.out, arguments.fixture, arguments.max_size)
    else:
        run_ds18(arguments.out, arguments.max_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
