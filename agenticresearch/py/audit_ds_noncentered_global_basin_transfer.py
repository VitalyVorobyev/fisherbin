"""Independent adversarial audit oracle for DS18.

Audit target
------------
``DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`` (KNOWN_RESULTS/05b-ds-bridge.md,
section "DS18. Exact off-class global basin and empirical stable transfer").

Named population law::

    X, Z iid Uniform[-1, 1],
    S_psi    = X,
    S_lambda = 3 X^2 - 1 + Z,
    K        = 3.

Independence contract
---------------------
This module is written from the law definition alone.  It does **not** import,
extend, translate, or reuse ``py/ds_noncentered_global_basin.py`` (the
researcher's harness), and it does not import the ``scorequant`` library.  It
is pure standard library on purpose, so a bookkeeping session can rerun it.

Two genuinely separate routes are used for every continuous-law quantity:

* **Route A (exact).**  Bivariate polynomial algebra over
  ``fractions.Fraction``.  The law is integrated in the *pre-shear*
  coordinates ``(x, z)``, uniform on the square with density ``1/4``; no
  closed form from the registered proof is typed in.
* **Route B (interval).**  Rigorous interval enclosures built on
  ``decimal.Decimal`` with directed rounding (``ROUND_FLOOR`` /
  ``ROUND_CEILING``) and domain subdivision.  No antiderivative is used, so a
  slip in route A cannot propagate into route B.

Randomness, where used, comes from an explicit 64-bit LCG with the
deterministic seed formula ``seed(n, rep) = SEED_BASE + 1000 * n + rep`` and
``SEED_BASE = 20260831``.

Nothing here is theorem authority.  The audit report
``AUDITS/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001.md`` carries the
mathematics; this file is falsification pressure plus exact provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from collections.abc import Callable, Iterator, Sequence
from datetime import UTC, datetime
from decimal import ROUND_CEILING, ROUND_FLOOR, Context, Decimal
from fractions import Fraction
from itertools import combinations, product
from math import isqrt
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[1]
WORKSPACE = RESEARCH.parent
AUDIT_ID = "AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001"
ARTIFACTS = RESEARCH / "AUDITS" / "artifacts" / AUDIT_ID
SEED_BASE = 20260831
N_BINS = 3

F = Fraction
ONE = F(1)
CUT = F(1, 3)

# --------------------------------------------------------------------------- #
# Route A: exact bivariate polynomial algebra over the pre-shear square
# --------------------------------------------------------------------------- #
#: A polynomial in ``(x, z)`` is a mapping ``(i, j) -> coefficient``.
Poly = dict[tuple[int, int], Fraction]

#: The score coordinates, written straight from the law definition.
S_PSI: Poly = {(1, 0): F(1)}
S_LAM: Poly = {(2, 0): F(3), (0, 0): F(-1), (0, 1): F(1)}
ONE_POLY: Poly = {(0, 0): F(1)}


def padd(left: Poly, right: Poly) -> Poly:
    """Return the sum of two polynomials."""
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, F(0)) + value
    return {key: value for key, value in out.items() if value != 0}


def pmul(left: Poly, right: Poly) -> Poly:
    """Return the product of two polynomials."""
    out: Poly = {}
    for (i0, j0), a in left.items():
        for (i1, j1), b in right.items():
            key = (i0 + i1, j0 + j1)
            out[key] = out.get(key, F(0)) + a * b
    return {key: value for key, value in out.items() if value != 0}


def pscale(poly: Poly, factor: Fraction) -> Poly:
    """Return ``factor * poly``."""
    return {key: value * factor for key, value in poly.items() if value * factor != 0}


def integrate_rectangle(
    poly: Poly, x_lo: Fraction, x_hi: Fraction, z_lo: Fraction, z_hi: Fraction
) -> Fraction:
    """Return the exact integral of ``poly`` over ``[x_lo, x_hi] x [z_lo, z_hi]``."""
    total = F(0)
    for (i, j), coefficient in poly.items():
        x_part = (x_hi ** (i + 1) - x_lo ** (i + 1)) / (i + 1)
        z_part = (z_hi ** (j + 1) - z_lo ** (j + 1)) / (j + 1)
        total += coefficient * x_part * z_part
    return total


def expectation(poly: Poly, x_lo: Fraction = -ONE, x_hi: Fraction = ONE) -> Fraction:
    """Return ``E[poly(X, Z) 1{x_lo <= X <= x_hi}]`` for the uniform square law.

    The joint density of ``(X, Z)`` is ``1/4`` on ``[-1, 1]^2``; the shear to
    score space has unit Jacobian and is never inverted here.
    """
    return integrate_rectangle(poly, x_lo, x_hi, -ONE, ONE) / 4


# --------------------------------------------------------------------------- #
# Route B: rigorous interval arithmetic on Decimal with directed rounding
# --------------------------------------------------------------------------- #
DECIMAL_PRECISION = 50
_DOWN = Context(prec=DECIMAL_PRECISION, rounding=ROUND_FLOOR)
_UP = Context(prec=DECIMAL_PRECISION, rounding=ROUND_CEILING)


class Interval:
    """A rigorous enclosure ``[lo, hi]`` with ``Decimal`` endpoints.

    Every elementary operation is evaluated twice, once in a ``ROUND_FLOOR``
    context for the lower endpoint and once in a ``ROUND_CEILING`` context for
    the upper one, so the enclosure property survives finite precision.
    """

    __slots__ = ("hi", "lo")

    def __init__(self, lo: Decimal, hi: Decimal) -> None:
        if lo > hi:
            raise ValueError(f"empty interval [{lo}, {hi}]")
        self.lo = lo
        self.hi = hi

    @classmethod
    def exact(cls, value: Fraction | int) -> Interval:
        """Return the tightest enclosure of a rational number."""
        value = Fraction(value)
        numerator = Decimal(value.numerator)
        denominator = Decimal(value.denominator)
        return cls(_DOWN.divide(numerator, denominator), _UP.divide(numerator, denominator))

    def __add__(self, other: Interval) -> Interval:
        return Interval(_DOWN.add(self.lo, other.lo), _UP.add(self.hi, other.hi))

    def __sub__(self, other: Interval) -> Interval:
        return Interval(_DOWN.subtract(self.lo, other.hi), _UP.subtract(self.hi, other.lo))

    def __neg__(self) -> Interval:
        return Interval(-self.hi, -self.lo)

    def __mul__(self, other: Interval) -> Interval:
        pairs = (
            (self.lo, other.lo),
            (self.lo, other.hi),
            (self.hi, other.lo),
            (self.hi, other.hi),
        )
        lo = min(_DOWN.multiply(left, right) for left, right in pairs)
        hi = max(_UP.multiply(left, right) for left, right in pairs)
        return Interval(lo, hi)

    def __truediv__(self, other: Interval) -> Interval:
        if other.lo <= 0 <= other.hi:
            raise ZeroDivisionError("interval divisor straddles zero")
        pairs = (
            (self.lo, other.lo),
            (self.lo, other.hi),
            (self.hi, other.lo),
            (self.hi, other.hi),
        )
        lo = min(_DOWN.divide(left, right) for left, right in pairs)
        hi = max(_UP.divide(left, right) for left, right in pairs)
        return Interval(lo, hi)

    def sqrt(self) -> Interval:
        """Return an enclosure of the elementwise square root."""
        if self.lo < 0:
            raise ValueError("sqrt of a negative interval")
        return Interval(_DOWN.sqrt(self.lo), _UP.sqrt(self.hi))

    def contains(self, value: Fraction) -> bool:
        """Return whether the enclosure contains an exact rational."""
        other = Interval.exact(value)
        return self.lo <= other.lo and other.hi <= self.hi

    @property
    def width(self) -> Decimal:
        """Return the enclosure width."""
        return _UP.subtract(self.hi, self.lo)

    def as_json(self) -> dict[str, str]:
        """Return a JSON-serialisable record of the enclosure."""
        return {"lo": str(self.lo), "hi": str(self.hi), "width": str(self.width)}


#: An integrand for route B: the value plus interval extensions of the two
#: pure second partial derivatives.  The cell contribution is the exact Taylor
#: form ``area * (f(mid) + (H_xx dx^2 + H_zz dz^2) / 24)``: the gradient term
#: integrates to zero over a centred cell and the mixed second term does too,
#: so the enclosure is rigorous and second order in the mesh.
Integrand = tuple[
    Callable[[Interval, Interval], Interval],
    Callable[[Interval, Interval], Interval],
    Callable[[Interval, Interval], Interval],
]


def interval_integrate(
    integrand: Integrand,
    x_lo: Fraction,
    x_hi: Fraction,
    z_lo: Fraction,
    z_hi: Fraction,
    nx: int,
    nz: int,
) -> Interval:
    """Enclose a double integral by the exact second-order Taylor form.

    No antiderivative of the integrand is used, so a slip in the exact
    polynomial route cannot propagate here.
    """
    value, hxx, hzz = integrand
    total = Interval.exact(F(0))
    dx = (x_hi - x_lo) / nx
    dz = (z_hi - z_lo) / nz
    area = Interval.exact(dx * dz)
    weight_x = Interval.exact(dx * dx / 24)
    weight_z = Interval.exact(dz * dz / 24)
    for ix in range(nx):
        left = x_lo + ix * dx
        x_box = Interval(Interval.exact(left).lo, Interval.exact(left + dx).hi)
        x_mid = Interval.exact(left + dx / 2)
        for iz in range(nz):
            bottom = z_lo + iz * dz
            z_box = Interval(Interval.exact(bottom).lo, Interval.exact(bottom + dz).hi)
            z_mid = Interval.exact(bottom + dz / 2)
            bracket = (
                value(x_mid, z_mid)
                + hxx(x_box, z_box) * weight_x
                + hzz(x_box, z_box) * weight_z
            )
            total = total + bracket * area
    return total


def interval_expectation(
    integrand: Integrand,
    x_lo: Fraction = -ONE,
    x_hi: Fraction = ONE,
    nx: int = 200,
    nz: int = 200,
) -> Interval:
    """Enclose ``E[integrand(X, Z) 1{x_lo <= X <= x_hi}]`` (density ``1/4``)."""
    raw = interval_integrate(integrand, x_lo, x_hi, -ONE, ONE, nx, nz)
    return raw * Interval.exact(F(1, 4))


def _zero(_x: Interval, _z: Interval) -> Interval:
    return Interval.exact(F(0))


def _one(_x: Interval, _z: Interval) -> Interval:
    return Interval.exact(F(1))


def _lam(x_box: Interval, z_box: Interval) -> Interval:
    return Interval.exact(F(3)) * x_box * x_box - Interval.exact(F(1)) + z_box


#: ``E[1]`` -- cell mass.
IV_ONE: Integrand = (_one, _zero, _zero)
#: ``E[S_psi]``.
IV_PSI: Integrand = (lambda x, _z: x, _zero, _zero)
#: ``E[S_lambda]``; ``d^2/dx^2 = 6``.
IV_LAM: Integrand = (_lam, lambda _x, _z: Interval.exact(F(6)), _zero)
#: ``E[S_psi^2]``; ``d^2/dx^2 = 2``.
IV_PSI_SQ: Integrand = (lambda x, _z: x * x, lambda _x, _z: Interval.exact(F(2)), _zero)
#: ``E[S_psi S_lambda] = E[3 X^3 - X + X Z]``; ``d^2/dx^2 = 18 x``, ``d^2/dz^2 = 0``.
IV_CROSS: Integrand = (
    lambda x, z: x * _lam(x, z),
    lambda x, _z: Interval.exact(F(18)) * x,
    _zero,
)
#: ``E[S_lambda^2]``; ``d^2/dx^2 = 12 L + 72 x^2``, ``d^2/dz^2 = 2``.
IV_LAM_SQ: Integrand = (
    lambda x, z: _lam(x, z) * _lam(x, z),
    lambda x, z: Interval.exact(F(12)) * _lam(x, z) + Interval.exact(F(72)) * x * x,
    lambda _x, _z: Interval.exact(F(2)),
)


# --------------------------------------------------------------------------- #
# exact finite algebra
# --------------------------------------------------------------------------- #
def canonical_partitions(size: int, bins: int = N_BINS) -> Iterator[tuple[int, ...]]:
    """Yield each set partition into exactly ``bins`` nonempty cells once.

    Restricted-growth strings are the canonical representatives, so cell labels
    are quotiented by permutation exactly as the theorem requires.
    """
    if size < bins:
        return
    for labels in product(range(bins), repeat=size):
        if labels[0] != 0:
            continue
        if any(labels[index] > max(labels[:index]) + 1 for index in range(1, size)):
            continue
        if len(set(labels)) != bins:
            continue
        yield labels


def cell_moments(
    scores: Sequence[tuple[Fraction, Fraction]],
    weights: Sequence[Fraction],
    labels: Sequence[int],
    bins: int = N_BINS,
) -> tuple[list[Fraction], list[Fraction], list[Fraction]]:
    """Return per-cell mass and unnormalised first moments ``(W, m_psi, m_lam)``."""
    masses = [F(0)] * bins
    m_psi = [F(0)] * bins
    m_lam = [F(0)] * bins
    for (psi, lam), weight, label in zip(scores, weights, labels, strict=True):
        masses[label] += weight
        m_psi[label] += weight * psi
        m_lam[label] += weight * lam
    return masses, m_psi, m_lam


def binned_information(
    scores: Sequence[tuple[Fraction, Fraction]],
    weights: Sequence[Fraction],
    labels: Sequence[int],
    bins: int = N_BINS,
) -> list[list[Fraction]]:
    """Return ``I_q = sum_b m_b m_b^T / W_b`` in exact arithmetic."""
    masses, m_psi, m_lam = cell_moments(scores, weights, labels, bins)
    out = [[F(0), F(0)], [F(0), F(0)]]
    for mass, first, second in zip(masses, m_psi, m_lam, strict=True):
        if mass == 0:
            continue
        out[0][0] += first * first / mass
        out[0][1] += first * second / mass
        out[1][0] += first * second / mass
        out[1][1] += second * second / mass
    return out


def profiled_value(information: Sequence[Sequence[Fraction]]) -> tuple[Fraction, bool]:
    """Return ``(S_psi^+(I), regular)`` for a 2x2 binned information matrix.

    ``regular`` is ``I_lambda_lambda > 0``; at a singular nuisance block the
    DS11 pseudo-inverse extension is returned, which is exactly ``I_psi_psi``
    because a PSD block matrix with a zero nuisance block has zero cross term.
    """
    nuisance = information[1][1]
    if nuisance == 0:
        return information[0][0], False
    return information[0][0] - information[0][1] ** 2 / nuisance, True


def variational_profiled_value(
    scores: Sequence[tuple[Fraction, Fraction]],
    weights: Sequence[Fraction],
    labels: Sequence[int],
    bins: int = N_BINS,
) -> Fraction:
    """Return ``min_B sum_b W_b (mu_psi - B mu_lam)^2`` evaluated at its minimiser.

    Independent of :func:`profiled_value`: it minimises the DS11 variational
    form directly instead of forming a Schur complement.
    """
    masses, m_psi, m_lam = cell_moments(scores, weights, labels, bins)
    quadratic = F(0)
    linear = F(0)
    constant = F(0)
    for mass, first, second in zip(masses, m_psi, m_lam, strict=True):
        if mass == 0:
            continue
        constant += first * first / mass
        linear += first * second / mass
        quadratic += second * second / mass
    if quadratic == 0:
        return constant
    slope = linear / quadratic
    return constant - 2 * slope * linear + slope * slope * quadratic


def between_second_moment(
    values: Sequence[Fraction],
    weights: Sequence[Fraction],
    labels: Sequence[int],
    bins: int = N_BINS,
) -> Fraction:
    """Return ``sum_b (sum_{i in b} w_i v_i)^2 / W_b`` -- uncentered, about the origin."""
    masses = [F(0)] * bins
    sums = [F(0)] * bins
    for value, weight, label in zip(values, weights, labels, strict=True):
        masses[label] += weight
        sums[label] += weight * value
    return sum(
        (total * total / mass for total, mass in zip(sums, masses, strict=True) if mass != 0),
        F(0),
    )


def best_three_group_between(
    values: Sequence[Fraction], weights: Sequence[Fraction]
) -> tuple[Fraction, tuple[int, int]]:
    """Return the exact optimal three-group uncentered between-value and its cuts.

    One-dimensional contiguity: the maximiser groups the sorted values into
    three consecutive runs.  The contiguity reduction is verified against brute
    force over all canonical partitions by :func:`contiguity_check`.
    """
    order = sorted(range(len(values)), key=lambda index: values[index])
    sorted_values = [values[index] for index in order]
    sorted_weights = [weights[index] for index in order]
    size = len(order)
    prefix_mass = [F(0)] * (size + 1)
    prefix_sum = [F(0)] * (size + 1)
    for index in range(size):
        prefix_mass[index + 1] = prefix_mass[index] + sorted_weights[index]
        prefix_sum[index + 1] = prefix_sum[index] + sorted_weights[index] * sorted_values[index]
    best = None
    best_cuts = (1, 2)
    for first in range(1, size - 1):
        mass_a = prefix_mass[first]
        if mass_a == 0:
            continue
        term_a = prefix_sum[first] ** 2 / mass_a
        for second in range(first + 1, size):
            mass_b = prefix_mass[second] - prefix_mass[first]
            mass_c = prefix_mass[size] - prefix_mass[second]
            if mass_b == 0 or mass_c == 0:
                continue
            total = (
                term_a
                + (prefix_sum[second] - prefix_sum[first]) ** 2 / mass_b
                + (prefix_sum[size] - prefix_sum[second]) ** 2 / mass_c
            )
            if best is None or total > best:
                best = total
                best_cuts = (first, second)
    if best is None:
        raise ValueError("no feasible three-group split")
    return best, best_cuts


def contiguity_check(
    values: Sequence[Fraction], weights: Sequence[Fraction]
) -> tuple[Fraction, Fraction]:
    """Return ``(brute force optimum, contiguous optimum)`` for the scalar problem."""
    brute = max(
        between_second_moment(values, weights, labels)
        for labels in canonical_partitions(len(values))
    )
    contiguous, _ = best_three_group_between(values, weights)
    return brute, contiguous


def admissible_moves(labels: Sequence[int], bins: int = N_BINS) -> Iterator[tuple[int, int, int]]:
    """Yield ``(row, source, destination)`` for every source-nonempty relocation."""
    counts = [0] * bins
    for label in labels:
        counts[label] += 1
    for row, source in enumerate(labels):
        if counts[source] <= 1:
            continue
        for destination in range(bins):
            if destination != source:
                yield row, source, destination


def best_exchange_gain(
    scores: Sequence[tuple[Fraction, Fraction]],
    weights: Sequence[Fraction],
    labels: Sequence[int],
    bins: int = N_BINS,
) -> tuple[Fraction, tuple[int, int, int] | None, int]:
    """Return the best exact one-point profiled gain, its move, and the move count."""
    base, _ = profiled_value(binned_information(scores, weights, labels, bins))
    best = F(0)
    best_move: tuple[int, int, int] | None = None
    count = 0
    for row, source, destination in admissible_moves(labels, bins):
        count += 1
        moved = list(labels)
        moved[row] = destination
        value, _ = profiled_value(binned_information(scores, weights, moved, bins))
        if best_move is None or value - base > best:
            best = value - base
            best_move = (row, source, destination)
    return best, best_move, count


# --------------------------------------------------------------------------- #
# scalar distortion of Uniform[-1, 1] (the upper problem), exact
# --------------------------------------------------------------------------- #
def scalar_distortion(codebook: Sequence[Fraction]) -> Fraction:
    """Return ``E[min_b (X - c_b)^2]`` for ``X ~ Uniform[-1, 1]``, exactly.

    Cells are the nearest-point (Voronoi) cells of the codebook, which in one
    dimension are the intervals cut at consecutive midpoints; midpoints outside
    ``[-1, 1]`` are clamped, so codebooks with empty cells are handled.
    """
    points = sorted(codebook)
    edges = [-ONE]
    for left, right in zip(points, points[1:], strict=False):
        edges.append(min(ONE, max(-ONE, (left + right) / 2)))
    edges.append(ONE)
    total = F(0)
    for index, centre in enumerate(points):
        lo, hi = edges[index], edges[index + 1]
        if hi <= lo:
            continue
        # (1/2) * int_lo^hi (x - c)^2 dx
        total += ((hi - centre) ** 3 - (lo - centre) ** 3) / 6
    return total


def _finite_difference_gradient(
    function: Callable[[tuple[Fraction, ...]], Fraction],
    point: tuple[Fraction, ...],
    step: Fraction,
) -> list[Fraction]:
    """Return the exact gradient of a cubic via a five-point stencil."""
    gradient = []
    for index in range(len(point)):

        def shifted(delta: Fraction, index: int = index) -> Fraction:
            moved = list(point)
            moved[index] += delta
            return function(tuple(moved))

        gradient.append(
            (
                8 * (shifted(step) - shifted(-step))
                - (shifted(2 * step) - shifted(-2 * step))
            )
            / (12 * step)
        )
    return gradient


def _finite_difference_hessian(
    function: Callable[[tuple[Fraction, ...]], Fraction],
    point: tuple[Fraction, ...],
    step: Fraction,
) -> list[list[Fraction]]:
    """Return the exact Hessian of a cubic via central stencils."""
    size = len(point)
    hessian = [[F(0)] * size for _ in range(size)]

    def shifted(deltas: Sequence[Fraction]) -> Fraction:
        moved = [value + delta for value, delta in zip(point, deltas, strict=True)]
        return function(tuple(moved))

    zero = [F(0)] * size
    base = function(point)
    for i in range(size):
        plus = list(zero)
        plus[i] = step
        minus = list(zero)
        minus[i] = -step
        hessian[i][i] = (shifted(plus) - 2 * base + shifted(minus)) / (step * step)
        for j in range(i + 1, size):
            pp, pm, mp, mm = (list(zero) for _ in range(4))
            pp[i], pp[j] = step, step
            pm[i], pm[j] = step, -step
            mp[i], mp[j] = -step, step
            mm[i], mm[j] = -step, -step
            value = (shifted(pp) - shifted(pm) - shifted(mp) + shifted(mm)) / (4 * step * step)
            hessian[i][j] = value
            hessian[j][i] = value
    return hessian


def leading_minors(matrix: Sequence[Sequence[Fraction]]) -> list[Fraction]:
    """Return the leading principal minors of a square rational matrix."""
    size = len(matrix)
    minors = []
    for order in range(1, size + 1):
        block = [row[:order] for row in matrix[:order]]
        minors.append(_determinant(block))
    return minors


def _determinant(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    size = len(matrix)
    if size == 1:
        return matrix[0][0]
    if size == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    total = F(0)
    for column in range(size):
        minor = [
            [row[index] for index in range(size) if index != column] for row in matrix[1:]
        ]
        total += (-1) ** column * matrix[0][column] * _determinant(minor)
    return total


def psd_certificate(matrix: Sequence[Sequence[Fraction]], floor: Fraction) -> bool:
    """Return whether ``matrix - floor * I`` has strictly positive leading minors."""
    shifted = [
        [value - (floor if row == column else F(0)) for column, value in enumerate(line)]
        for row, line in enumerate(matrix)
    ]
    return all(minor > 0 for minor in leading_minors(shifted))


def lambda_min_at_least(information: Sequence[Sequence[Fraction]], floor: Fraction) -> bool:
    """Return whether ``lambda_min(I) >= floor`` by an exact rational test."""
    shifted = [
        [value - (floor if row == column else F(0)) for column, value in enumerate(line)]
        for row, line in enumerate(information)
    ]
    return shifted[0][0] >= 0 and _determinant(shifted) >= 0


# --------------------------------------------------------------------------- #
# deterministic sampling from the law (rational grid emulation)
# --------------------------------------------------------------------------- #
GRID_BITS = 30
GRID = 1 << GRID_BITS


class Lcg:
    """A 64-bit linear congruential generator (Knuth's MMIX constants)."""

    def __init__(self, seed: int) -> None:
        self.state = seed % (1 << 64)

    def next_uint32(self) -> int:
        """Return the next 32-bit output."""
        self.state = (6364136223846793005 * self.state + 1442695040888963407) % (1 << 64)
        return (self.state >> 32) & 0xFFFFFFFF


def sample_law(size: int, seed: int) -> list[tuple[Fraction, Fraction]]:
    """Return ``size`` exact rational draws from the grid emulation of the law."""
    rng = Lcg(seed)
    rows = []
    for _ in range(size):
        x_raw = rng.next_uint32() % GRID
        z_raw = rng.next_uint32() % GRID
        x_value = F(2 * x_raw - GRID + 1, GRID)
        z_value = F(2 * z_raw - GRID + 1, GRID)
        rows.append((x_value, 3 * x_value * x_value - 1 + z_value))
    return rows


def population_labels(scores: Sequence[tuple[Fraction, Fraction]]) -> tuple[int, ...]:
    """Return the labels induced by the population cuts ``+/- 1/3`` on ``S_psi``."""
    return tuple(0 if psi < -CUT else (1 if psi < CUT else 2) for psi, _ in scores)


# --------------------------------------------------------------------------- #
# provenance
# --------------------------------------------------------------------------- #
def _git(*arguments: str) -> str:
    try:
        return subprocess.run(  # noqa: S603
            ["git", *arguments],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):  # pragma: no cover - provenance only
        return "unavailable"


def provenance() -> dict[str, object]:
    """Return the reproducibility block stamped into every artifact."""
    source = Path(__file__).resolve()
    return {
        "audit": AUDIT_ID,
        "script": str(source.relative_to(WORKSPACE)),
        "script_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "git_revision": _git("rev-parse", "HEAD"),
        "git_status_clean": _git("status", "--porcelain") == "",
        "python": sys.version,
        "platform": platform.platform(),
        "decimal_precision": DECIMAL_PRECISION,
        "seed_base": SEED_BASE,
        "seed_formula": "seed(n, rep) = SEED_BASE + 1000 * n + rep",
        "grid_denominator": GRID,
        "generated_utc": datetime.now(UTC).isoformat(),
    }


def _json_default(value: object) -> str:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"cannot serialise {type(value)!r}")


def write_artifact(name: str, payload: dict[str, object]) -> Path:
    """Write one artifact record and return its path."""
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=_json_default) + "\n")
    return path


# --------------------------------------------------------------------------- #
# interval helpers used by the (M4) sweep
# --------------------------------------------------------------------------- #
def rational_sqrt_upper(value: Fraction, digits: int = 30) -> Fraction:
    """Return a rational upper bound of ``sqrt(value)`` with bounded denominator.

    ``sqrt(p / q) = sqrt(p q) / q`` is bracketed with :func:`math.isqrt`, so the
    denominator never grows -- unlike a rational Newton iteration, which squares
    it at every step.
    """
    if value < 0:
        raise ValueError("negative radicand")
    scale = 10**digits
    numerator = value.numerator * value.denominator * scale * scale
    root = isqrt(numerator) + 1
    bound = F(root, value.denominator * scale)
    if bound * bound < value:  # pragma: no cover - isqrt rounds down
        raise AssertionError("sqrt upper bound failed")
    return bound


def _section_length(centre: Fraction, half: Fraction) -> Fraction:
    """Return ``|[centre - half, centre + half] cap [-1, 1]|``."""
    lo = max(-ONE, centre - half)
    hi = min(ONE, centre + half)
    return max(F(0), hi - lo)


def _parabola_range(
    quad: Fraction, lin: Fraction, const: Fraction, x_lo: Fraction, x_hi: Fraction
) -> tuple[Fraction, Fraction]:
    """Return the exact range of ``quad x^2 + lin x + const`` on ``[x_lo, x_hi]``."""

    def value(x: Fraction) -> Fraction:
        return quad * x * x + lin * x + const

    candidates = [value(x_lo), value(x_hi)]
    if quad != 0:
        vertex = -lin / (2 * quad)
        if x_lo <= vertex <= x_hi:
            candidates.append(value(vertex))
    return min(candidates), max(candidates)


def slab_mass_exact(
    p: Fraction, q: Fraction, offset: Fraction, tau: Fraction, nx: int = 4000
) -> tuple[Fraction, Fraction]:
    """Return exact rational bounds on ``P(|p S_psi + q S_lambda - offset| <= tau)``.

    The ``z``-section of the slab is an interval of constant half-width
    ``tau / |q|`` centred at ``(offset - A(x)) / q`` with
    ``A(x) = 3 q x^2 + p x - q``.  The clipped section length is a unimodal
    function of that centre, so its exact minimum and maximum over an ``x``
    cell follow from the exact range of a parabola -- no antiderivative and no
    floating point anywhere.
    """
    if q == 0:
        if p == 0:
            raise ValueError("degenerate direction")
        length = min(F(2), 2 * tau / abs(p))
        mass = length * 2 / 4
        return mass, mass
    half = abs(tau / q)
    lower = F(0)
    upper = F(0)
    dx = 2 * ONE / nx
    for index in range(nx):
        x_lo = -ONE + index * dx
        x_hi = x_lo + dx
        a_lo, a_hi = _parabola_range(3 * q, p, -q, x_lo, x_hi)
        centre_lo = (offset - a_hi) / q
        centre_hi = (offset - a_lo) / q
        if centre_lo > centre_hi:
            centre_lo, centre_hi = centre_hi, centre_lo
        ends = (_section_length(centre_lo, half), _section_length(centre_hi, half))
        cell_min = min(ends)
        # The clipped length is unimodal in the centre with its peak at 0.
        if centre_lo <= 0 <= centre_hi:
            cell_max = _section_length(F(0), half)
        else:
            cell_max = max(ends)
        lower += cell_min * dx
        upper += cell_max * dx
    return lower / 4, upper / 4


# --------------------------------------------------------------------------- #
# fast exact scalar upper problem for equal weights on the rational grid
# --------------------------------------------------------------------------- #
def best_three_group_equal_weight(units: Sequence[int]) -> tuple[Fraction, tuple[int, int]]:
    """Return the exact optimal three-group between-value for equal weights.

    ``units`` are the grid integers of the sorted ``S_psi`` sample; the returned
    value is ``max_z sum_b (sum_{i in b} w_i x_i)^2 / W_b`` in real units.
    Comparisons are integer cross-multiplications, so no floating point or
    ``Fraction`` normalisation enters the inner loop.
    """
    size = len(units)
    prefix = [0] * (size + 1)
    for index, value in enumerate(units):
        prefix[index + 1] = prefix[index] + value
    total = prefix[size]
    best_num = None
    best_den = 1
    best_cuts = (1, 2)
    for first in range(1, size - 1):
        head = prefix[first]
        head_sq = head * head
        for second in range(first + 1, size):
            mid = prefix[second] - head
            tail = total - prefix[second]
            width_b = second - first
            width_c = size - second
            num = (
                head_sq * width_b * width_c
                + mid * mid * first * width_c
                + tail * tail * first * width_b
            )
            den = first * width_b * width_c
            if best_num is None or num * best_den > best_num * den:
                best_num, best_den, best_cuts = num, den, (first, second)
    if best_num is None:
        raise ValueError("no feasible three-group split")
    return F(best_num, best_den) / (size * GRID * GRID), best_cuts


# --------------------------------------------------------------------------- #
# subcommand: population
# --------------------------------------------------------------------------- #
CELL_EDGES = ((-ONE, -CUT), (-CUT, CUT), (CUT, ONE))


def population_route_a() -> dict[str, object]:
    """Recompute every population quantity of DS18 from the law definition."""
    psi_sq = pmul(S_PSI, S_PSI)
    lam_sq = pmul(S_LAM, S_LAM)
    cross = pmul(S_PSI, S_LAM)
    full = [
        [expectation(psi_sq), expectation(cross)],
        [expectation(cross), expectation(lam_sq)],
    ]
    masses = [expectation(ONE_POLY, lo, hi) for lo, hi in CELL_EDGES]
    m_psi = [expectation(S_PSI, lo, hi) for lo, hi in CELL_EDGES]
    m_lam = [expectation(S_LAM, lo, hi) for lo, hi in CELL_EDGES]
    mu_psi = [m / w for m, w in zip(m_psi, masses, strict=True)]
    mu_lam = [m / w for m, w in zip(m_lam, masses, strict=True)]
    information = [[F(0), F(0)], [F(0), F(0)]]
    for mass, first, second in zip(masses, mu_psi, mu_lam, strict=True):
        information[0][0] += mass * first * first
        information[0][1] += mass * first * second
        information[1][0] += mass * first * second
        information[1][1] += mass * second * second
    value, regular = profiled_value(information)
    full_value, _ = profiled_value(full)

    # Off-(L) witness: E[S_lambda | X] = 3 X^2 - 1 is verified by testing the
    # defining orthogonality against a polynomial basis in X.
    candidate = {(2, 0): F(3), (0, 0): F(-1)}
    residuals = [
        expectation(pmul(padd(S_LAM, pscale(candidate, F(-1))), {(power, 0): F(1)}))
        for power in range(6)
    ]
    off_class = [expectation(pmul(candidate, {(power, 0): F(1)})) for power in range(3)]

    # DS17.4 root residual E[h(T_0) S_lambda] with h the step function of cell means.
    root_residual = sum(
        (mass * t * lam for mass, t, lam in zip(masses, mu_psi, mu_lam, strict=True)), F(0)
    )

    distortion = scalar_distortion(mu_psi)
    scalar_upper = expectation(psi_sq) - distortion
    two_cell = expectation(psi_sq) - scalar_distortion([F(-1, 2), F(1, 2)])

    step = F(1, 97)
    gradient = _finite_difference_gradient(
        lambda point: scalar_distortion(list(point)), tuple(mu_psi), step
    )
    gradient_alt = _finite_difference_gradient(
        lambda point: scalar_distortion(list(point)), tuple(mu_psi), F(1, 131)
    )
    hessian = _finite_difference_hessian(
        lambda point: scalar_distortion(list(point)), tuple(mu_psi), step
    )
    hessian_alt = _finite_difference_hessian(
        lambda point: scalar_distortion(list(point)), tuple(mu_psi), F(1, 131)
    )
    curvature_floor = F(1, 7)
    exact_lambda_min = F(1, 6)
    shifted = [
        [value - (exact_lambda_min if row == column else F(0)) for column, value in enumerate(line)]
        for row, line in enumerate(hessian)
    ]

    separation = min(
        abs(mu_psi[first] - mu_psi[second])
        for first, second in combinations(range(N_BINS), 2)
    )
    return {
        "full_information": full,
        "full_profiled_value": full_value,
        "full_regression_slope": (
            full[0][1] / full[1][1] if full[1][1] != 0 else None
        ),
        "cell_edges": [[str(lo), str(hi)] for lo, hi in CELL_EDGES],
        "cell_masses": masses,
        "cell_means_psi": mu_psi,
        "cell_means_lambda": mu_lam,
        "binned_information": information,
        "profiled_value": value,
        "binned_regular": regular,
        "ds_retention": value / full_value,
        "root_residual": root_residual,
        "conditional_nuisance_mean_polynomial": "3 x^2 - 1",
        "conditional_orthogonality_residuals": residuals,
        "conditional_nuisance_moments": off_class,
        "scalar_distortion_at_optimum": distortion,
        "scalar_upper_v3": scalar_upper,
        "scalar_upper_v2": two_cell,
        "scalar_gradient": gradient,
        "scalar_gradient_alternate_step": gradient_alt,
        "scalar_hessian": hessian,
        "scalar_hessian_alternate_step": hessian_alt,
        "scalar_hessian_psd_floor": curvature_floor,
        "scalar_hessian_psd_certificate": psd_certificate(hessian, curvature_floor),
        "scalar_hessian_steps_agree": hessian == hessian_alt,
        "scalar_gradient_steps_agree": gradient == gradient_alt,
        "scalar_hessian_lambda_min_exact": exact_lambda_min,
        "scalar_hessian_lambda_min_determinant": _determinant(shifted),
        "scalar_hessian_lambda_min_psd": all(
            _determinant([row[:order] for row in shifted[:order]]) >= 0 for order in (1, 2, 3)
        ),
        "margins": {
            "min_mass": min(masses),
            "lambda_min_at_least_one_quarter": lambda_min_at_least(information, F(1, 4)),
            "projected_separation": separation,
            "c0": F(1, 4),
            "kappa": F(1, 4),
            "gamma": F(1, 2),
            "mass_slack": min(masses) - F(1, 4),
            "separation_slack": separation - F(1, 2),
        },
    }


def scalar_codebook_grid_scan(spacing: Fraction) -> dict[str, object]:
    """Scan every sorted rational codebook on a lattice for a rival optimum."""
    steps = int(2 / spacing)
    lattice = [-ONE + index * spacing for index in range(steps + 1)]
    optimum = F(1, 27)
    best_rival = None
    best_rival_codebook: list[str] = []
    count = 0
    below = 0
    target = [F(-2, 3), F(0), F(2, 3)]
    for triple in combinations(lattice, N_BINS):
        count += 1
        distortion = scalar_distortion(list(triple))
        if distortion < optimum:
            below += 1
        if list(triple) == target:
            continue
        if best_rival is None or distortion < best_rival:
            best_rival = distortion
            best_rival_codebook = [str(value) for value in triple]
    return {
        "spacing": str(spacing),
        "codebooks_scanned": count,
        "codebooks_below_optimum": below,
        "best_non_optimal_distortion": best_rival,
        "best_non_optimal_codebook": best_rival_codebook,
        "optimum": optimum,
        "target_on_lattice": all(value in lattice for value in target),
    }


def population_route_b(nx: int = 300, nz: int = 300) -> tuple[dict[str, object], dict[str, Interval]]:
    """Enclose the same population quantities with interval arithmetic."""
    enclosures = {
        "full_psi_psi": interval_expectation(IV_PSI_SQ, nx=nx, nz=1),
        "full_psi_lambda": interval_expectation(IV_CROSS, nx=nx, nz=1),
        "full_lambda_lambda": interval_expectation(IV_LAM_SQ, nx=nx, nz=nz),
    }
    for index, (lo, hi) in enumerate(CELL_EDGES):
        enclosures[f"mass_{index}"] = interval_expectation(IV_ONE, lo, hi, nx=4, nz=1)
        enclosures[f"m_psi_{index}"] = interval_expectation(IV_PSI, lo, hi, nx=4, nz=1)
        enclosures[f"m_lambda_{index}"] = interval_expectation(IV_LAM, lo, hi, nx=nx, nz=1)
    return {name: enclosure.as_json() for name, enclosure in enclosures.items()}, enclosures


def population_monte_carlo(size: int, seed: int) -> dict[str, object]:
    """Return an independent Monte-Carlo cross-check of the population moments.

    Everything is accumulated in integers over the common grid denominator, so
    the check is exact for the grid emulation and costs no rational
    normalisation.
    """
    rng = Lcg(seed)
    sum_psi_sq = 0
    sum_cross = 0
    sum_lam_sq = 0
    counts = [0, 0, 0]
    cell_psi = [0, 0, 0]
    cell_lam = [0, 0, 0]
    for _ in range(size):
        vx = 2 * (rng.next_uint32() % GRID) - GRID + 1
        vz = 2 * (rng.next_uint32() % GRID) - GRID + 1
        # S_psi = vx / GRID, S_lambda = vl / GRID^2 with vl integral.
        vl = 3 * vx * vx - GRID * GRID + vz * GRID
        sum_psi_sq += vx * vx
        sum_cross += vx * vl
        sum_lam_sq += vl * vl
        cell = 0 if 3 * vx < -GRID else (1 if 3 * vx < GRID else 2)
        counts[cell] += 1
        cell_psi[cell] += vx
        cell_lam[cell] += vl
    grid = F(GRID)
    full = [
        [F(sum_psi_sq, size) / grid**2, F(sum_cross, size) / grid**3],
        [F(sum_cross, size) / grid**3, F(sum_lam_sq, size) / grid**4],
    ]
    information = [[F(0), F(0)], [F(0), F(0)]]
    for count, psi_sum, lam_sum in zip(counts, cell_psi, cell_lam, strict=True):
        if count == 0:
            continue
        psi_mean = F(psi_sum, count) / grid
        lam_mean = F(lam_sum, count) / grid**2
        mass = F(count, size)
        information[0][0] += mass * psi_mean * psi_mean
        information[0][1] += mass * psi_mean * lam_mean
        information[1][0] += mass * psi_mean * lam_mean
        information[1][1] += mass * lam_mean * lam_mean
    value, _ = profiled_value(information)
    return {
        "size": size,
        "seed": seed,
        "full_information": [[float(entry) for entry in row] for row in full],
        "cell_masses": [float(F(count, size)) for count in counts],
        "binned_information": [[float(entry) for entry in row] for row in information],
        "profiled_value": float(value),
        "ds_retention": float(value / (full[0][0] - full[0][1] ** 2 / full[1][1])),
    }


def m4_sweep(nx: int = 4000) -> dict[str, object]:
    """Sweep slab masses exactly and test them against the registered (M4) modulus.

    The registered modulus is ``phi(t) = min(1, sqrt(29) t / 2)``, which comes
    from ``area(slab cap support) <= 2 t diam`` with ``diam`` the diameter of
    the bounding rectangle ``[-1, 1] x [-2, 3]``.  The support's own diameter is
    strictly smaller but is *not* ``sqrt(26)``: the farthest pair is a corner
    ``(1, 3)`` against a point of the lower arc ``y = 3 x^2 - 2`` at the root of
    ``18 x^3 - 29 x - 1 = 0`` near ``-0.0345``, giving ``diam^2 = 26.0345...``.
    The rational bound ``diam^2 <= 2609 / 100`` is what this sweep tests as the
    sharper constant; it is a measured refinement, not a registered claim.
    """
    directions = [
        (F(1), F(0)),
        (F(0), F(1)),
        (F(1), F(1)),
        (F(1), F(-1)),
        (F(2), F(1)),
        (F(1), F(2)),
        (F(3), F(-1)),
        (F(1), F(-3)),
        (F(5), F(2)),
        (F(-2), F(5)),
        (F(1), F(-8)),
        (F(8), F(1)),
    ]
    offsets = [F(-2), F(-3, 2), F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(3, 2), F(2), F(5, 2)]
    taus = [F(1, 4), F(1, 10), F(1, 40), F(1, 200)]
    records = []
    violations = 0
    sharper_violations = 0
    worst_ratio = F(0)
    worst_record: dict[str, str] = {}
    modulus = rational_sqrt_upper(F(29)) / 2
    sharper = rational_sqrt_upper(F(2609, 100)) / 2
    for p, q in directions:
        norm_upper = rational_sqrt_upper(p * p + q * q)
        for offset in offsets:
            for tau in taus:
                lower, upper = slab_mass_exact(p, q, offset, tau, nx=nx)
                half_width = tau / norm_upper
                bound = min(ONE, modulus * half_width)
                sharp_bound = min(ONE, sharper * half_width)
                ratio = upper / half_width
                if ratio > worst_ratio:
                    worst_ratio = ratio
                    worst_record = {
                        "direction": f"({p}, {q})",
                        "offset": str(offset),
                        "tau": str(tau),
                    }
                ok = upper <= bound
                violations += 0 if ok else 1
                sharper_violations += 0 if upper <= sharp_bound else 1
                records.append(
                    {
                        "direction": [str(p), str(q)],
                        "offset": str(offset),
                        "tau": str(tau),
                        "unit_half_width": float(half_width),
                        "mass_lower": float(lower),
                        "mass_upper": float(upper),
                        "enclosure_width": float(upper - lower),
                        "phi_bound": float(bound),
                        "satisfied": ok,
                    }
                )
    cross_check = []
    for p, q in ((F(1), F(2)), (F(3), F(-1)), (F(0), F(1))):
        for tau in (F(1, 4), F(1, 10)):
            lower, upper = slab_mass_exact(p, q, F(0), tau, nx=nx)
            rng = Lcg(SEED_BASE + 7)
            hits = 0
            draws = 200_000
            for _ in range(draws):
                vx = 2 * (rng.next_uint32() % GRID) - GRID + 1
                vz = 2 * (rng.next_uint32() % GRID) - GRID + 1
                # |p x + q lambda| <= tau, cleared of denominators.
                left = p * vx * GRID + q * (3 * vx * vx - GRID * GRID + vz * GRID)
                if abs(left) <= tau * GRID * GRID:
                    hits += 1
            cross_check.append(
                {
                    "direction": [str(p), str(q)],
                    "tau": str(tau),
                    "exact_lower": float(lower),
                    "exact_upper": float(upper),
                    "monte_carlo": hits / draws,
                    "monte_carlo_draws": draws,
                }
            )
    return {
        "subdivisions": nx,
        "interval_route_cross_check": cross_check,
        "slabs_tested": len(records),
        "violations": violations,
        "violations_against_measured_support_diameter_constant": sharper_violations,
        "worst_mass_over_half_width": float(worst_ratio),
        "worst_slab": worst_record,
        "registered_constant_sqrt29_over_2": float(modulus),
        "measured_support_diameter_constant": float(sharper),
        "support_diameter_squared_upper_bound": "2609/100",
        "support_diameter_squared_measured": 26.034495502232028,
        "support_diameter_stationarity": "corner (1, 3) against y = 3x^2 - 2 at the root of 18 x^3 - 29 x - 1",
        "bounding_rectangle_diameter_squared": 29,
        "records_retained": "all violations plus the 25 largest mass/half-width ratios",
        "records": (
            [row for row in records if not row["satisfied"]]
            + sorted(
                (row for row in records if row["satisfied"]),
                key=lambda row: -row["mass_upper"] / row["unit_half_width"],
            )[:25]
        ),
    }


# --------------------------------------------------------------------------- #
# exact identity battery and the serialized boundary fixture
# --------------------------------------------------------------------------- #
FIXTURE_X = (F(-3, 4), F(-1, 4), F(1, 4), F(3, 4))
FIXTURE_Z = (F(-1), F(-3, 4), F(1), F(1))


def law_scores(
    xs: Sequence[Fraction], zs: Sequence[Fraction]
) -> list[tuple[Fraction, Fraction]]:
    """Return score rows built from the law, never copied from a fixture."""
    return [(x, 3 * x * x - 1 + z) for x, z in zip(xs, zs, strict=True)]


def sandwich_report(
    scores: Sequence[tuple[Fraction, Fraction]],
    weights: Sequence[Fraction],
    labels: Sequence[int],
) -> dict[str, object]:
    """Return the exact profiled/between/scalar-upper chain for one labeling."""
    information = binned_information(scores, weights, labels)
    value, regular = profiled_value(information)
    variational = variational_profiled_value(scores, weights, labels)
    between = between_second_moment([psi for psi, _ in scores], weights, labels)
    upper, _ = best_three_group_between([psi for psi, _ in scores], weights)
    return {
        "information": information,
        "profiled_value": value,
        "regular": regular,
        "variational_value": variational,
        "variational_matches_schur": variational == value,
        "between": between,
        "scalar_upper": upper,
        "profiled_le_between": value <= between,
        "between_le_upper": between <= upper,
    }


def exact_battery() -> dict[str, object]:
    """Rebuild the boundary fixture and every exact identity it is meant to pin."""
    fixture_path = (
        RESEARCH / "COUNTEREXAMPLES" / "CE-DS-NONCENTERED-POPULATION-CUT-UNSTABLE-001.json"
    )
    fixture = json.loads(fixture_path.read_text())
    scores = law_scores(FIXTURE_X, FIXTURE_Z)
    weights = [F(1, 4)] * 4
    stored = [tuple(F(entry) for entry in row) for row in fixture["scores"]]
    before = tuple(fixture["labels_before"])
    after = tuple(fixture["labels_after_or_optimum"])

    derived_before = population_labels(scores)
    value_before, _ = profiled_value(binned_information(scores, weights, before))
    value_after, _ = profiled_value(binned_information(scores, weights, after))

    regular_values = []
    singular_values = []
    for labels in canonical_partitions(4):
        information = binned_information(scores, weights, labels)
        value, regular = profiled_value(information)
        (regular_values if regular else singular_values).append((value, labels))
    best_regular = max(regular_values)

    gain, move, move_count = best_exchange_gain(scores, weights, before)
    after_gain, after_move, after_moves = best_exchange_gain(scores, weights, after)

    three_row = law_scores(FIXTURE_X[:3], FIXTURE_Z[:3])
    three_partitions = list(canonical_partitions(3))
    three_moves = sum(1 for _ in admissible_moves(three_partitions[0]))

    permuted = tuple({0: 2, 1: 0, 2: 1}[label] for label in before)
    permuted_value, _ = profiled_value(binned_information(scores, weights, permuted))

    return {
        "fixture": fixture["id"],
        "scores_rebuilt_from_law": scores,
        "scores_match_fixture": [list(row) for row in scores] == [list(row) for row in stored],
        "weighted_score_mean": [
            sum((w * row[column] for w, row in zip(weights, scores, strict=True)), F(0))
            for column in range(2)
        ],
        "population_labels_match_fixture": derived_before == before,
        "objective_before": value_before,
        "objective_after": value_after,
        "objective_before_matches": value_before == F(fixture["objective_before"]),
        "objective_after_matches": value_after == F(fixture["objective_after"]),
        "exact_gain": value_after - value_before,
        "exact_gain_matches": (
            value_after - value_before == F(fixture["exact_quantities"]["exact_gain"])
        ),
        "best_move_from_population_labels": move,
        "best_gain_from_population_labels": gain,
        "admissible_moves_from_population_labels": move_count,
        "admissible_moves_matches_fixture": (
            move_count
            == fixture["exact_quantities"]["admissible_nonempty_preserving_one_point_moves"]
        ),
        "canonical_partitions_at_four": len(regular_values) + len(singular_values),
        "singular_labelings_at_four": len(singular_values),
        "global_regular_optimum": best_regular[0],
        "global_regular_optimum_labels": list(best_regular[1]),
        "global_optimum_is_post_move_labeling": best_regular[1] == after,
        "post_move_best_gain": after_gain,
        "post_move_is_exchange_stable": after_gain <= 0,
        "post_move_admissible_moves": after_moves,
        "support_minimality": {
            "n_equals_three_canonical_partitions": len(three_partitions),
            "n_equals_three_admissible_moves": three_moves,
            "n_equals_three_scores": three_row,
            "n_below_three_feasible": False,
        },
        "label_permutation_invariance": permuted_value == value_before,
        "sandwich_before": sandwich_report(scores, weights, before),
        "sandwich_after": sandwich_report(scores, weights, after),
    }


# --------------------------------------------------------------------------- #
# adversarial families
# --------------------------------------------------------------------------- #
def midpoint_sample(size: int) -> tuple[list[tuple[Fraction, Fraction]], list[Fraction]]:
    """Return a deterministic symmetric grid sample of the law."""
    xs = [F(2 * index + 1 - size, size) for index in range(size)]
    zs = [F(2 * ((index * 5 + 2) % size) + 1 - size, size) for index in range(size)]
    return law_scores(xs, zs), [F(1, size)] * size


def product_sample(size: int) -> tuple[list[tuple[Fraction, Fraction]], list[Fraction]]:
    """Return a product-grid sample of the law truncated to ``size`` rows."""
    grid = [F(-3, 4), F(-1, 4), F(1, 4), F(3, 4)]
    rows = [(x, z) for x in grid for z in grid]
    xs = [row[0] for row in rows[:size]]
    zs = [row[1] for row in rows[:size]]
    return law_scores(xs, zs), [F(1, size)] * size


def lcg_sample(size: int, rep: int) -> tuple[list[tuple[Fraction, Fraction]], list[Fraction]]:
    """Return a coarse-grid LCG sample with the deterministic seed formula."""
    rng = Lcg(SEED_BASE + 1000 * size + rep)
    coarse = 1 << 10
    xs = []
    zs = []
    for _ in range(size):
        xs.append(F(2 * (rng.next_uint32() % coarse) - coarse + 1, coarse))
        zs.append(F(2 * (rng.next_uint32() % coarse) - coarse + 1, coarse))
    return law_scores(xs, zs), [F(1, size)] * size


def adversarial_cases() -> list[tuple[str, list[tuple[Fraction, Fraction]], list[Fraction]]]:
    """Return the hand-built boundary tables the theorem's assumptions exclude."""
    cases: list[tuple[str, list[tuple[Fraction, Fraction]], list[Fraction]]] = []

    xs = [F(-3, 4), F(-1, 4), F(1, 4), F(3, 4), F(-1, 2), F(1, 2)]
    zs = [F(-1), F(-3, 4), F(1), F(1), F(1, 2), F(-1, 2)]
    cases.append(("unequal_weights", law_scores(xs, zs), [F(1, 12), F(1, 12), F(1, 3), F(1, 4), F(1, 8), F(1, 8)]))
    cases.append(("zero_weight_row", law_scores(xs, zs), [F(1, 5), F(1, 5), F(1, 5), F(1, 5), F(1, 5), F(0)]))

    duplicate_x = [F(-1, 2), F(-1, 2), F(1, 2), F(1, 2), F(0)]
    duplicate_z = [F(1, 4), F(1, 4), F(-1, 4), F(-1, 4), F(1, 3)]
    cases.append(("duplicate_atoms", law_scores(duplicate_x, duplicate_z), [F(1, 5)] * 5))

    tie_x = [-CUT, -CUT, CUT, CUT, F(0), F(-1)]
    tie_z = [F(1, 2), F(-1, 2), F(1, 3), F(-1, 3), F(0), F(1, 5)]
    cases.append(("exact_ties_at_cuts", law_scores(tie_x, tie_z), [F(1, 6)] * 6))

    # Every cell nuisance sum vanishes: an exactly singular binned nuisance block.
    singular_x = [F(-3, 4), F(-3, 4), F(-1, 4), F(-1, 4), F(3, 4), F(3, 4)]
    singular_z = [F(-11, 16) + F(1, 2), F(-11, 16) - F(1, 2), F(13, 16) + F(1, 4), F(13, 16) - F(1, 4), F(-11, 16) + F(1, 8), F(-11, 16) - F(1, 8)]
    cases.append(("singular_nuisance_pairs", law_scores(singular_x, singular_z), [F(1, 6)] * 6))

    tiny_x = [F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(99, 100)]
    tiny_z = [F(-1), F(1, 2), F(-1, 3), F(1, 4), F(1), F(-99, 100)]
    cases.append(("tiny_and_singleton_cells", law_scores(tiny_x, tiny_z), [F(1, 6)] * 6))

    near_x = [F(-1), F(-999, 1000), F(0), F(1, 1000), F(1), F(999, 1000)]
    near_z = [F(0), F(1, 1000), F(0), F(-1, 1000), F(0), F(-1, 1000)]
    cases.append(("near_singular_information", law_scores(near_x, near_z), [F(1, 6)] * 6))
    return cases


def scan_partitions(
    scores: Sequence[tuple[Fraction, Fraction]],
    weights: Sequence[Fraction],
    check_contiguity: bool = False,
) -> dict[str, object]:
    """Enumerate every canonical partition of one table and test the DS18 chain."""
    values = [psi for psi, _ in scores]
    upper, _ = best_three_group_between(values, weights)
    partitions = 0
    regular = 0
    singular = 0
    sandwich_violations = 0
    variational_violations = 0
    best_regular: tuple[Fraction, tuple[int, ...]] | None = None
    best_singular: Fraction | None = None
    for labels in canonical_partitions(len(scores)):
        partitions += 1
        information = binned_information(scores, weights, labels)
        value, is_regular = profiled_value(information)
        between = between_second_moment(values, weights, labels)
        if not (value <= between <= upper):
            sandwich_violations += 1
        if is_regular:
            regular += 1
            if variational_profiled_value(scores, weights, labels) != value:
                variational_violations += 1
            if best_regular is None or value > best_regular[0]:
                best_regular = (value, labels)
        else:
            singular += 1
            if best_singular is None or value > best_singular:
                best_singular = value
    report: dict[str, object] = {
        "rows": len(scores),
        "canonical_partitions": partitions,
        "regular_partitions": regular,
        "singular_partitions": singular,
        "sandwich_violations": sandwich_violations,
        "variational_violations": variational_violations,
        "scalar_upper": upper,
        "global_regular_value": None if best_regular is None else best_regular[0],
        "global_regular_labels": None if best_regular is None else list(best_regular[1]),
        "best_singular_pseudo_inverse_value": best_singular,
        "singular_beats_regular": (
            best_singular is not None
            and best_regular is not None
            and best_singular > best_regular[0]
        ),
    }
    if check_contiguity:
        brute, contiguous = contiguity_check(values, weights)
        report["contiguity_brute_force"] = brute
        report["contiguity_dynamic_program"] = contiguous
        report["contiguity_agrees"] = brute == contiguous
    return report


# --------------------------------------------------------------------------- #
# boundary witness: a singular one-point destination beats the regular optimum
# --------------------------------------------------------------------------- #
#: Support-minimal table on the named law whose unique nuisance-singular
#: labeling carries a DS11 pseudo-inverse value strictly above the exact global
#: optimum over regular labelings, reachable by one admissible relocation from
#: every global regular optimum.
WITNESS_X = (F(-1), F(0), F(1, 2), F(1, 2))
WITNESS_Z = (F(-1), F(1), F(-3, 4), F(1, 4))


def _canonical(labels: Sequence[int]) -> tuple[int, ...]:
    mapping: dict[int, int] = {}
    out = []
    for label in labels:
        if label not in mapping:
            mapping[label] = len(mapping)
        out.append(mapping[label])
    return tuple(out)


def singular_destination_witness() -> dict[str, object]:
    """Return the full exact anatomy of the singular-destination boundary table."""
    scores = law_scores(WITNESS_X, WITNESS_Z)
    weights = [F(1, 4)] * 4
    values = [psi for psi, _ in scores]
    table = []
    for labels in canonical_partitions(4):
        information = binned_information(scores, weights, labels)
        value, regular = profiled_value(information)
        table.append(
            {
                "labels": list(labels),
                "information": information,
                "value": value,
                "regular": regular,
                "between": between_second_moment(values, weights, labels),
            }
        )
    regular_rows = [row for row in table if row["regular"]]
    singular_rows = [row for row in table if not row["regular"]]
    best = max(row["value"] for row in regular_rows)
    optima = [row for row in regular_rows if row["value"] == best]
    escapes = []
    for row in optima:
        labels = tuple(row["labels"])
        for move_row, source, destination in admissible_moves(labels):
            moved = list(labels)
            moved[move_row] = destination
            information = binned_information(scores, weights, moved)
            value, regular = profiled_value(information)
            escapes.append(
                {
                    "from_labels": list(labels),
                    "move": [move_row, source, destination],
                    "to_labels": list(_canonical(moved)),
                    "destination_regular": regular,
                    "destination_value": value,
                    "pseudo_inverse_gain": value - best,
                }
            )
    improving = [row for row in escapes if row["pseudo_inverse_gain"] > 0]
    upper, _ = best_three_group_between(values, weights)
    return {
        "scores": scores,
        "construction": {"x": list(WITNESS_X), "z": list(WITNESS_Z)},
        "weights": weights,
        "weighted_score_mean": [
            sum((w * row[column] for w, row in zip(weights, scores, strict=True)), F(0))
            for column in range(2)
        ],
        "rows_on_support": all(
            abs(x) <= 1 and abs(z) <= 1 for x, z in zip(WITNESS_X, WITNESS_Z, strict=True)
        ),
        "distinct_score_rows": len(set(scores)) == 4,
        "partitions": table,
        "scalar_upper": upper,
        "global_regular_value": best,
        "global_regular_optima": [row["labels"] for row in optima],
        "singular_labelings": [row["labels"] for row in singular_rows],
        "singular_pseudo_inverse_values": [row["value"] for row in singular_rows],
        "singular_beats_regular": any(row["value"] > best for row in singular_rows),
        "escape_moves": escapes,
        "improving_pseudo_inverse_moves": improving,
        "every_regular_optimum_has_improving_singular_move": all(
            any(
                row["pseudo_inverse_gain"] > 0 and not row["destination_regular"]
                for row in escapes
                if row["from_labels"] == optimum["labels"]
            )
            for optimum in optima
        ),
        "improving_regular_moves": [
            row for row in escapes if row["pseudo_inverse_gain"] > 0 and row["destination_regular"]
        ],
    }


def singular_minimality_search(
    x_grid: Sequence[Fraction] | None = None,
    z_grid: Sequence[Fraction] | None = None,
) -> dict[str, object]:
    """Enumerate four-row tables on the law's support hunting the same escape.

    Also records that three rows cannot host the phenomenon: at ``K=3`` a
    three-row table has three singleton cells and no nonempty-preserving
    relocation exists at all.
    """
    x_grid = x_grid or (F(-1), F(-1, 2), F(0), F(1, 2), F(1))
    z_grid = z_grid or (F(-1), F(-3, 4), F(-1, 2), F(0), F(1, 4), F(1, 2), F(3, 4), F(1))
    rows = [(x, z) for x in x_grid for z in z_grid]
    weights = [F(1, 4)] * 4
    combos = 0
    with_singular = 0
    witnesses = 0
    centered_witnesses = 0
    for choice in combinations(range(len(rows)), 4):
        combos += 1
        xs = [rows[index][0] for index in choice]
        zs = [rows[index][1] for index in choice]
        scores = law_scores(xs, zs)
        if len(set(scores)) != 4:
            continue
        best = None
        optima: list[tuple[int, ...]] = []
        singulars: list[Fraction] = []
        for labels in canonical_partitions(4):
            information = binned_information(scores, weights, labels)
            value, regular = profiled_value(information)
            if regular:
                if best is None or value > best:
                    best, optima = value, [labels]
                elif value == best:
                    optima.append(labels)
            else:
                singulars.append(value)
        if not singulars:
            continue
        with_singular += 1
        if best is None or max(singulars) <= best:
            continue
        escaped = True
        for optimum in optima:
            found = False
            for move_row, _source, destination in admissible_moves(optimum):
                moved = list(optimum)
                moved[move_row] = destination
                value, regular = profiled_value(binned_information(scores, weights, moved))
                if not regular and value > best:
                    found = True
                    break
            escaped = escaped and found
        if escaped:
            witnesses += 1
            mean = [
                sum((w * row[column] for w, row in zip(weights, scores, strict=True)), F(0))
                for column in range(2)
            ]
            if mean == [F(0), F(0)]:
                centered_witnesses += 1
    three_row = list(canonical_partitions(3))
    return {
        "x_grid": [str(value) for value in x_grid],
        "z_grid": [str(value) for value in z_grid],
        "candidate_rows": len(rows),
        "four_row_tables_enumerated": combos,
        "tables_with_a_singular_labeling": with_singular,
        "tables_where_every_regular_optimum_escapes": witnesses,
        "exactly_centered_witnesses": centered_witnesses,
        "three_row_canonical_partitions": len(three_row),
        "three_row_admissible_moves": sum(1 for _ in admissible_moves(three_row[0])),
        "support_minimality": "K=3 needs N>=4 for any nonempty-preserving relocation",
    }


def probability_zero_argument() -> dict[str, object]:
    """Record the exact reason the boundary is null under the continuous law."""
    return {
        "statement": (
            "At d_lambda = 1 the binned nuisance block sum_b W_b mu_lambda_b^2 vanishes "
            "iff every cell lambda-sum vanishes, which forces the total sample "
            "lambda-sum sum_i S_lambda_i to vanish.  Under the named law S_lambda has "
            "an absolutely continuous distribution, so P(sum_i S_lambda_i = 0) = 0 for "
            "every N, and a countable union over N stays null."
        ),
        "consequence": (
            "Almost surely every labeling with three nonempty cells is regular, so the "
            "regularity restriction in DS18.2 is a.s. vacuous and the ordinary "
            "one-point comparison domain contains no singular destination."
        ),
        "boundary": (
            "The statement is false for atomic emulations and hand-built tables: see "
            "the support-minimal witness in this artifact."
        ),
    }


# --------------------------------------------------------------------------- #
# subcommand: search
# --------------------------------------------------------------------------- #
def run_search(max_size: int = 10) -> dict[str, object]:
    """Run the exhaustive exact falsification sweep over the declared classes."""
    families: list[tuple[str, list[tuple[Fraction, Fraction]], list[Fraction]]] = []
    for size in range(3, max_size + 1):
        scores, weights = midpoint_sample(size)
        families.append((f"midpoint_n{size}", scores, weights))
    for size in (6, 8, 10):
        scores, weights = product_sample(size)
        families.append((f"product_n{size}", scores, weights))
    for size in range(4, max_size + 1):
        for rep in range(3):
            scores, weights = lcg_sample(size, rep)
            families.append((f"lcg_n{size}_rep{rep}", scores, weights))
    families.extend(adversarial_cases())

    reports = []
    totals = {
        "tables": 0,
        "canonical_partitions": 0,
        "regular_partitions": 0,
        "singular_partitions": 0,
        "sandwich_violations": 0,
        "variational_violations": 0,
        "contiguity_disagreements": 0,
        "singular_beats_regular": 0,
    }
    for name, scores, weights in families:
        report = scan_partitions(scores, weights, check_contiguity=len(scores) <= 8)
        report["name"] = name
        reports.append(report)
        totals["tables"] += 1
        totals["canonical_partitions"] += int(report["canonical_partitions"])
        totals["regular_partitions"] += int(report["regular_partitions"])
        totals["singular_partitions"] += int(report["singular_partitions"])
        totals["sandwich_violations"] += int(report["sandwich_violations"])
        totals["variational_violations"] += int(report["variational_violations"])
        if report.get("contiguity_agrees") is False:
            totals["contiguity_disagreements"] += 1
        if report["singular_beats_regular"]:
            totals["singular_beats_regular"] += 1
    return {"totals": totals, "tables": reports}


# --------------------------------------------------------------------------- #
# subcommand: transfer
# --------------------------------------------------------------------------- #
def exhaustive_transfer(size: int, rep: int) -> dict[str, object]:
    """Return the exact global optimum of one sample and its distance to ``q*``."""
    scores = sample_law(size, SEED_BASE + 1000 * size + rep)
    weights = [F(1, size)] * size
    values = [psi for psi, _ in scores]
    reference = population_labels(scores)
    upper, _ = best_three_group_between(values, weights)
    reference_value, reference_regular = profiled_value(
        binned_information(scores, weights, reference)
    )
    best_value = None
    best_labels: tuple[int, ...] = ()
    count = 0
    singular = 0
    for labels in canonical_partitions(size):
        count += 1
        information = binned_information(scores, weights, labels)
        value, regular = profiled_value(information)
        if not regular:
            singular += 1
            continue
        if best_value is None or value > best_value:
            best_value, best_labels = value, labels
    gain, _, moves = best_exchange_gain(scores, weights, best_labels)
    disagreement = min(
        sum(
            1
            for left, right in zip(best_labels, [mapping[label] for label in reference], strict=True)
            if left != right
        )
        for mapping in _permutations_of_three()
    )
    optimum_information = binned_information(scores, weights, best_labels)
    return {
        "size": size,
        "rep": rep,
        "seed": SEED_BASE + 1000 * size + rep,
        "canonical_partitions": count,
        "singular_partitions": singular,
        "population_cut_value": reference_value,
        "population_cut_regular": reference_regular,
        "global_value": best_value,
        "global_labels": list(best_labels),
        "global_information": optimum_information,
        "global_is_exchange_stable": gain <= 0,
        "global_best_move_gain": gain,
        "global_admissible_moves": moves,
        "scalar_upper": upper,
        "delta_certificate": upper - reference_value,
        "label_disagreements_with_population_rule": disagreement,
        "disagreement_fraction": F(disagreement, size),
    }


def _permutations_of_three() -> list[dict[int, int]]:
    return [
        dict(zip(range(N_BINS), order, strict=True))
        for order in (
            (0, 1, 2),
            (0, 2, 1),
            (1, 0, 2),
            (1, 2, 0),
            (2, 0, 1),
            (2, 1, 0),
        )
    ]


def squeeze_certificate(size: int, rep: int) -> dict[str, object]:
    """Return the exact finite-``N`` squeeze certificate for one sample.

    Every exact global regular optimum ``z`` of this sample satisfies, without
    any enumeration:

    * ``btw(z) >= v_hat_3 - Delta``,
    * the excess of ``z`` over its own codebook's nearest-point rule is
      ``<= Delta``,
    * ``z``'s own codebook is ``Delta``-optimal for the empirical scalar
      three-level problem,

    with ``Delta = v_hat_3 - Phi_hat(z*)`` and ``z*`` the fixed population-cut
    labeling.  ``Delta -> 0`` is exactly the DS18.2 squeeze.
    """
    scores = sample_law(size, SEED_BASE + 1000 * size + rep)
    weights = [F(1, size)] * size
    reference = population_labels(scores)
    counts = [reference.count(index) for index in range(N_BINS)]
    if min(counts) == 0:
        raise ValueError("degenerate reference labeling")
    information = binned_information(scores, weights, reference)
    value, regular = profiled_value(information)
    between = between_second_moment([psi for psi, _ in scores], weights, reference)
    units = sorted(int(psi * GRID) for psi, _ in scores)
    upper, cuts = best_three_group_equal_weight(units)
    second_moment = sum((F(1, size) * psi * psi for psi, _ in scores), F(0))
    slope = information[0][1] / information[1][1] if information[1][1] != 0 else F(0)
    projected = []
    masses, m_psi, m_lam = cell_moments(scores, weights, reference)
    for mass, first, second in zip(masses, m_psi, m_lam, strict=True):
        projected.append(first / mass - slope * second / mass)
    separation = min(
        abs(projected[first] - projected[second])
        for first, second in combinations(range(N_BINS), 2)
    )
    delta = upper - value
    return {
        "size": size,
        "rep": rep,
        "seed": SEED_BASE + 1000 * size + rep,
        "reference_masses": [F(count, size) for count in counts],
        "reference_information": information,
        "reference_regular": regular,
        "reference_profiled_value": value,
        "reference_between": between,
        "reference_tax": between - value,
        "empirical_second_moment": second_moment,
        "scalar_upper": upper,
        "scalar_upper_cuts": list(cuts),
        "scalar_suboptimality_of_fixed_cuts": upper - between,
        "delta": delta,
        "delta_float": float(delta),
        "margins": {
            "min_mass": min(F(count, size) for count in counts),
            "mass_at_least_c0": min(counts) * 4 >= size,
            "lambda_min_at_least_kappa": lambda_min_at_least(information, F(1, 4)),
            "projected_separation": separation,
            "separation_at_least_gamma": separation >= F(1, 2),
            "companion_slope": slope,
        },
    }


def run_transfer(
    exhaustive_sizes: Sequence[int] = (4, 5, 6, 7, 8, 9, 10, 11),
    certificate_sizes: Sequence[int] = (64, 256, 1024, 4096),
    reps: int = 3,
) -> dict[str, object]:
    """Run both halves of the empirical-transfer probe."""
    exhaustive = [
        exhaustive_transfer(size, rep) for size in exhaustive_sizes for rep in range(reps)
    ]
    certificates = [
        squeeze_certificate(size, rep) for size in certificate_sizes for rep in range(reps)
    ]
    return {
        "exhaustive": exhaustive,
        "exhaustive_all_stable": all(row["global_is_exchange_stable"] for row in exhaustive),
        "exhaustive_delta_nonnegative": all(row["delta_certificate"] >= 0 for row in exhaustive),
        "certificates": certificates,
        "certificate_delta_by_size": {
            str(size): [
                float(row["delta"]) for row in certificates if row["size"] == size
            ]
            for size in certificate_sizes
        },
        "certificate_margins_by_size": {
            str(size): {
                "mass_at_least_c0": sum(
                    1 for row in certificates
                    if row["size"] == size and row["margins"]["mass_at_least_c0"]
                ),
                "lambda_min_at_least_kappa": sum(
                    1 for row in certificates
                    if row["size"] == size and row["margins"]["lambda_min_at_least_kappa"]
                ),
                "separation_at_least_gamma": sum(
                    1 for row in certificates
                    if row["size"] == size and row["margins"]["separation_at_least_gamma"]
                ),
                "reps": sum(1 for row in certificates if row["size"] == size),
                "max_abs_companion_slope": float(
                    max(
                        abs(row["margins"]["companion_slope"])
                        for row in certificates
                        if row["size"] == size
                    )
                ),
            }
            for size in certificate_sizes
        },
        "certificate_margins_hold_at_largest_size": all(
            row["margins"]["mass_at_least_c0"]
            and row["margins"]["lambda_min_at_least_kappa"]
            and row["margins"]["separation_at_least_gamma"]
            for row in certificates
            if row["size"] == max(certificate_sizes)
        ),
    }


# --------------------------------------------------------------------------- #
# command line
# --------------------------------------------------------------------------- #
def cmd_population(args: argparse.Namespace) -> dict[str, object]:
    """Recompute the population theorem by both routes."""
    started = time.time()
    route_a = population_route_a()
    route_b_json, route_b = population_route_b()
    checks = {
        "full_psi_psi": route_a["full_information"][0][0],
        "full_psi_lambda": route_a["full_information"][0][1],
        "full_lambda_lambda": route_a["full_information"][1][1],
    }
    for index in range(N_BINS):
        checks[f"mass_{index}"] = route_a["cell_masses"][index]
        checks[f"m_psi_{index}"] = (
            route_a["cell_means_psi"][index] * route_a["cell_masses"][index]
        )
        checks[f"m_lambda_{index}"] = (
            route_a["cell_means_lambda"][index] * route_a["cell_masses"][index]
        )
    agreement = {
        name: route_b[name].contains(value) for name, value in checks.items()
    }
    return {
        "route_a_exact": route_a,
        "route_b_interval": route_b_json,
        "route_b_contains_route_a": agreement,
        "route_b_all_agree": all(agreement.values()),
        "route_c_monte_carlo": [
            population_monte_carlo(size, SEED_BASE + size)
            for size in (10_000, 200_000)
        ],
        "scalar_codebook_scan": scalar_codebook_grid_scan(F(1, args.codebook_steps)),
        "m4_sweep": m4_sweep(nx=args.slab_subdivisions),
        "seconds": round(time.time() - started, 2),
    }


def cmd_exact(_args: argparse.Namespace) -> dict[str, object]:
    """Rebuild the exact identities and the serialized boundary fixture."""
    started = time.time()
    payload = exact_battery()
    payload["seconds"] = round(time.time() - started, 2)
    return payload


def cmd_search(args: argparse.Namespace) -> dict[str, object]:
    """Run the exhaustive exact falsification sweep."""
    started = time.time()
    payload = run_search(max_size=args.max_size)
    payload["seconds"] = round(time.time() - started, 2)
    return payload


def cmd_boundary(args: argparse.Namespace) -> dict[str, object]:
    """Rebuild the singular-destination boundary witness and its minimality search."""
    started = time.time()
    payload: dict[str, object] = {
        "witness": singular_destination_witness(),
        "probability_zero_argument": probability_zero_argument(),
    }
    if args.minimality_search:
        payload["minimality_search"] = singular_minimality_search()
    payload["seconds"] = round(time.time() - started, 2)
    return payload


def cmd_transfer(args: argparse.Namespace) -> dict[str, object]:
    """Run the empirical-transfer probe."""
    started = time.time()
    payload = run_transfer(
        exhaustive_sizes=tuple(range(4, args.max_exhaustive + 1)),
        certificate_sizes=tuple(args.certificate_sizes),
        reps=args.reps,
    )
    payload["seconds"] = round(time.time() - started, 2)
    return payload


COMMANDS = {
    "population": (cmd_population, "population.json"),
    "exact": (cmd_exact, "exact.json"),
    "search": (cmd_search, "search.json"),
    "boundary": (cmd_boundary, "boundary.json"),
    "transfer": (cmd_transfer, "transfer.json"),
}


def main(argv: Sequence[str] | None = None) -> int:
    """Run one audit subcommand and write its provenance-stamped artifact."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "command", choices=[*COMMANDS, "all"], help="which audit stage to run"
    )
    parser.add_argument("--max-size", type=int, default=10, help="exhaustive search bound")
    parser.add_argument(
        "--max-exhaustive", type=int, default=11, help="largest exhaustively optimised sample"
    )
    parser.add_argument(
        "--certificate-sizes",
        type=int,
        nargs="+",
        default=[64, 256, 1024, 4096],
        help="sample sizes for the squeeze certificate",
    )
    parser.add_argument("--reps", type=int, default=3, help="repetitions per sample size")
    parser.add_argument(
        "--codebook-steps", type=int, default=30, help="1/spacing of the codebook lattice"
    )
    parser.add_argument(
        "--slab-subdivisions", type=int, default=2000, help="(M4) sweep mesh in x"
    )
    parser.add_argument(
        "--no-minimality-search",
        dest="minimality_search",
        action="store_false",
        help="skip the four-row boundary minimality enumeration",
    )
    args = parser.parse_args(argv)

    names = list(COMMANDS) if args.command == "all" else [args.command]
    written = []
    for name in names:
        function, filename = COMMANDS[name]
        payload = {"provenance": provenance(), "stage": name, **function(args)}
        path = write_artifact(filename, payload)
        written.append(str(path.relative_to(WORKSPACE)))
        print(f"{name}: wrote {path.relative_to(WORKSPACE)}")
    print("artifacts: " + ", ".join(written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
