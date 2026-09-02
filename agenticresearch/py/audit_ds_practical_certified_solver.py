"""Independent adversarial audit instrument for DS19.

Audit target
------------
``OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`` and its DS19 components
(``DS-TILT-DUAL-CERTIFICATE``, ``DS-TILT-DUAL-STRONG-DUALITY-FAILS``,
``DS-STRIP-DP-DELTA-CONSISTENCY``, ``DS-MATRIX-TILT-NONQUASICONVEX`` and the
DS19 clauses of ``DS-PROFILED-COMPILE-CERTIFICATE``), frozen at commit
``2c9cb77`` of ``research-ds-practical-certified-solver``.

Independence contract
---------------------
Written from the registered statements alone.  This module does **not**
import, extend, translate or reuse ``py/ds_practical_certified_solver.py`` (the
researcher's harness) and does not import the ``scorequant`` library.  It is
pure standard library so that a bookkeeping session can rerun it.

Every claim-relevant quantity is computed in ``fractions.Fraction``.  Where an
exact minimizer of the tilt dual is a quadratic irrational, it is represented
exactly in the field ``Q(sqrt(D))`` by :class:`QSqrt`; sign tests in that
field are exact.  Floating point appears only in human-readable summaries.

Notation (all second moments are about the score-space origin; nothing is
sample-centered)::

    T_beta,i = s_psi,i - beta . s_lambda,i
    V_z(beta) = sum_b (sum_{i in b} w_i T_beta,i)^2 / W_b        (btw of T_beta)
    v_K(beta) = max_z V_z(beta)                                   (tilt dual map)
    Phi^+(z)  = I_psipsi - I_psilam I_lamlam^+ I_lampsi = min_beta V_z(beta)

Stages (``python audit_ds_practical_certified_solver.py <stage>|all``):

``witness``     rebuild CE-DS-TILT-DUAL-GAP-001 from raw rows, compute the
                exact algebraic dual minimum, decide support minimality and
                search N=3,K=2 for the overall-minimal witness (fixture 002).
``ceiling``     exhaustive weak-duality / DS11 / domain-split sweep, N<=10.
``saddle``      exact d at d_lambda=1, closure iff saddle, tie-masked closures.
``ties``        tie-order independence of the interval DP and derivative rules.
``compute``     coercivity radius, root-separation bit model, cutting-plane
                certified bracket at d_lambda=2, arrangement-cell counts.
``family``      the positive-weight order-one augmentation family, r=2..6.
``ds18``        beta-zero interval DP on exact DS18-law samples: Delta_N chain.
``tierb``       matrix-tilt non-quasiconvexity rebuilt from raw rows.
``invariances`` protocol-G invariance battery.

Randomness comes from an explicit 64-bit LCG with the deterministic seed
formula ``seed(n, rep) = SEED_BASE + 1000 * n + rep`` and
``SEED_BASE = 20260902``.

Nothing here is theorem authority; the report
``AUDITS/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001.md`` carries the mathematics.
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
from collections.abc import Callable, Iterator, Sequence
from functools import cmp_to_key
from datetime import UTC, datetime
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[1]
WORKSPACE = RESEARCH.parent
AUDIT_ID = "AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001"
ARTIFACTS = RESEARCH / "AUDITS" / "artifacts" / AUDIT_ID
FIXTURES = RESEARCH / "COUNTEREXAMPLES"
SEED_BASE = 20260902

F = Fraction
ZERO = F(0)
ONE = F(1)

Row = tuple[Fraction, ...]
Table = tuple[list[Row], list[Fraction]]


# --------------------------------------------------------------------------- #
# Exact quadratic-field arithmetic: a + b*sqrt(D), D a positive non-square int
# --------------------------------------------------------------------------- #
def _is_square(value: int) -> bool:
    root = math.isqrt(value)
    return root * root == value


class QSqrt:
    """Exact element ``a + b*sqrt(D)`` of a real quadratic field.

    ``D`` is a positive integer; when ``D`` is a perfect square the element is
    normalised to a rational (``b = 0``).  All comparisons are exact.
    """

    __slots__ = ("a", "b", "d")

    def __init__(self, a: Fraction | int, b: Fraction | int = 0, d: int = 1) -> None:
        a = F(a)
        b = F(b)
        if d <= 0:
            raise ValueError("D must be positive")
        if b != 0 and _is_square(d):
            a += b * math.isqrt(d)
            b = ZERO
            d = 1
        if b == 0:
            d = 1
        self.a, self.b, self.d = a, b, d

    # -- helpers -------------------------------------------------------------
    def _coerce(self, other: object) -> QSqrt:
        if isinstance(other, QSqrt):
            return other
        if isinstance(other, (int, Fraction)):
            return QSqrt(other)
        return NotImplemented  # type: ignore[return-value]

    def _same_field(self, other: QSqrt) -> tuple[QSqrt, QSqrt, int]:
        """Bring two elements into one field, or raise if they are incommensurable."""
        if self.b == 0 or other.b == 0 or self.d == other.d:
            return self, other, (self.d if self.b != 0 else other.d)
        # D and E share a field iff D*E is a perfect square: sqrt(E) = sqrt(D*E)/D... use
        # sqrt(E) = (sqrt(D E)/D) * sqrt(D) with sqrt(DE) integer
        prod = self.d * other.d
        if _is_square(prod):
            factor = F(math.isqrt(prod), self.d)  # sqrt(E) = factor * sqrt(D)
            return self, QSqrt(other.a, other.b * factor, self.d), self.d
        raise ValueError("mixed quadratic fields")

    def _field(self, other: QSqrt) -> int:
        return self.d if self.b != 0 else other.d

    def is_rational(self) -> bool:
        return self.b == 0

    def sign(self) -> int:
        """Exact sign of ``a + b*sqrt(D)``."""
        a, b, d = self.a, self.b, self.d
        if b == 0:
            return (a > 0) - (a < 0)
        if a == 0:
            return (b > 0) - (b < 0)
        # sign(a + b sqrt D): compare a^2 with b^2 D when signs differ
        if a > 0 and b > 0:
            return 1
        if a < 0 and b < 0:
            return -1
        lhs, rhs = a * a, b * b * d
        if a > 0:  # b < 0
            return 1 if lhs > rhs else (-1 if lhs < rhs else 0)
        # a < 0, b > 0
        return -1 if lhs > rhs else (1 if lhs < rhs else 0)

    def __float__(self) -> float:
        return float(self.a) + float(self.b) * math.sqrt(self.d)

    def __repr__(self) -> str:
        if self.b == 0:
            return str(self.a)
        return f"{self.a} + ({self.b})*sqrt({self.d})"

    # -- arithmetic ----------------------------------------------------------
    def __add__(self, other: object) -> QSqrt:
        left, right, d = self._same_field(self._coerce(other))
        return QSqrt(left.a + right.a, left.b + right.b, d)

    __radd__ = __add__

    def __neg__(self) -> QSqrt:
        return QSqrt(-self.a, -self.b, self.d)

    def __sub__(self, other: object) -> QSqrt:
        left, right, d = self._same_field(self._coerce(other))
        return QSqrt(left.a - right.a, left.b - right.b, d)

    def __rsub__(self, other: object) -> QSqrt:
        return QSqrt(other) - self

    def __mul__(self, other: object) -> QSqrt:
        left, right, d = self._same_field(self._coerce(other))
        return QSqrt(
            left.a * right.a + left.b * right.b * d,
            left.a * right.b + left.b * right.a,
            d,
        )

    __rmul__ = __mul__

    def __truediv__(self, other: object) -> QSqrt:
        left, right, d = self._same_field(self._coerce(other))
        norm = right.a * right.a - right.b * right.b * d
        if norm == 0:
            raise ZeroDivisionError("division by zero in Q(sqrt D)")
        conj = QSqrt(right.a, -right.b, d)
        numerator = left * conj
        return QSqrt(numerator.a / norm, numerator.b / norm, d)

    def __rtruediv__(self, other: object) -> QSqrt:
        return QSqrt(other) / self

    # -- comparisons ---------------------------------------------------------
    def enclosure(self, digits: int = 30) -> tuple[Fraction, Fraction]:
        """Rigorous rational enclosure ``[lo, hi]`` of the element."""
        if self.b == 0:
            return self.a, self.a
        scale = 10**digits
        root_lo = F(math.isqrt(self.d * scale * scale), scale)
        root_hi = root_lo + F(1, scale)
        if self.b > 0:
            return self.a + self.b * root_lo, self.a + self.b * root_hi
        return self.a + self.b * root_hi, self.a + self.b * root_lo

    def compare(self, other: object) -> int:
        """Exact three-way comparison, valid across incommensurable fields."""
        other = self._coerce(other)
        try:
            return (self - other).sign()
        except ValueError:
            pass
        # a + b sqrt(D) = c + e sqrt(E) with b, e != 0 and D E not a square is
        # impossible (sqrt(D), sqrt(E) are Q-linearly independent), so a strict
        # sign exists and rational enclosures separate after finitely many digits.
        digits = 30
        while True:
            lo1, hi1 = self.enclosure(digits)
            lo2, hi2 = other.enclosure(digits)
            if hi1 < lo2:
                return -1
            if hi2 < lo1:
                return 1
            digits *= 2
            if digits > 4000:
                raise RuntimeError("enclosures failed to separate")

    def __eq__(self, other: object) -> bool:
        return self.compare(other) == 0

    def __lt__(self, other: object) -> bool:
        return self.compare(other) < 0

    def __le__(self, other: object) -> bool:
        return self.compare(other) <= 0

    def __gt__(self, other: object) -> bool:
        return self.compare(other) > 0

    def __ge__(self, other: object) -> bool:
        return self.compare(other) >= 0

    def __hash__(self) -> int:
        return hash((self.a, self.b, self.d))

    def __abs__(self) -> QSqrt:
        return self if self.sign() >= 0 else -self

    def to_json(self) -> dict[str, str | int]:
        return {"a": str(self.a), "b": str(self.b), "D": self.d, "float": repr(float(self))}


def sorted_distinct(points: Sequence[QSqrt]) -> list[QSqrt]:
    """Sort exact values and drop exact duplicates (hash-insensitive, field-insensitive)."""
    ordered = sorted(points)
    out: list[QSqrt] = []
    for x in ordered:
        if not out or x != out[-1]:
            out.append(x)
    return out


def rational_between(left: QSqrt, right: QSqrt) -> Fraction:
    """A rational strictly between two distinct exact values (any fields)."""
    digits = 12
    while True:
        _, hi_l = left.enclosure(digits)
        lo_r, _ = right.enclosure(digits)
        if hi_l < lo_r:
            return (hi_l + lo_r) / 2
        digits *= 2
        if digits > 4000:
            raise RuntimeError("could not separate values")


def quadratic_roots(a: Fraction, b: Fraction, c: Fraction) -> list[QSqrt]:
    """Exact real roots of ``a x^2 + b x + c`` (a, b, c rational)."""
    if a == 0:
        if b == 0:
            return []
        return [QSqrt(-c / b)]
    disc = b * b - 4 * a * c
    if disc < 0:
        return []
    if disc == 0:
        return [QSqrt(-b / (2 * a))]
    # sqrt(disc) = sqrt(p/q) = sqrt(p q)/q
    p, q = disc.numerator, disc.denominator
    square_free = p * q
    root = QSqrt(0, F(1, q), square_free)  # sqrt(disc)
    left = (QSqrt(-b) - root) / (2 * a)
    right = (QSqrt(-b) + root) / (2 * a)
    return sorted([left, right])


# --------------------------------------------------------------------------- #
# Partitions, moments, information, DS11 algebra
# --------------------------------------------------------------------------- #
def canonical_partitions(size: int, bins: int) -> Iterator[tuple[int, ...]]:
    """Restricted-growth labelings with exactly ``bins`` nonempty cells."""
    if size < bins or bins < 1:
        return

    labels = [0] * size

    def rec(position: int, used: int) -> Iterator[tuple[int, ...]]:
        if position == size:
            if used == bins:
                yield tuple(labels)
            return
        remaining = size - position
        for label in range(min(used + 1, bins)):
            if label == used and used + 1 > bins:
                continue
            new_used = used + (1 if label == used else 0)
            if bins - new_used > remaining - 1:
                continue
            labels[position] = label
            yield from rec(position + 1, new_used)

    yield from rec(0, 0)


def canonicalize(labels: Sequence[int]) -> tuple[int, ...]:
    mapping: dict[int, int] = {}
    out = []
    for label in labels:
        if label not in mapping:
            mapping[label] = len(mapping)
        out.append(mapping[label])
    return tuple(out)


def cell_sums(
    scores: Sequence[Row], weights: Sequence[Fraction], labels: Sequence[int], bins: int
) -> tuple[list[Fraction], list[list[Fraction]]]:
    """Return cell masses and weighted coordinate sums ``sum_i w_i s_i``."""
    dim = len(scores[0])
    masses = [ZERO] * bins
    sums = [[ZERO] * dim for _ in range(bins)]
    for row, weight, label in zip(scores, weights, labels, strict=True):
        masses[label] += weight
        for k in range(dim):
            sums[label][k] += weight * row[k]
    return masses, sums


def binned_information(
    scores: Sequence[Row], weights: Sequence[Fraction], labels: Sequence[int], bins: int
) -> list[list[Fraction]]:
    """``I_z = sum_b m_b m_b^T / W_b`` exactly; raises on an empty cell."""
    masses, sums = cell_sums(scores, weights, labels, bins)
    dim = len(scores[0])
    if any(mass == 0 for mass in masses):
        raise ValueError("every cell must carry positive mass")
    info = [[ZERO] * dim for _ in range(dim)]
    for mass, vector in zip(masses, sums, strict=True):
        for r in range(dim):
            for c in range(dim):
                info[r][c] += vector[r] * vector[c] / mass
    return info


def solve_normal_equation(
    lam: Sequence[Sequence[Fraction]], rhs: Sequence[Fraction]
) -> tuple[list[Fraction], list[list[Fraction]], int] | None:
    """Solve ``beta I_lamlam = I_psilam`` (row-vector form, symmetric block).

    Returns ``(particular, null_basis, rank)`` or ``None`` if inconsistent.
    """
    n = len(rhs)
    # augmented system A x = rhs with A = lam (symmetric)
    rows = [[F(v) for v in lam[r]] + [F(rhs[r])] for r in range(n)]
    pivots: list[int] = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, n) if rows[i][c] != 0), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        scale = rows[r][c]
        rows[r] = [v / scale for v in rows[r]]
        for i in range(n):
            if i != r and rows[i][c] != 0:
                factor = rows[i][c]
                rows[i] = [vi - factor * vr for vi, vr in zip(rows[i], rows[r], strict=True)]
        pivots.append(c)
        r += 1
        if r == n:
            break
    for i in range(r, n):
        if rows[i][n] != 0:
            return None
    particular = [ZERO] * n
    for i, c in enumerate(pivots):
        particular[c] = rows[i][n]
    free = [c for c in range(n) if c not in pivots]
    null_basis = []
    for f in free:
        vec = [ZERO] * n
        vec[f] = ONE
        for i, c in enumerate(pivots):
            vec[c] = -rows[i][f]
        null_basis.append(vec)
    return particular, null_basis, len(pivots)


def profiled_value(info: Sequence[Sequence[Fraction]]) -> tuple[Fraction, bool, list[Fraction]]:
    """Return ``(Phi^+(z), regular, beta_z)`` from the DS11 normal equation.

    ``Phi^+`` is the Moore-Penrose value ``I_pp - I_pl I_ll^+ I_lp``; any
    solution of the normal equation gives it (completion of squares), so the
    particular solution suffices.  ``regular`` is ``I_ll`` nonsingular.
    """
    dl = len(info) - 1
    lam = [[info[1 + r][1 + c] for c in range(dl)] for r in range(dl)]
    rhs = [info[0][1 + c] for c in range(dl)]
    solved = solve_normal_equation(lam, rhs)
    if solved is None:
        raise AssertionError("PSD block matrix must satisfy the range condition")
    beta, _, rank = solved
    value = info[0][0] - sum(b * r for b, r in zip(beta, rhs, strict=True))
    return value, rank == dl, beta


def tilted_form(
    info: Sequence[Sequence[Fraction]], beta: Sequence[Fraction | QSqrt]
) -> Fraction | QSqrt:
    """``V_z(beta) = [1, -beta] I_z [1, -beta]^T`` exactly."""
    dl = len(info) - 1
    value: Fraction | QSqrt = info[0][0]
    for r in range(dl):
        value = value - 2 * beta[r] * info[0][1 + r]
        for c in range(dl):
            value = value + beta[r] * beta[c] * info[1 + r][1 + c]
    return value


def tilt_quadratic_1d(info: Sequence[Sequence[Fraction]]) -> tuple[Fraction, Fraction, Fraction]:
    """Coefficients ``(A, B, C)`` of ``V_z(beta) = A beta^2 + B beta + C`` at d_lambda=1."""
    return info[1][1], -2 * info[0][1], info[0][0]


def tilted_values(scores: Sequence[Row], beta: Sequence[Fraction | QSqrt]) -> list[Fraction | QSqrt]:
    out: list[Fraction | QSqrt] = []
    for row in scores:
        value: Fraction | QSqrt = row[0]
        for k, b in enumerate(beta):
            value = value - b * row[1 + k]
        out.append(value)
    return out


def between_value(
    values: Sequence[Fraction | QSqrt],
    weights: Sequence[Fraction],
    labels: Sequence[int],
    bins: int,
) -> Fraction | QSqrt:
    """Uncentered scalar between second moment ``sum_b (sum w t)^2 / W_b``."""
    masses = [ZERO] * bins
    moments: list[Fraction | QSqrt] = [ZERO] * bins
    for value, weight, label in zip(values, weights, labels, strict=True):
        masses[label] += weight
        moments[label] = moments[label] + weight * value
    if any(mass == 0 for mass in masses):
        raise ValueError("every cell must carry positive mass")
    total: Fraction | QSqrt = ZERO
    for moment, mass in zip(moments, masses, strict=True):
        total = total + moment * moment / mass
    return total


# --------------------------------------------------------------------------- #
# Exact interval DP (Fisher contiguity) over any exact ordered numeric type
# --------------------------------------------------------------------------- #
def interval_dp(
    values: Sequence[Fraction | QSqrt],
    weights: Sequence[Fraction],
    bins: int,
    order: Sequence[int],
    slopes: Sequence[Fraction] | None = None,
    prefer_max_slope: bool = True,
) -> tuple[Fraction | QSqrt, tuple[int, ...], Fraction | None]:
    """Exact O(K N^2) interval DP in the supplied total order.

    Maximises ``sum_b M_b^2 / W_b`` over contiguous K-cell partitions of
    ``order``.  When ``slopes`` (``-2 * s_lambda`` per row) is given, exact
    value ties are broken lexicographically by the derivative
    ``sum_b M_b * (sum_b w*slope) / W_b`` (max or min, giving the one-sided
    derivative of ``v_K``) and then by the curvature ``sum_b (sum_b w*slope)^2
    / (4 W_b)`` (max), which selects the labeling active on the open one-sided
    interval.  All three keys are additive over cells, so the lexicographic DP
    is exact.

    Returns ``(value, labels, derivative)``.
    """
    n = len(order)
    if n < bins:
        raise ValueError("fewer rows than cells")
    pw = [ZERO] * (n + 1)
    pm: list[Fraction | QSqrt] = [ZERO] * (n + 1)
    ps = [ZERO] * (n + 1)
    for pos, idx in enumerate(order):
        pw[pos + 1] = pw[pos] + weights[idx]
        pm[pos + 1] = pm[pos] + weights[idx] * values[idx]
        if slopes is not None:
            ps[pos + 1] = ps[pos] + weights[idx] * slopes[idx]
    sign = 1 if prefer_max_slope else -1

    def cost(i: int, j: int) -> tuple[Fraction | QSqrt, Fraction | QSqrt, Fraction]:
        mass = pw[j] - pw[i]
        moment = pm[j] - pm[i]
        value = moment * moment / mass
        if slopes is None:
            return value, ZERO, ZERO
        slope = ps[j] - ps[i]
        return value, moment * slope / mass * sign, slope * slope / (4 * mass)

    Entry = tuple[Fraction | QSqrt, Fraction | QSqrt, Fraction]
    dp: list[list[Entry | None]] = [[None] * (n + 1) for _ in range(bins + 1)]
    arg: list[list[int]] = [[-1] * (n + 1) for _ in range(bins + 1)]
    dp[0][0] = (ZERO, ZERO, ZERO)
    for c in range(1, bins + 1):
        for j in range(c, n + 1):
            best: Entry | None = None
            best_i = -1
            for i in range(c - 1, j):
                prev = dp[c - 1][i]
                if prev is None:
                    continue
                cv, cd, cc = cost(i, j)
                cand: Entry = (prev[0] + cv, prev[1] + cd, prev[2] + cc)
                if best is None or cand[0] > best[0]:
                    best, best_i = cand, i
                elif slopes is not None and cand[0] == best[0]:
                    if cand[1] > best[1] or (cand[1] == best[1] and cand[2] > best[2]):
                        best, best_i = cand, i
            dp[c][j] = best
            arg[c][j] = best_i
    final = dp[bins][n]
    assert final is not None
    labels = [0] * n
    j = n
    for c in range(bins, 0, -1):
        i = arg[c][j]
        for pos in range(i, j):
            labels[order[pos]] = c - 1
        j = i
    derivative = None if slopes is None else final[1] * sign
    return final[0], canonicalize(labels), derivative  # type: ignore[return-value]


def sorted_order(
    values: Sequence[Fraction | QSqrt], tie_key: Sequence[Fraction] | None = None
) -> list[int]:
    """Indices sorted by value; exact ties broken by ``tie_key`` then index."""
    idx = list(range(len(values)))

    def cmp(i: int, j: int) -> int:
        vi, vj = values[i], values[j]
        if vi < vj:
            return -1
        if vi > vj:
            return 1
        if tie_key is not None:
            if tie_key[i] < tie_key[j]:
                return -1
            if tie_key[i] > tie_key[j]:
                return 1
        return (i > j) - (i < j)

    return sorted(idx, key=cmp_to_key(cmp))


def dual_value_1d(
    scores: Sequence[Row], weights: Sequence[Fraction], bins: int, beta: Fraction | QSqrt
) -> tuple[Fraction | QSqrt, tuple[int, ...], Fraction | QSqrt, tuple[int, ...], Fraction | QSqrt]:
    """``v_K(beta)`` with exact one-sided derivatives at d_lambda=1.

    Returns ``(value, z_right, D+, z_left, D-)`` where ``z_right`` is active on
    ``(beta, beta+eps)`` and ``z_left`` on ``(beta-eps, beta)``.  The right
    perturbation orders exact ties by decreasing ``s_lambda`` (since
    ``T_{beta+eps} = T_beta - eps s_lambda``) and takes the maximal
    derivative; the left perturbation does the opposite.
    """
    values = tilted_values(scores, [beta])
    slopes = [-2 * row[1] for row in scores]
    lam = [row[1] for row in scores]
    order_right = sorted_order(values, [-x for x in lam])
    order_left = sorted_order(values, lam)
    v_r, z_r, d_r = interval_dp(values, weights, bins, order_right, slopes, True)
    v_l, z_l, d_l = interval_dp(values, weights, bins, order_left, slopes, False)
    assert v_r == v_l, "tie-order dependence of the interval-DP value"
    assert d_r is not None and d_l is not None
    return v_r, z_r, d_r, z_l, d_l


def brute_dual_value(
    scores: Sequence[Row], weights: Sequence[Fraction], bins: int, beta: Sequence[Fraction | QSqrt]
) -> tuple[Fraction | QSqrt, list[tuple[int, ...]]]:
    """``max_z V_z(beta)`` over every canonical labeling, with the active set."""
    values = tilted_values(scores, beta)
    best = None
    active: list[tuple[int, ...]] = []
    for labels in canonical_partitions(len(scores), bins):
        value = between_value(values, weights, labels, bins)
        if best is None or value > best:
            best, active = value, [labels]
        elif value == best:
            active.append(labels)
    assert best is not None
    return best, active


# --------------------------------------------------------------------------- #
# Exact minimisation of v_K at d_lambda = 1 (audit-supplied algorithm)
# --------------------------------------------------------------------------- #
def rational_sqrt_upper(value: Fraction) -> Fraction:
    """A rational upper bound on ``sqrt(value)`` for ``value >= 0``."""
    if value <= 0:
        return ZERO
    num, den = value.numerator, value.denominator
    # sqrt(num/den) = sqrt(num*den)/den <= (isqrt(num*den)+1)/den
    return F(math.isqrt(num * den) + 1, den)


def coercivity_radius(scores: Sequence[Row], weights: Sequence[Fraction], bins: int) -> Fraction:
    """Observable rational radius containing every dual minimizer (d_lambda=1).

    For every row i, the partition with i alone in a cell and the remaining
    rows filling K-1 nonempty cells exists whenever N-1 >= K-1, and gives
    ``v_K(beta) >= w_i (s_psi,i - beta s_lam,i)^2``.  Any minimizer satisfies
    ``v_K(beta*) <= v_K(0)``, hence lies in every slab
    ``|beta - s_psi,i/s_lam,i| <= sqrt(v_K(0)/w_i)/|s_lam,i|``.
    """
    v0, _, _, _, _ = dual_value_1d(scores, weights, bins, ZERO)
    assert isinstance(v0, Fraction)
    radius = None
    for row, weight in zip(scores, weights, strict=True):
        if row[1] == 0:
            continue
        centre = row[0] / row[1]
        half = rational_sqrt_upper(v0 / weight) / abs(row[1])
        bound = abs(centre) + half
        if radius is None or bound < radius:
            radius = bound
    if radius is None:
        return ZERO  # no nuisance span: v_K is constant in beta
    return radius


def exact_dual_min_1d(
    scores: Sequence[Row], weights: Sequence[Fraction], bins: int, max_steps: int = 4000
) -> dict[str, object]:
    """Exact minimizer of the convex piecewise-quadratic ``v_K`` (d_lambda=1).

    Bracketing bisection on the sign of the one-sided derivatives, accelerated
    by probing the vertex of the active quadratic at each bracket end and the
    crossing root of the two end-active quadratics.  A probe point ``x`` is
    certified as a minimizer exactly when ``D-(x) <= 0 <= D+(x)``.  The
    returned dictionary carries the exact minimizer (rational or ``QSqrt``),
    the exact value, the certificate derivatives and the probe count.
    """
    if all(row[1] == 0 for row in scores):
        v0, z, _, _, _ = dual_value_1d(scores, weights, bins, ZERO)
        return {"beta": QSqrt(0), "value": v0, "active": z, "probes": 1, "kind": "constant"}
    radius = coercivity_radius(scores, weights, bins)
    lo, hi = -radius - 1, radius + 1
    probes = 0
    tested: set[object] = set()

    def probe(x: Fraction | QSqrt) -> tuple[int, dict[str, object] | None]:
        nonlocal probes
        probes += 1
        v, z_r, d_r, z_l, d_l = dual_value_1d(scores, weights, bins, x)
        if d_l <= 0 <= d_r:
            return 0, {
                "beta": x if isinstance(x, QSqrt) else QSqrt(x),
                "value": v,
                "active_right": z_r,
                "active_left": z_l,
                "derivative_right": d_r,
                "derivative_left": d_l,
                "probes": probes,
            }
        return (1 if d_l > 0 else -1), None

    info_lo: tuple[Fraction, Fraction, Fraction] | None = None
    info_hi: tuple[Fraction, Fraction, Fraction] | None = None

    def rational_below(x: QSqrt, lo_bound: Fraction) -> Fraction:
        digits = 12
        while True:
            low, _ = x.enclosure(digits)
            if low > lo_bound:
                return low
            digits *= 2

    def rational_above(x: QSqrt, hi_bound: Fraction) -> Fraction:
        digits = 12
        while True:
            _, high = x.enclosure(digits)
            if high < hi_bound:
                return high
            digits *= 2

    for _ in range(max_steps):
        candidates: list[Fraction | QSqrt] = []
        if info_lo is not None and info_hi is not None and info_lo != info_hi:
            da, db, dc = (l - r for l, r in zip(info_lo, info_hi, strict=True))
            for root in quadratic_roots(da, db, dc):
                if lo < root < hi:
                    candidates.append(root if not root.is_rational() else root.a)
        for q in (info_lo, info_hi):
            if q is not None and q[0] > 0:
                vertex = -q[1] / (2 * q[0])
                if lo < vertex < hi:
                    candidates.append(vertex)
        candidates.append((lo + hi) / 2)
        for x in candidates:
            key = x if isinstance(x, QSqrt) else QSqrt(x)
            if key in tested:
                continue
            tested.add(key)
            probes += 1
            v, z_r, d_r, z_l, d_l = dual_value_1d(scores, weights, bins, x)
            if d_l <= 0 <= d_r:
                return {
                    "beta": key,
                    "value": v,
                    "active_right": z_r,
                    "active_left": z_l,
                    "derivative_right": d_r,
                    "derivative_left": d_l,
                    "probes": probes,
                    "kind": "rational" if key.is_rational() else "algebraic",
                    "bracket_width_at_exit": hi - lo,
                    "radius": radius,
                }
            if d_l > 0:  # minimizer lies strictly to the left of x
                if isinstance(x, QSqrt):
                    x = rational_above(x, hi)
                    _, _, _, z_l, _ = dual_value_1d(scores, weights, bins, x)
                hi = x
                info_hi = tilt_quadratic_1d(binned_information(scores, weights, z_l, bins))
            else:  # d_r < 0: minimizer lies strictly to the right of x
                if isinstance(x, QSqrt):
                    x = rational_below(x, lo)
                    _, z_r, _, _, _ = dual_value_1d(scores, weights, bins, x)
                lo = x
                info_lo = tilt_quadratic_1d(binned_information(scores, weights, z_r, bins))
            break
    raise RuntimeError("exact 1-D minimisation did not certify within max_steps")


# --------------------------------------------------------------------------- #
# Deterministic randomness, provenance, serialisation
# --------------------------------------------------------------------------- #
class Lcg:
    """64-bit linear congruential generator (Knuth MMIX constants)."""

    def __init__(self, seed: int) -> None:
        self.state = seed & ((1 << 64) - 1)

    def next_int(self, bound: int) -> int:
        self.state = (self.state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return (self.state >> 33) % bound

    def choice(self, items: Sequence[object]) -> object:
        return items[self.next_int(len(items))]


def seed_for(n: int, rep: int) -> int:
    return SEED_BASE + 1000 * n + rep


def random_table(n: int, d_lambda: int, rep: int, weight_pool: Sequence[int] = (1, 2, 3, 5)) -> Table:
    """Small-rational table: numerators in [-4,4], denominators in {1,2,4}."""
    rng = Lcg(seed_for(n, rep) * 7919 + d_lambda)
    scores: list[Row] = []
    for _ in range(n):
        row = []
        for _k in range(1 + d_lambda):
            num = rng.next_int(9) - 4
            den = (1, 2, 4)[rng.next_int(3)]
            row.append(F(num, den))
        scores.append(tuple(row))
    raw = [weight_pool[rng.next_int(len(weight_pool))] for _ in range(n)]
    total = sum(raw)
    return scores, [F(r, total) for r in raw]


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=WORKSPACE, capture_output=True, check=True, text=True
    ).stdout.strip()


def provenance(stage: str, started: float, extra: dict[str, object] | None = None) -> dict[str, object]:
    script = Path(__file__).resolve()
    payload: dict[str, object] = {
        "schema_version": 1,
        "audit": AUDIT_ID,
        "stage": stage,
        "created_utc": datetime.now(UTC).isoformat(),
        "git_revision": _git("rev-parse", "HEAD"),
        "git_status_short": _git("status", "--short"),
        "frozen_theorem_source": "research-ds-practical-certified-solver@2c9cb77",
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "runtime_seconds": round(time.monotonic() - started, 3),
        "arithmetic": "fractions.Fraction; quadratic irrationals exact in Q(sqrt D) (QSqrt)",
        "seed_formula": f"seed(n, rep) = {SEED_BASE} + 1000*n + rep",
        "independence": "no import of py/ds_practical_certified_solver.py or scorequant",
    }
    if extra:
        payload.update(extra)
    return payload


def _json_default(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, QSqrt):
        return value.to_json()
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"cannot serialise {type(value)}")


def write_artifact(name: str, payload: dict[str, object]) -> Path:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / f"{name}.json"
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=_json_default) + "\n",
        encoding="utf-8",
    )
    return path


def fmt(value: object) -> str:
    if isinstance(value, Fraction):
        return f"{value} ({float(value):.6g})"
    if isinstance(value, QSqrt):
        return f"{value!r} ({float(value):.9g})"
    return str(value)


# =========================================================================== #
# Shared table catalogue
# =========================================================================== #
def fixture_001_table() -> Table:
    scores: list[Row] = [
        (F(-11, 2), F(39, 8)),
        (F(3, 2), F(-65, 8)),
        (F(7, 2), F(31, 8)),
        (F(9, 2), F(-49, 8)),
    ]
    return scores, [F(1, 4)] * 4


def adversarial_tables() -> list[tuple[str, Table, list[int]]]:
    """Named attack tables ``(name, (scores, weights), K list)``; d_lambda = 1 unless noted."""
    def w(*raw: int) -> list[Fraction]:
        total = sum(raw)
        return [F(r, total) for r in raw]

    tables: list[tuple[str, Table, list[int]]] = [
        ("fixture_001", fixture_001_table(), [2, 3]),
        (
            "tilt_ties_unequal_weights",  # rows 0..3 all tie at beta=1 (T=0), row 4 does not
            ([(F(0), F(0)), (F(1), F(1)), (F(2), F(2)), (F(3), F(3)), (F(1), F(-1))], w(1, 2, 3, 4, 5)),
            [2, 3, 4],
        ),
        (
            "duplicate_full_score_rows",
            ([(F(-1), F(0)), (F(-1), F(0)), (F(0), F(1)), (F(1), F(0)), (F(1), F(0))], w(1, 3, 2, 2, 1)),
            [2, 3, 4],
        ),
        (
            "all_nuisance_zero_regular_class_empty",
            ([(F(-1), F(0)), (F(0), F(0)), (F(1), F(0)), (F(2), F(0))], w(1, 1, 1, 1)),
            [2, 3],
        ),
        (
            "partially_singular_partitions",
            ([(F(-1), F(1)), (F(0), F(0)), (F(1), F(-1)), (F(2), F(0)), (F(1, 2), F(2))], w(2, 1, 2, 1, 1)),
            [2, 3, 4],
        ),
        (
            "near_singular_nuisance",
            ([(F(-1), F(0)), (F(-1, 2), F(1, 1000)), (F(1, 2), F(-1, 1000)), (F(1), F(0)), (F(3, 2), F(1, 1000))], w(1, 1, 1, 1, 1)),
            [2, 3],
        ),
        (
            "tiny_positive_weights",
            ([(F(-2), F(1)), (F(-1), F(-1)), (F(0), F(2)), (F(1), F(-2)), (F(2), F(1))], w(1, 1, 1, 1000, 1)),
            [2, 3],
        ),
        (
            "origin_atom_and_singletons",
            ([(F(0), F(0)), (F(0), F(0)), (F(1), F(1)), (F(-1), F(2)), (F(2), F(-1))], w(1, 1, 1, 1, 1)),
            [2, 3, 4],
        ),
        (
            "centered_symmetric",
            ([(F(-2), F(1)), (F(-1), F(-1)), (F(1), F(-1)), (F(2), F(1))], w(1, 1, 1, 1)),
            [2, 3],
        ),
    ]
    return tables


def adversarial_tables_2d() -> list[tuple[str, Table, list[int]]]:
    def w(*raw: int) -> list[Fraction]:
        total = sum(raw)
        return [F(r, total) for r in raw]

    return [
        (
            "dl2_generic",
            ([(F(1), F(1), F(0)), (F(-1), F(0), F(1)), (F(2), F(-1), F(1)), (F(0), F(1), F(-1)), (F(-2), F(-1), F(-1))], w(1, 2, 1, 1, 2)),
            [2, 3, 4],
        ),
        (
            "dl2_common_null_direction",  # lambda_2 = 2 lambda_1 on every row
            ([(F(1), F(1), F(2)), (F(-1), F(0), F(0)), (F(2), F(-1), F(-2)), (F(0), F(1, 2), F(1)), (F(-3, 2), F(-1), F(-2))], w(1, 1, 1, 1, 1)),
            [2, 3],
        ),
        (
            "dl2_singular_cells",
            ([(F(1), F(1), F(0)), (F(-1), F(-1), F(0)), (F(2), F(0), F(1)), (F(-2), F(0), F(-1)), (F(1, 2), F(0), F(0))], w(1, 1, 1, 1, 1)),
            [2, 3, 4],
        ),
    ]


def probe_tilts_1d() -> list[Fraction]:
    return [F(-2), F(-1), F(-1, 2), ZERO, F(1, 2), F(1), F(2)]


def probe_tilts_2d() -> list[list[Fraction]]:
    return [[ZERO, ZERO], [ONE, ZERO], [ZERO, ONE], [F(-1, 2), F(1, 2)], [ONE, ONE], [F(-1), F(2)]]


def dp_value_any_dim(
    scores: Sequence[Row], weights: Sequence[Fraction], bins: int, beta: Sequence[Fraction | QSqrt]
) -> tuple[Fraction | QSqrt, tuple[int, ...]]:
    """``v_K(beta)`` by the interval DP in the sorted (index-tie-broken) order."""
    values = tilted_values(scores, beta)
    order = sorted_order(values)
    value, labels, _ = interval_dp(values, weights, bins, order)
    return value, labels


def subgradient(
    scores: Sequence[Row], weights: Sequence[Fraction], labels: Sequence[int], bins: int, beta: Sequence[Fraction]
) -> list[Fraction]:
    """``grad_beta V_z(beta) = -2 sum_b M_b(beta) L_b / W_b`` (a subgradient of v_K if z is active)."""
    masses, sums = cell_sums(scores, weights, labels, bins)
    dl = len(beta)
    grad = [ZERO] * dl
    for mass, vec in zip(masses, sums, strict=True):
        moment = vec[0] - sum(b * vec[1 + k] for k, b in enumerate(beta))
        for k in range(dl):
            grad[k] += -2 * moment * vec[1 + k] / mass
    return grad


# =========================================================================== #
# Stage: witness
# =========================================================================== #
def envelope_active_set(
    quads: dict[tuple[int, ...], tuple[Fraction, Fraction, Fraction]],
) -> set[tuple[int, ...]]:
    """Labelings whose quadratic touches the upper envelope somewhere (brute force).

    Evaluated at every pairwise crossing root, at every vertex, at midpoints
    between consecutive distinct candidate points and beyond the extremes.
    """
    keys = list(quads)
    points: list[QSqrt] = []
    for i in range(len(keys)):
        a, b, c = quads[keys[i]]
        if a > 0:
            points.append(QSqrt(-b / (2 * a)))
        for j in range(i + 1, len(keys)):
            a2, b2, c2 = quads[keys[j]]
            points.extend(quadratic_roots(a - a2, b - b2, c - c2))
    if not points:
        points = [QSqrt(0)]
    points = sorted_distinct(points)
    extended: list[QSqrt] = [points[0] - 1]
    for left, right in zip(points, points[1:], strict=False):
        extended.append(left)
        extended.append(QSqrt(rational_between(left, right)))
    extended.append(points[-1])
    extended.append(points[-1] + 1)
    active: set[tuple[int, ...]] = set()
    for x in extended:
        best = None
        here: list[tuple[int, ...]] = []
        for key in keys:
            a, b, c = quads[key]
            val = a * x * x + b * x + c
            if best is None or val > best:
                best, here = val, [key]
            elif val == best:
                here.append(key)
        active.update(here)
    return active


def stage_witness() -> dict[str, object]:
    started = time.monotonic()
    scores, weights = fixture_001_table()
    bins = 3
    partitions = list(canonical_partitions(4, bins))
    rows = {}
    quads: dict[tuple[int, ...], tuple[Fraction, Fraction, Fraction]] = {}
    for z in partitions:
        info = binned_information(scores, weights, z, bins)
        value, regular, beta_z = profiled_value(info)
        quads[z] = tilt_quadratic_1d(info)
        rows[z] = {"phi_plus": value, "regular": regular, "beta_z": beta_z[0], "quadratic_ABC": quads[z]}
    g_plus = max(r["phi_plus"] for r in rows.values())
    g_reg = max(r["phi_plus"] for r in rows.values() if r["regular"])
    first, optimum = (0, 0, 1, 2), (0, 1, 2, 2)
    alpha = F(14, 25)
    mixture = tuple(alpha * l + (1 - alpha) * r for l, r in zip(quads[first], quads[optimum], strict=True))
    ma, mb, mc = mixture
    vertex = -mb / (2 * ma)
    mixture_min = ma * vertex * vertex + mb * vertex + mc
    lower_gap = mixture_min - g_plus
    exact = exact_dual_min_1d(scores, weights, bins)
    beta_star = exact["beta"]
    d_exact = exact["value"]
    brute_d, active_at_star = brute_dual_value(scores, weights, bins, [beta_star])
    derivs = {z: 2 * quads[z][0] * beta_star + quads[z][1] for z in active_at_star}
    left = min(derivs.values())
    right = max(derivs.values())
    p_plus_set = envelope_active_set(quads)
    p_plus = max(rows[z]["phi_plus"] for z in p_plus_set)
    p_reg = max(rows[z]["phi_plus"] for z in p_plus_set if rows[z]["regular"])
    # is any labeling a saddle?
    saddles = []
    for z in partitions:
        bz = rows[z]["beta_z"]
        vz, act = brute_dual_value(scores, weights, bins, [bz])
        if z in act:
            saddles.append(z)
    n3k3 = list(canonical_partitions(3, 3))
    result = {
        "provenance": provenance("witness", started),
        "fixture": "CE-DS-TILT-DUAL-GAP-001",
        "K": bins,
        "canonical_partitions": len(partitions),
        "regular_partitions": sum(r["regular"] for r in rows.values()),
        "per_partition": {str(list(z)): r for z, r in rows.items()},
        "global_generalized_value": g_plus,
        "global_regular_value": g_reg,
        "global_labels": [list(z) for z, r in rows.items() if r["phi_plus"] == g_plus],
        "registered_global_value": F(116805, 11816),
        "registered_first_quadratic": (F(925, 64), F(15, 4), F(81, 8)),
        "registered_optimum_quadratic": (F(1477, 64), F(24), F(129, 8)),
        "first_quadratic_matches": quads[first] == (F(925, 64), F(15, 4), F(81, 8)),
        "optimum_quadratic_matches": quads[optimum] == (F(1477, 64), F(24), F(129, 8)),
        "mixture_alpha": alpha,
        "mixture_quadratic": mixture,
        "mixture_vertex": vertex,
        "mixture_minimum": mixture_min,
        "certified_gap_lower_bound": lower_gap,
        "registered_gap_lower_bound": F(105329256, 154014175),
        "certificate_matches": (
            vertex == F(-10128, 29197)
            and mixture_min == F(61717893, 5839400)
            and lower_gap == F(105329256, 154014175)
        ),
        "exact_dual_minimizer": beta_star,
        "exact_dual_minimum": d_exact,
        "exact_dual_minimizer_kind": exact["kind"],
        "exact_probe_count": exact["probes"],
        "brute_force_dual_at_minimizer": brute_d,
        "brute_matches_dp": brute_d == d_exact,
        "active_labelings_at_minimizer": [list(z) for z in active_at_star],
        "subgradient_interval_at_minimizer": [left, right],
        "zero_in_subgradient": left <= 0 <= right,
        "exact_duality_gap": d_exact - g_plus,
        "exact_gap_exceeds_certificate": (d_exact - g_plus) >= lower_gap,
        "dp_active_primal_p_plus": p_plus,
        "dp_active_primal_p_reg": p_reg,
        "dp_active_labelings": [list(z) for z in sorted(p_plus_set)],
        "bracket_chain_p_plus_le_g_plus_le_d": p_plus <= g_plus <= d_exact,
        "saddle_labelings": [list(z) for z in saddles],
        "closure": g_plus == d_exact,
        "N3_K3_partitions": [list(z) for z in n3k3],
        "N3_K3_closes": len(n3k3) == 1,
    }
    result["N3_K2_search"] = search_n3_k2_witness()
    write_artifact("witness", result)
    print(
        f"witness: g={g_plus} d_exact={fmt(d_exact)} gap={fmt(d_exact - g_plus)} "
        f"cert={float(lower_gap):.6f} closure={result['closure']} "
        f"N3K2 minimal={result['N3_K2_search']['minimal']['scores'] if result['N3_K2_search']['minimal'] else None}"
    )
    return result


def search_n3_k2_witness() -> dict[str, object]:
    """Exhaust equal-weight N=3 integer tables in [-2,2]^2 for a K=2 tilt-dual gap."""
    grid = [F(v) for v in range(-2, 3)]
    weights = [F(1, 3)] * 3
    found: list[dict[str, object]] = []
    tables = 0
    partitions = list(canonical_partitions(3, 2))
    seen: set[tuple[Row, ...]] = set()
    for rows in product(product(grid, repeat=2), repeat=3):
        key = tuple(sorted(rows))
        if key in seen or len(set(rows)) < 3:
            continue
        seen.add(key)
        scores = [tuple(r) for r in key]
        tables += 1
        if all(r[1] == 0 for r in scores):
            continue
        values = {}
        for z in partitions:
            info = binned_information(scores, weights, z, 2)
            values[z] = profiled_value(info)
        g_plus = max(v[0] for v in values.values())
        exact = exact_dual_min_1d(scores, weights, 2)
        d = exact["value"]
        gap = d - g_plus
        if gap > 0:
            size = (max(abs(x) for r in scores for x in r), sum(abs(x) for r in scores for x in r))
            found.append({"scores": scores, "g_plus": g_plus, "d": d, "gap": gap, "size": size, "beta": exact["beta"]})
    found.sort(key=lambda e: (e["size"], -float(e["gap"]), str(e["scores"])))  # type: ignore[index]
    minimal = None
    if found:
        best = found[0]
        # prefer, among the smallest-size tables, the largest gap; then build a rational certificate
        scores = best["scores"]  # type: ignore[assignment]
        beta_star = best["beta"]
        quads = {z: tilt_quadratic_1d(binned_information(scores, weights, z, 2)) for z in partitions}
        _, active = brute_dual_value(scores, weights, 2, [beta_star])
        certificate = rational_mixture_certificate(quads, active, beta_star, best["g_plus"])  # type: ignore[arg-type]
        phis = {z: profiled_value(binned_information(scores, weights, z, 2)) for z in partitions}
        minimal = {
            "scores": scores,
            "weights": weights,
            "K": 2,
            "canonical_partitions": [list(z) for z in partitions],
            "phi_plus": {str(list(z)): v[0] for z, v in phis.items()},
            "regular": {str(list(z)): v[1] for z, v in phis.items()},
            "quadratics_ABC": {str(list(z)): q for z, q in quads.items()},
            "g_plus": best["g_plus"],
            "exact_dual_minimizer": beta_star,
            "exact_dual_minimum": best["d"],
            "exact_gap": best["gap"],
            "active_at_minimizer": [list(z) for z in active],
            "rational_certificate": certificate,
        }
    return {
        "grid": "integer coordinates in [-2,2]^2, three distinct rows, equal weights 1/3",
        "tables": tables,
        "tables_with_gap": len(found),
        "largest_gap": max((e["gap"] for e in found), default=None),
        "minimal": minimal,
    }


def rational_mixture_certificate(
    quads: dict[tuple[int, ...], tuple[Fraction, Fraction, Fraction]],
    active: Sequence[tuple[int, ...]],
    beta_star: QSqrt,
    g_plus: Fraction,
) -> dict[str, object] | None:
    """Rational alpha in [0,1] with min_beta(alpha q1 + (1-alpha) q2) > g_plus."""
    if len(active) < 2:
        return None
    z1, z2 = active[0], active[1]
    q1, q2 = quads[z1], quads[z2]
    d1 = 2 * q1[0] * beta_star + q1[1]
    d2 = 2 * q2[0] * beta_star + q2[1]
    if (d1 > 0) == (d2 > 0):
        return None
    alpha_star = d2 / (d2 - d1)  # makes the mixture derivative vanish at beta_star
    lo, hi = alpha_star.enclosure(12)
    best: dict[str, object] | None = None
    for den in (2, 3, 4, 5, 10, 25, 50, 100, 1000, 10000):
        for num in range(int(lo * den) - 1, int(hi * den) + 2):
            alpha = F(num, den)
            if not (0 <= alpha <= 1):
                continue
            mixture = tuple(alpha * l + (1 - alpha) * r for l, r in zip(q1, q2, strict=True))
            a, b, c = mixture
            if a <= 0:
                continue
            vertex = -b / (2 * a)
            minimum = a * vertex * vertex + b * vertex + c
            if minimum > g_plus and (best is None or minimum > best["mixture_minimum"]):  # type: ignore[operator]
                best = {
                    "labels_first": list(z1),
                    "labels_second": list(z2),
                    "alpha_on_first": alpha,
                    "mixture_quadratic_ABC": mixture,
                    "mixture_vertex": vertex,
                    "mixture_minimum": minimum,
                    "certified_gap_lower_bound": minimum - g_plus,
                }
    return best


# =========================================================================== #
# Stage: ceiling (weak duality, DS11 identity, DS9/DS11 split), N <= 10
# =========================================================================== #
def catalogue_1d(max_n: int = 10) -> list[tuple[str, Table, list[int]]]:
    tables = list(adversarial_tables())
    for n in range(3, max_n + 1):
        for rep in (0, 1):
            ks = [k for k in (2, 3, 4) if k <= n]
            tables.append((f"random_dl1_n{n}_rep{rep}", random_table(n, 1, rep), ks))
    return tables


def catalogue_2d(max_n: int = 8) -> list[tuple[str, Table, list[int]]]:
    tables = list(adversarial_tables_2d())
    for n in range(4, max_n + 1):
        for rep in (0, 1):
            ks = [k for k in (2, 3, 4) if k <= n]
            tables.append((f"random_dl2_n{n}_rep{rep}", random_table(n, 2, rep), ks))
    return tables


def analyse_table(
    name: str, table: Table, bins: int, exact_min: bool, primal: bool
) -> dict[str, object]:
    scores, weights = table
    dl = len(scores[0]) - 1
    n = len(scores)
    probes: list[list[Fraction]] = (
        [[b] for b in probe_tilts_1d()] if dl == 1 else probe_tilts_2d()
    )
    partitions = list(canonical_partitions(n, bins))
    info_of = {}
    phi = {}
    regular = {}
    beta_z = {}
    null_of = {}
    for z in partitions:
        info = binned_information(scores, weights, z, bins)
        value, reg, bz = profiled_value(info)
        dlam = len(info) - 1
        lam = [[info[1 + r][1 + c] for c in range(dlam)] for r in range(dlam)]
        rhs = [info[0][1 + c] for c in range(dlam)]
        solved = solve_normal_equation(lam, rhs)
        assert solved is not None
        info_of[z], phi[z], regular[z], beta_z[z], null_of[z] = info, value, reg, bz, solved[1]
    g_plus = max(phi.values())
    g_reg = max((phi[z] for z in partitions if regular[z]), default=None)
    ds11_violations = 0
    cos_violations = 0
    null_violations = 0
    weak_violations = 0
    contiguity_disagreements = 0
    dual_probe_values = []
    extra_probes = list(probes) + [beta_z[z] for z in partitions if phi[z] == g_plus][:1]
    for beta in extra_probes:
        brute, _ = brute_dual_value(scores, weights, bins, beta)
        dp, _ = dp_value_any_dim(scores, weights, bins, beta)
        if brute != dp:
            contiguity_disagreements += 1
        dual_probe_values.append(brute)
        for z in partitions:
            vz = tilted_form(info_of[z], beta)
            if not (phi[z] <= vz <= brute):
                weak_violations += 1
            # completion of squares: V_z(beta) - Phi+ = (beta - beta_z) I_ll (beta - beta_z)^T
            diff = [b - bz for b, bz in zip(beta, beta_z[z], strict=True)]
            quad = ZERO
            for r in range(dl):
                for c in range(dl):
                    quad += diff[r] * info_of[z][1 + r][1 + c] * diff[c]
            if vz - phi[z] != quad:
                cos_violations += 1
    for z in partitions:
        if tilted_form(info_of[z], beta_z[z]) != phi[z]:
            ds11_violations += 1
        for vec in null_of[z]:
            for t in (ONE, F(-3)):
                shifted = [b + t * v for b, v in zip(beta_z[z], vec, strict=True)]
                if tilted_form(info_of[z], shifted) != phi[z]:
                    null_violations += 1
    out: dict[str, object] = {
        "name": name,
        "N": n,
        "K": bins,
        "d_lambda": dl,
        "canonical_partitions": len(partitions),
        "regular_partitions": sum(regular.values()),
        "singular_partitions": sum(not r for r in regular.values()),
        "g_plus": g_plus,
        "g_reg": g_reg,
        "g_plus_exceeds_g_reg": (g_reg is None) or (g_plus > g_reg),
        "global_generalized_labels": [list(z) for z in partitions if phi[z] == g_plus][:4],
        "global_is_regular": any(regular[z] for z in partitions if phi[z] == g_plus),
        "ds11_normal_equation_violations": ds11_violations,
        "completion_of_squares_violations": cos_violations,
        "null_direction_invariance_violations": null_violations,
        "weak_duality_violations": weak_violations,
        "contiguity_disagreements": contiguity_disagreements,
        "probe_count": len(extra_probes),
        "min_probe_dual": min(dual_probe_values),
        "g_plus_le_min_probe_dual": g_plus <= min(dual_probe_values),
    }
    if exact_min and dl == 1:
        exact = exact_dual_min_1d(scores, weights, bins)
        d = exact["value"]
        out["exact_dual_minimum"] = d
        out["exact_dual_minimizer"] = exact["beta"]
        out["exact_minimizer_kind"] = exact["kind"]
        out["exact_probes"] = exact["probes"]
        out["radius"] = exact.get("radius")
        out["g_plus_le_d"] = g_plus <= d
        out["closed"] = g_plus == d
        out["exact_gap"] = d - g_plus
    if primal and dl == 1:
        quads = {z: tilt_quadratic_1d(info_of[z]) for z in partitions}
        active = envelope_active_set(quads)
        p_plus = max(phi[z] for z in active)
        p_reg = max((phi[z] for z in active if regular[z]), default=None)
        out["dp_active_labelings"] = len(active)
        out["p_plus"] = p_plus
        out["p_reg"] = p_reg
        out["p_plus_lt_g_plus"] = p_plus < g_plus
        out["p_plus_le_g_plus"] = p_plus <= g_plus
        out["p_reg_le_g_reg"] = True if g_reg is None or p_reg is None else p_reg <= g_reg
        out["singular_dp_active_count"] = sum(not regular[z] for z in active)
    # refinement monotonicity spot check (split one cell of every K-cell labeling into two)
    if bins < n and n <= 7:
        mono_violations = 0
        checks = 0
        for z in partitions:
            for cell in range(bins):
                members = [i for i, l in enumerate(z) if l == cell]
                if len(members) < 2:
                    continue
                moved = list(z)
                moved[members[0]] = bins
                refined = canonicalize(moved)
                info_r = binned_information(scores, weights, refined, bins + 1)
                value_r, reg_r, _ = profiled_value(info_r)
                checks += 1
                if value_r < phi[z] or (regular[z] and not reg_r):
                    mono_violations += 1
        out["refinement_checks"] = checks
        out["refinement_violations"] = mono_violations
    return out


def stage_ceiling() -> dict[str, object]:
    started = time.monotonic()
    reports = []
    for name, table, ks in catalogue_1d(10) + catalogue_2d(8):
        for k in ks:
            n = len(table[0])
            reports.append(analyse_table(name, table, k, exact_min=(len(table[0][0]) == 2 and n <= 8), primal=(n <= 6)))
    def total(key: str) -> int:
        return sum(int(r.get(key, 0)) for r in reports)
    summary = {
        "tables": len(reports),
        "canonical_partitions": total("canonical_partitions"),
        "weak_duality_violations": total("weak_duality_violations"),
        "ds11_normal_equation_violations": total("ds11_normal_equation_violations"),
        "completion_of_squares_violations": total("completion_of_squares_violations"),
        "null_direction_invariance_violations": total("null_direction_invariance_violations"),
        "contiguity_disagreements": total("contiguity_disagreements"),
        "refinement_violations": total("refinement_violations"),
        "g_plus_le_probe_dual_failures": sum(not r["g_plus_le_min_probe_dual"] for r in reports),
        "g_plus_le_exact_d_failures": sum(1 for r in reports if "g_plus_le_d" in r and not r["g_plus_le_d"]),
        "closed_brackets": sum(1 for r in reports if r.get("closed")),
        "open_brackets": sum(1 for r in reports if r.get("closed") is False),
        "tables_where_generalized_exceeds_regular": sum(1 for r in reports if r["g_reg"] is not None and r["g_plus"] > r["g_reg"]),
        "tables_with_empty_regular_class": sum(1 for r in reports if r["g_reg"] is None),
        "tables_with_p_plus_strictly_below_g_plus": sum(1 for r in reports if r.get("p_plus_lt_g_plus")),
        "p_plus_le_g_plus_failures": sum(1 for r in reports if "p_plus_le_g_plus" in r and not r["p_plus_le_g_plus"]),
        "p_reg_le_g_reg_failures": sum(1 for r in reports if "p_reg_le_g_reg" in r and not r["p_reg_le_g_reg"]),
        "singular_dp_active_labelings": total("singular_dp_active_count"),
    }
    payload = {"provenance": provenance("ceiling", started), "summary": summary, "tables": reports}
    write_artifact("ceiling", payload)
    print(f"ceiling: {json.dumps(summary)}")
    return payload


# =========================================================================== #
# Stage: saddle (closure iff saddle; tie-masked closures), d_lambda = 1
# =========================================================================== #
def saddle_report(name: str, table: Table, bins: int) -> dict[str, object]:
    scores, weights = table
    n = len(scores)
    partitions = list(canonical_partitions(n, bins))
    phi, regular, beta_z, quads = {}, {}, {}, {}
    for z in partitions:
        info = binned_information(scores, weights, z, bins)
        value, reg, bz = profiled_value(info)
        phi[z], regular[z], beta_z[z], quads[z] = value, reg, bz[0], tilt_quadratic_1d(info)
    g_plus = max(phi.values())
    exact = exact_dual_min_1d(scores, weights, bins)
    beta_star, d = exact["beta"], exact["value"]
    closed = g_plus == d
    maximisers = [z for z in partitions if phi[z] == g_plus]
    _, active_star = brute_dual_value(scores, weights, bins, [beta_star])
    # (=>) every Phi+-maximizer must be active at beta* and solve its normal equation there
    forward_failures = 0
    if closed:
        for z in maximisers:
            in_active = z in active_star
            solves = (
                (quads[z][0] * beta_star * 2 + quads[z][1]) == 0  # d/dbeta V_z(beta*) = 0 <=> beta* I_ll = I_pl
            )
            if not (in_active and solves):
                forward_failures += 1
    # (<=) any labeling that is DP-active at a normal-equation solution closes the bracket
    saddles = []
    for z in partitions:
        if regular[z]:
            bz = beta_z[z]
            _, act = brute_dual_value(scores, weights, bins, [bz])
            if z in act:
                saddles.append(z)
        else:
            # I_ll = 0 => every beta solves; z is active somewhere iff its constant
            # quadratic reaches the dual minimum d (v_K >= d everywhere)
            if quads[z][0] == 0 and quads[z][1] == 0 and quads[z][2] == d:
                saddles.append(z)
    backward_failure = bool(saddles) and not closed
    regular_saddles = [z for z in saddles if regular[z]]
    # tie-masked closure: closed, but the active set at beta* contains a non-closing member
    non_closing_active = [z for z in active_star if phi[z] != g_plus]
    dp_right = exact["active_right"] if "active_right" in exact else None
    dp_left = exact["active_left"] if "active_left" in exact else None
    return {
        "name": name,
        "N": n,
        "K": bins,
        "partitions": len(partitions),
        "g_plus": g_plus,
        "d": d,
        "beta_star": beta_star,
        "minimizer_kind": exact["kind"],
        "closed": closed,
        "maximisers": [list(z) for z in maximisers],
        "active_at_beta_star": [list(z) for z in active_star],
        "forward_direction_failures": forward_failures,
        "saddle_labelings": [list(z) for z in saddles],
        "saddle_exists": bool(saddles),
        "iff_holds": (bool(saddles) == closed) and forward_failures == 0,
        "backward_failure": backward_failure,
        "regular_saddle_exists": bool(regular_saddles),
        "singular_only_saddle": bool(saddles) and not regular_saddles,
        "tie_masked_closure": closed and bool(non_closing_active),
        "non_closing_active_at_beta_star": [list(z) for z in non_closing_active],
        "deterministic_dp_right_labeling": list(dp_right) if dp_right else None,
        "deterministic_dp_left_labeling": list(dp_left) if dp_left else None,
        "deterministic_dp_right_closes": (dp_right is not None and phi[dp_right] == g_plus) if closed else None,
        "deterministic_dp_left_closes": (dp_left is not None and phi[dp_left] == g_plus) if closed else None,
    }


def tie_mask_search() -> dict[str, object]:
    """Exhaust small integer tables for a closed bracket whose DP tie set at beta* hides it."""
    found = []
    tables = 0
    grids = [(3, 2, 2), (4, 2, 1), (4, 3, 1), (3, 3, 2)]
    for n, k, radius in grids:
        grid = [F(v) for v in range(-radius, radius + 1)]
        weights = [F(1, n)] * n
        seen: set[tuple[Row, ...]] = set()
        for rows in product(product(grid, repeat=2), repeat=n):
            key = tuple(sorted(rows))
            if key in seen:
                continue
            seen.add(key)
            scores = [tuple(r) for r in key]
            if all(r[1] == 0 for r in scores) or len(set(scores)) < 2:
                continue
            tables += 1
            rep_out = saddle_report(f"grid_n{n}_k{k}", (scores, weights), k)
            if rep_out["tie_masked_closure"]:
                found.append({**rep_out, "scores": scores, "weights": weights})
    found.sort(key=lambda e: (e["N"], e["K"], not e["regular_saddle_exists"], sum(abs(x) for r in e["scores"] for x in r), str(e["scores"])))
    masked_deterministic = [e for e in found if not (e["deterministic_dp_right_closes"] and e["deterministic_dp_left_closes"])]
    regular_masked = [e for e in masked_deterministic if e["regular_saddle_exists"]]
    return {
        "grids": [f"N={n}, K={k}, integer coordinates in [-{r},{r}]^2, equal weights" for n, k, r in grids],
        "tables_searched": tables,
        "found": len(found),
        "found_where_deterministic_dp_reports_open": len(masked_deterministic),
        "smallest": found[0] if found else None,
        "smallest_deterministic_miss": masked_deterministic[0] if masked_deterministic else None,
        "found_with_regular_closing_labeling": len(regular_masked),
        "smallest_regular_miss": regular_masked[0] if regular_masked else None,
        "smallest_singular_miss": next((e for e in masked_deterministic if not e["regular_saddle_exists"]), None),
    }


def stage_saddle() -> dict[str, object]:
    started = time.monotonic()
    reports = []
    for name, table, ks in catalogue_1d(8):
        scores, _ = table
        if all(r[1] == 0 for r in scores):
            continue
        for k in ks:
            reports.append(saddle_report(name, table, k))
    tie_mask = tie_mask_search()
    summary = {
        "tables": len(reports),
        "iff_failures": sum(not r["iff_holds"] for r in reports),
        "forward_failures": sum(r["forward_direction_failures"] for r in reports),
        "backward_failures": sum(r["backward_failure"] for r in reports),
        "closed": sum(r["closed"] for r in reports),
        "open": sum(not r["closed"] for r in reports),
        "closed_with_regular_saddle": sum(r["regular_saddle_exists"] for r in reports),
        "closed_singular_only": sum(r["singular_only_saddle"] for r in reports),
        "algebraic_minimizers": sum(r["minimizer_kind"] == "algebraic" for r in reports),
        "tie_masked_closures_in_catalogue": sum(r["tie_masked_closure"] for r in reports),
        "deterministic_dp_missed_closure": sum(
            1 for r in reports if r["closed"] and (not r["deterministic_dp_right_closes"] or not r["deterministic_dp_left_closes"])
        ),
        "tie_mask_search_tables": tie_mask["tables_searched"],
        "tie_mask_search_found": tie_mask["found"],
    }
    payload = {"provenance": provenance("saddle", started), "summary": summary, "tables": reports, "tie_mask_search": tie_mask}
    write_artifact("saddle", payload)
    print(f"saddle: {json.dumps(summary)}")
    return payload


# =========================================================================== #
# Stage: ties (tie-order independence of the DP; one-sided derivative rules)
# =========================================================================== #
def all_tie_orders(values: Sequence[Fraction]) -> Iterator[list[int]]:
    groups: list[list[int]] = []
    for v in sorted(set(values)):
        groups.append([i for i, x in enumerate(values) if x == v])
    for perms in product(*[list(permutations(g)) for g in groups]):
        yield [i for g in perms for i in g]


def stage_ties() -> dict[str, object]:
    started = time.monotonic()
    cases: list[tuple[str, Table, Fraction, int]] = []
    def w(*raw: int) -> list[Fraction]:
        total = sum(raw)
        return [F(r, total) for r in raw]
    # rows tied at the named beta with unequal weights; extra untied rows
    cases.append(("four_way_tie_beta1", ([(F(0), F(0)), (F(1), F(1)), (F(2), F(2)), (F(3), F(3)), (F(1), F(-1))], w(1, 2, 3, 4, 5)), ONE, 3))
    cases.append(("four_way_tie_beta1_K2", ([(F(0), F(0)), (F(1), F(1)), (F(2), F(2)), (F(3), F(3)), (F(1), F(-1))], w(1, 2, 3, 4, 5)), ONE, 2))
    cases.append(("two_ties_beta0", ([(F(1), F(1)), (F(1), F(-2)), (F(-1), F(0)), (F(-1), F(3)), (F(0), F(1)), (F(2), F(1))], w(1, 5, 2, 1, 3, 1)), ZERO, 3))
    cases.append(("tie_with_duplicates_K4", ([(F(1), F(1)), (F(1), F(1)), (F(1), F(-2)), (F(-1), F(0)), (F(0), F(2)), (F(2), F(1))], w(1, 2, 3, 1, 1, 2)), ZERO, 4))
    cases.append(("all_tied_beta_half", ([(F(1), F(2)), (F(2), F(4)), (F(0), F(0)), (F(-1), F(-2)), (F(3, 2), F(3))], w(3, 1, 2, 5, 1)), F(1, 2), 3))
    cases.append(("tie_half_weights_K2", ([(F(0), F(0)), (F(1), F(1)), (F(2), F(2)), (F(1), F(-1)), (F(-2), F(0))], w(1, 4, 1, 2, 2)), ONE, 2))
    reports = []
    for name, (scores, weights), beta, bins in cases:
        values = [row[0] - beta * row[1] for row in scores]
        lam = [row[1] for row in scores]
        slopes = [-2 * l for l in lam]
        brute, active = brute_dual_value(scores, weights, bins, [beta])
        order_values = []
        orders = 0
        for order in all_tie_orders(values):
            orders += 1
            value, _, _ = interval_dp(values, weights, bins, order)
            order_values.append(value)
        quads = {z: tilt_quadratic_1d(binned_information(scores, weights, z, bins)) for z in active}
        derivs = [2 * q[0] * beta + q[1] for q in quads.values()]
        _, z_r, d_r, z_l, d_l = dual_value_1d(scores, weights, bins, beta)
        # right derivative must equal max over ALL active labelings; left the min
        tie_groups = [len([i for i, x in enumerate(values) if x == v]) for v in set(values)]
        # verify one-sided derivatives against exact finite differences at beta +/- h
        h = F(1, 10**6)
        v_plus, _, _, _, _ = dual_value_1d(scores, weights, bins, beta + h)
        v_minus, _, _, _, _ = dual_value_1d(scores, weights, bins, beta - h)
        q_r = tilt_quadratic_1d(binned_information(scores, weights, z_r, bins))
        q_l = tilt_quadratic_1d(binned_information(scores, weights, z_l, bins))
        reports.append({
            "name": name,
            "beta": beta,
            "K": bins,
            "tie_group_sizes": sorted(tie_groups, reverse=True),
            "tie_orders": orders,
            "brute_force_v_K": brute,
            "dp_values_all_orders_equal_brute": all(v == brute for v in order_values),
            "active_labelings": [list(z) for z in active],
            "active_count": len(active),
            "max_active_derivative": max(derivs),
            "min_active_derivative": min(derivs),
            "dp_right_derivative": d_r,
            "dp_left_derivative": d_l,
            "right_rule_correct": d_r == max(derivs),
            "left_rule_correct": d_l == min(derivs),
            "right_labeling_active_on_right": v_plus == q_r[0] * (beta + h) ** 2 + q_r[1] * (beta + h) + q_r[2],
            "left_labeling_active_on_left": v_minus == q_l[0] * (beta - h) ** 2 + q_l[1] * (beta - h) + q_l[2],
        })
    # the convexity lemma behind tie invariance: g -> (M + t g)^2 / (W + g) is convex on g >= 0
    lemma_checks = 0
    lemma_violations = 0
    rng = Lcg(SEED_BASE + 77)
    for _ in range(300):
        M = F(rng.next_int(21) - 10, 1 + rng.next_int(4))
        t = F(rng.next_int(21) - 10, 1 + rng.next_int(4))
        W = F(1 + rng.next_int(10), 1 + rng.next_int(4))
        gs = sorted({F(rng.next_int(20), 1 + rng.next_int(5)) for _ in range(3)})
        if len(gs) < 3:
            continue
        f = [(M + t * g) ** 2 / (W + g) for g in gs]
        g0, g1, g2 = gs
        # chord inequality: f(g1) <= f(g0) + (g1-g0)/(g2-g0) * (f(g2)-f(g0))
        lemma_checks += 1
        if f[1] > f[0] + (g1 - g0) / (g2 - g0) * (f[2] - f[0]):
            lemma_violations += 1
    summary = {
        "cases": len(reports),
        "total_tie_orders": sum(r["tie_orders"] for r in reports),
        "dp_value_order_dependence_found": sum(not r["dp_values_all_orders_equal_brute"] for r in reports),
        "right_rule_failures": sum(not r["right_rule_correct"] for r in reports),
        "left_rule_failures": sum(not r["left_rule_correct"] for r in reports),
        "one_sided_activity_failures": sum((not r["right_labeling_active_on_right"]) + (not r["left_labeling_active_on_left"]) for r in reports),
        "convexity_lemma_checks": lemma_checks,
        "convexity_lemma_violations": lemma_violations,
    }
    payload = {"provenance": provenance("ties", started), "summary": summary, "cases": reports}
    write_artifact("ties", payload)
    print(f"ties: {json.dumps(summary)}")
    return payload


# =========================================================================== #
# Stage: compute (radius, root-separation bit model, cutting-plane bracket,
# nuisance-span quotient, arrangement-cell counts)
# =========================================================================== #
def lcm_of(values: Sequence[int]) -> int:
    out = 1
    for v in values:
        out = out * v // math.gcd(out, v)
    return out


def bit_model_1d(scores: Sequence[Row], weights: Sequence[Fraction], bins: int, radius: Fraction) -> dict[str, object]:
    """A-priori integer height H of every pairwise quadratic difference and the
    resulting root-separation bound; all quantities polynomial in the input bits."""
    ds = lcm_of([x.denominator for r in scores for x in r])
    dw = lcm_of([w.denominator for w in weights])
    max_psi = max(abs(r[0]) for r in scores)
    max_lam = max(abs(r[1]) for r in scores)
    # |A| <= max s_lam^2, |B| <= 2 max|s_psi s_lam|, |C| <= max s_psi^2 (each q_z <= sum_i w_i t_i^2)
    coef_bound = max(max_lam * max_lam, 2 * max_psi * max_lam, max_psi * max_psi)
    den_bound = dw ** (bins + 1) * ds * ds  # common denominator of one q_z
    den_pair = den_bound * den_bound  # of a difference q_z - q_z'
    height = 2 * math.ceil(coef_bound * den_pair)
    # distinct real roots of two integer polynomials of degree <= 2 with height <= H:
    # |r - r'| >= 1 / (H^4 (2 (1+H))^3)  (resultant / Cauchy bound; see report §7)
    separation = F(1, height**4 * (2 * (1 + height)) ** 3)
    depth = math.ceil(math.log2(float(2 * (radius + 1) / separation))) if separation > 0 else None
    return {
        "score_denominator_lcm": ds,
        "weight_denominator_lcm": dw,
        "coefficient_bound": coef_bound,
        "single_quadratic_denominator_bound": den_bound,
        "pair_height_H": height,
        "pair_height_bits": height.bit_length(),
        "root_separation_lower_bound": separation,
        "root_separation_bits": -math.floor(math.log2(float(separation))),
        "radius": radius,
        "worst_case_bisection_depth": depth,
    }


def measured_heights_1d(scores: Sequence[Row], weights: Sequence[Fraction], bins: int) -> dict[str, object]:
    """Measured height of every pairwise difference and the minimal breakpoint separation."""
    quads = {}
    for z in canonical_partitions(len(scores), bins):
        quads[z] = tilt_quadratic_1d(binned_information(scores, weights, z, bins))
    keys = list(quads)
    max_height = 0
    roots: list[QSqrt] = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            diff = [l - r for l, r in zip(quads[keys[i]], quads[keys[j]], strict=True)]
            den = lcm_of([c.denominator for c in diff])
            ints = [abs(int(c * den)) for c in diff]
            max_height = max(max_height, *ints)
            roots.extend(quadratic_roots(*diff))
    distinct = sorted_distinct(roots)
    min_sep = None
    for a, b in zip(distinct, distinct[1:], strict=False):
        _, hi_a = a.enclosure(40)
        lo_b, _ = b.enclosure(40)
        lo = lo_b - hi_a  # rigorous lower bound on b - a across fields
        if min_sep is None or lo < min_sep:
            min_sep = lo
    return {"labelings": len(keys), "measured_pair_height": max_height, "distinct_breakpoint_candidates": len(distinct), "min_candidate_separation_lower_enclosure": min_sep}


def nuisance_span_quotient(scores: Sequence[Row]) -> tuple[list[Row], list[list[Fraction]], int]:
    """Reduce nuisance coordinates to a basis of their empirical span (common-null quotient).

    Returns the reduced table, the basis rows (in original coordinates) and the rank.
    """
    dl = len(scores[0]) - 1
    rows = [[r[1 + k] for k in range(dl)] for r in scores]
    # row-reduce the N x dl nuisance matrix to find pivot columns
    mat = [list(r) for r in rows]
    pivots: list[int] = []
    r = 0
    for c in range(dl):
        piv = next((i for i in range(r, len(mat)) if mat[i][c] != 0), None)
        if piv is None:
            continue
        mat[r], mat[piv] = mat[piv], mat[r]
        scale = mat[r][c]
        mat[r] = [v / scale for v in mat[r]]
        for i in range(len(mat)):
            if i != r and mat[i][c] != 0:
                f = mat[i][c]
                mat[i] = [vi - f * vr for vi, vr in zip(mat[i], mat[r], strict=True)]
        pivots.append(c)
        r += 1
        if r == dl:
            break
    # coordinates in the pivot columns are a valid parametrisation: every row lies in the
    # span, and the pivot-column projection is injective on the span
    reduced: list[Row] = [tuple([row[0]] + [row[1 + c] for c in pivots]) for row in scores]
    basis = [mat[i] for i in range(len(pivots))]
    return reduced, basis, len(pivots)


def box_radius_2d(scores: Sequence[Row], weights: Sequence[Fraction], bins: int) -> Fraction:
    """Rational box bound containing every dual minimizer when the nuisance rows span R^2."""
    v0, _ = dp_value_any_dim(scores, weights, bins, [ZERO, ZERO])
    slabs = []
    for row, w in zip(scores, weights, strict=True):
        if row[1] == 0 and row[2] == 0:
            continue
        slabs.append((row[1], row[2], row[0], rational_sqrt_upper(v0 / w)))
    best = None
    for (a1, b1, c1, h1), (a2, b2, c2, h2) in combinations(slabs, 2):
        det = a1 * b2 - a2 * b1
        if det == 0:
            continue
        corner_max = ZERO
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                r1, r2 = c1 + s1 * h1, c2 + s2 * h2
                x = (r1 * b2 - r2 * b1) / det
                y = (a1 * r2 - a2 * r1) / det
                corner_max = max(corner_max, abs(x), abs(y))
        if best is None or corner_max < best:
            best = corner_max
    assert best is not None, "nuisance rows do not span R^2 (quotient first)"
    return best


def kelley_bracket(
    scores: Sequence[Row], weights: Sequence[Fraction], bins: int, radius: Fraction, eps: Fraction, max_iter: int = 14
) -> dict[str, object]:
    """Certified rational bracket [L, U] on d = min v_K over the box |beta_j| <= radius (d_lambda=2).

    Upper bound: the best exact v_K value seen.  Lower bound: the exact minimum
    over the box of the cutting-plane model max_k (v_k + g_k.(beta - beta_k)),
    solved exactly by vertex enumeration (a valid lower bound because every
    cut is a global affine minorant of the convex v_K and the box contains a
    minimizer).  Kelley's method is the certificate mechanism only; the
    polynomial iteration count in the theorem is the ellipsoid/GLS bound.
    """
    cuts: list[tuple[Fraction, Fraction, Fraction, Fraction]] = []  # (v, g1, g2 ; at (b1,b2)) -> affine
    queries: list[list[Fraction]] = [[ZERO, ZERO]] + [[s1 * radius, s2 * radius] for s1 in (-1, 1) for s2 in (-1, 1)]
    upper = None
    history = []
    lower = None
    R = radius
    for it in range(max_iter):
        for beta in queries:
            v, labels = dp_value_any_dim(scores, weights, bins, beta)
            g = subgradient(scores, weights, labels, bins, beta)
            # affine: v + g.(x - beta) = (v - g.beta) + g.x
            cuts.append((v - g[0] * beta[0] - g[1] * beta[1], g[0], g[1], v))
            if upper is None or v < upper:
                upper = v
        queries = []
        # exact LP: minimise t s.t. t >= c_k + g_k.x over the box
        lines = [(c, g1, g2) for c, g1, g2, _ in cuts]
        candidates: list[tuple[Fraction, Fraction]] = [(s1 * R, s2 * R) for s1 in (-1, 1) for s2 in (-1, 1)]
        for (c1, a1, b1), (c2, a2, b2) in combinations(lines, 2):
            da, db, dc = a1 - a2, b1 - b2, c1 - c2  # tie line: da x + db y + dc = 0
            if da == 0 and db == 0:
                continue
            for edge in (-R, R):
                if db != 0:  # x = edge
                    candidates.append((edge, -(da * edge + dc) / db))
                if da != 0:  # y = edge
                    candidates.append((-(db * edge + dc) / da, edge))
        for (c1, a1, b1), (c2, a2, b2), (c3, a3, b3) in combinations(lines, 3):
            m11, m12, r1 = a1 - a2, b1 - b2, c2 - c1
            m21, m22, r2 = a1 - a3, b1 - b3, c3 - c1
            det = m11 * m22 - m12 * m21
            if det == 0:
                continue
            x = (r1 * m22 - r2 * m12) / det
            y = (m11 * r2 - m21 * r1) / det
            candidates.append((x, y))
        best_val = None
        best_pt = None
        for x, y in candidates:
            if abs(x) > R or abs(y) > R:
                continue
            val = max(c + a * x + b * y for c, a, b in lines)
            if best_val is None or val < best_val:
                best_val, best_pt = val, (x, y)
        assert best_val is not None and best_pt is not None
        lower = best_val
        history.append({"iteration": it, "cuts": len(cuts), "lower": lower, "upper": upper, "width": upper - lower})
        if upper - lower <= eps:
            break
        # round the next query to a 2^-16 grid: every query point yields a valid global
        # cut, and rounding keeps the bit size of all iterates bounded (the theorem's
        # polynomial bound uses the ellipsoid method with the same rounding discipline)
        grid = 1 << 16
        queries = [[F(round(best_pt[0] * grid), grid), F(round(best_pt[1] * grid), grid)]]
    return {"lower": lower, "upper": upper, "width": upper - lower, "iterations": len(history), "cuts": len(cuts), "converged": upper - lower <= eps, "eps": eps, "query_grid": "2^-16", "history_tail": history[-3:]}


def stage_compute() -> dict[str, object]:
    started = time.monotonic()
    radius_reports = []
    for name, table, ks in catalogue_1d(8):
        scores, weights = table
        if all(r[1] == 0 for r in scores):
            continue
        for k in ks:
            exact = exact_dual_min_1d(scores, weights, k)
            radius = exact["radius"]
            beta = exact["beta"]
            model = bit_model_1d(scores, weights, k, radius)
            entry = {
                "name": name, "N": len(scores), "K": k,
                "beta_star": beta, "radius": radius,
                "minimizer_inside_radius": abs(beta) <= radius,
                "probes_used": exact["probes"],
                "minimizer_kind": exact["kind"],
                "bit_model": model,
            }
            if len(scores) <= 6:
                measured = measured_heights_1d(scores, weights, k)
                entry["measured"] = measured
                entry["measured_height_within_bound"] = measured["measured_pair_height"] <= model["pair_height_H"]
                ms = measured["min_candidate_separation_lower_enclosure"]
                entry["measured_separation_within_bound"] = ms is None or ms >= model["root_separation_lower_bound"]
            radius_reports.append(entry)
    # d_lambda = 2: quotient, box radius, cutting-plane bracket
    bracket_reports = []
    for name, table, ks in catalogue_2d(5):
        scores, weights = table
        reduced, basis, rank = nuisance_span_quotient(scores)
        for k in ks[:1]:
            entry: dict[str, object] = {"name": name, "N": len(scores), "K": k, "nuisance_rank": rank}
            if rank == 2:
                radius = box_radius_2d(scores, weights, k)
                bracket = kelley_bracket(scores, weights, k, radius, F(1, 20))
                g_plus = max(profiled_value(binned_information(scores, weights, z, k))[0] for z in canonical_partitions(len(scores), k))
                entry.update({"box_radius": radius, "bracket": bracket, "g_plus": g_plus, "g_plus_le_upper": g_plus <= bracket["upper"], "lower_le_upper": bracket["lower"] <= bracket["upper"]})
            elif rank == 1:
                # exact via the 1-D algorithm on the quotient; constancy along the null direction
                exact = exact_dual_min_1d(reduced, weights, k)
                b = exact["beta"]
                # original coordinates: beta = (b, 0) in pivot coordinates; null direction from basis
                # basis row [1, m] means lambda_2 = m lambda_1, so beta.(l1,l2) = (beta1 + m beta2) l1
                m = basis[0][1]
                same = []
                for t in (ZERO, ONE, F(-5, 2)):
                    beta_full = [b - m * t, t]
                    v, _ = dp_value_any_dim(scores, weights, k, beta_full)
                    same.append(v)
                entry.update({"quotient_exact_d": exact["value"], "quotient_beta": b, "null_direction_slope": m, "v_K_constant_along_null_direction": all(v == same[0] for v in same), "constant_value_equals_quotient_d": same[0] == exact["value"]})
            bracket_reports.append(entry)
    # arrangement-cell sanity at d_lambda = 2
    arrangement = []
    for name, table, _ in catalogue_2d(6)[:4]:
        scores, weights = table
        n = len(scores)
        lines = sum(1 for i, j in combinations(range(n), 2) if scores[i][1:] != scores[j][1:])
        bound = 1 + lines + lines * (lines - 1) // 2
        seen = set()
        grid = [F(v, 2) for v in range(-8, 9)]
        for b1 in grid:
            for b2 in grid:
                values = tilted_values(scores, [b1, b2])
                seen.add(tuple(sorted_order(values)))
        arrangement.append({"name": name, "N": n, "pair_lines": lines, "cell_bound_1_plus_m_plus_C(m,2)": bound, "distinct_orders_on_grid": len(seen), "within_bound": len(seen) <= bound})
    summary = {
        "radius_tables": len(radius_reports),
        "minimizer_outside_radius": sum(not r["minimizer_inside_radius"] for r in radius_reports),
        "max_probes_used": max(r["probes_used"] for r in radius_reports),
        "max_worst_case_depth": max(r["bit_model"]["worst_case_bisection_depth"] for r in radius_reports),
        "measured_height_violations": sum(1 for r in radius_reports if "measured_height_within_bound" in r and not r["measured_height_within_bound"]),
        "measured_separation_violations": sum(1 for r in radius_reports if "measured_separation_within_bound" in r and not r["measured_separation_within_bound"]),
        "bracket_tables": len(bracket_reports),
        "brackets_converged": sum(1 for r in bracket_reports if r.get("bracket", {}).get("converged")),
        "bracket_validity_failures": sum(1 for r in bracket_reports if "bracket" in r and not (r["g_plus_le_upper"] and r["lower_le_upper"])),
        "quotient_tables": sum(1 for r in bracket_reports if r["nuisance_rank"] == 1),
        "quotient_failures": sum(1 for r in bracket_reports if r["nuisance_rank"] == 1 and not (r["v_K_constant_along_null_direction"] and r["constant_value_equals_quotient_d"])),
        "arrangement_bound_violations": sum(not a["within_bound"] for a in arrangement),
    }
    payload = {"provenance": provenance("compute", started), "summary": summary, "radius_and_bit_model": radius_reports, "brackets_2d": bracket_reports, "arrangement": arrangement}
    write_artifact("compute", payload)
    print(f"compute: {json.dumps(summary)}")
    return payload


# =========================================================================== #
# Stage: family (order-one augmentation), r = 2..6
# =========================================================================== #
def family_table(r: int) -> Table:
    base, _ = fixture_001_table()
    scores = list(base)
    weights = [(1 - F(1, r)) / 4] * 4
    for j in range(1, r + 1):
        scores.append((F(j, (r + 1) ** 2), F(j, (r + 1) ** 3)))
        weights.append(F(1, r * r))
    assert sum(weights) == 1
    return scores, weights


def stage_family() -> dict[str, object]:
    started = time.monotonic()
    base_scores, base_weights = fixture_001_table()
    base_exact = exact_dual_min_1d(base_scores, base_weights, 3)
    d0 = base_exact["value"]
    g0 = max(profiled_value(binned_information(base_scores, base_weights, z, 3))[0] for z in canonical_partitions(4, 3))
    reports = []
    for r in range(2, 7):
        scores, weights = family_table(r)
        n = len(scores)
        partitions = list(canonical_partitions(n, 3))
        phi = {}
        regular_all = True
        base_induced_regular = True
        max_diff = ZERO
        added_only_max = ZERO
        max_t = max(abs(x) for row in scores for x in row) * 3
        probes = [ZERO, ONE, F(-1), base_exact["beta"].a]
        for z in partitions:
            info = binned_information(scores, weights, z, 3)
            value, reg, _ = profiled_value(info)
            phi[z] = value
            regular_all &= reg
            # induced base labeling (drop added-only cells)
            base_labels = canonicalize(z[:4])
            kb = max(base_labels) + 1
            info_b = binned_information(base_scores, [w for w in weights[:4]], base_labels, kb)
            _, reg_b, _ = profiled_value(info_b)
            base_induced_regular &= reg_b
            for beta in probes:
                vz = tilted_form(info, [beta])
                vb = tilted_form(info_b, [beta])
                # cells with only added atoms
                added_cells = [b for b in range(3) if all(z[i] != b for i in range(4))]
                masses, sums = cell_sums(scores, weights, z, 3)
                added_contrib = sum(((sums[b][0] - beta * sums[b][1]) ** 2) / masses[b] for b in added_cells)
                added_only_max = max(added_only_max, added_contrib)
                max_diff = max(max_diff, abs(vz - vb - added_contrib))
        g_r = max(phi.values())
        exact = exact_dual_min_1d(scores, weights, 3)
        d_r = exact["value"]
        entry = {
            "r": r, "N": n, "partitions": len(partitions), "added_mass": F(1, r),
            "g_plus_r": g_r, "d_r": d_r, "gap_r": d_r - g_r,
            "beta_star_r": exact["beta"], "minimizer_kind": exact["kind"],
            "all_partitions_regular": regular_all, "base_induced_partitions_regular": base_induced_regular,
            "max_cell_perturbation_over_probes": max_diff, "r_times_max_perturbation": r * max_diff,
            "max_added_only_cell_contribution": added_only_max, "r_times_added_only": r * added_only_max,
            "abs_g_drift": abs(g_r - g0), "r_times_g_drift": r * abs(g_r - g0),
            "abs_d_drift": abs(d_r - d0), "r_times_d_drift": r * abs(d_r - d0),
            "gap_positive": (d_r - g_r) > 0,
        }
        if n <= 6:
            quads = {z: tilt_quadratic_1d(binned_information(scores, weights, z, 3)) for z in partitions}
            active = envelope_active_set(quads)
            entry["p_plus_r"] = max(phi[z] for z in active)
        reports.append(entry)
    summary = {
        "base_d": d0, "base_g_plus": g0, "base_gap": d0 - g0,
        "family_sizes": [r["r"] for r in reports],
        "gaps": [r["gap_r"] for r in reports],
        "all_gaps_positive": all(r["gap_positive"] for r in reports),
        "min_gap": min(r["gap_r"] for r in reports),
        "max_r_times_perturbation": max(r["r_times_max_perturbation"] for r in reports),
        "max_r_times_d_drift": max(r["r_times_d_drift"] for r in reports),
        "max_r_times_g_drift": max(r["r_times_g_drift"] for r in reports),
        "all_base_induced_regular": all(r["base_induced_partitions_regular"] for r in reports),
        "beta_stars": [r["beta_star_r"] for r in reports],
    }
    payload = {"provenance": provenance("family", started), "summary": summary, "family": reports}
    write_artifact("family", payload)
    print(f"family: gaps={[float(g) for g in summary['gaps']]} r*drift(d)<= {float(summary['max_r_times_d_drift']):.4f}")
    return payload


# =========================================================================== #
# Stage: ds18 (beta-zero interval DP on exact DS18-law samples)
# =========================================================================== #
GRID_BITS = 16


def ds18_sample(size: int, seed: int) -> list[Row]:
    """Exact rational iid draws of ``S = (X, 3X^2 - 1 + Z)``, X,Z uniform on a dyadic grid.

    ``X = -1 + (2k+1)/2^16`` with ``k`` uniform in ``[0, 2^16)`` (likewise ``Z``),
    so no draw is exactly 0, +-1/3 or +-1, and second moments are about the
    origin (nothing is centered).
    """
    rng = Lcg(seed)
    rows: list[Row] = []
    denom = 1 << GRID_BITS
    for _ in range(size):
        x = F(2 * rng.next_int(denom) + 1, 2 * denom) * 2 - 1
        z = F(2 * rng.next_int(denom) + 1, 2 * denom) * 2 - 1
        rows.append((x, 3 * x * x - 1 + z))
    return rows


def three_cell_scalar_optimum(xs: Sequence[Fraction]) -> tuple[Fraction, tuple[int, ...], tuple[int, int]]:
    """Exact equal-weight three-interval optimum of ``sum_b (sum_{i in b} x_i)^2 / n_b``.

    Rows are scaled to integers, sorted, and every cut pair is scored.  A float
    pass screens candidates with a relative margin of ``1e-9`` (float error on
    these sums is below ``1e-13``), and the survivors are compared exactly.
    Returns ``(value, labels, cut positions)`` with weights ``1/N`` applied.
    """
    n = len(xs)
    den = lcm_of([x.denominator for x in xs])
    order = sorted(range(n), key=lambda i: xs[i])
    ints = [int(xs[i] * den) for i in order]
    prefix = [0]
    for v in ints:
        prefix.append(prefix[-1] + v)
    total = prefix[-1]
    best_float = -1.0
    floats: list[tuple[float, int, int]] = []
    for c1 in range(1, n - 1):
        s1 = prefix[c1]
        f1 = (s1 * s1) / c1
        for c2 in range(c1 + 1, n):
            s2 = prefix[c2] - s1
            s3 = total - prefix[c2]
            val = f1 + (s2 * s2) / (c2 - c1) + (s3 * s3) / (n - c2)
            floats.append((val, c1, c2))
            if val > best_float:
                best_float = val
    margin = 1e-9 * max(abs(best_float), 1.0)
    survivors = [(c1, c2) for val, c1, c2 in floats if val >= best_float - margin]
    best = None
    best_cuts = (0, 0)
    for c1, c2 in survivors:
        s1 = prefix[c1]
        s2 = prefix[c2] - s1
        s3 = total - prefix[c2]
        val = F(s1 * s1, c1) + F(s2 * s2, c2 - c1) + F(s3 * s3, n - c2)
        if best is None or val > best:
            best, best_cuts = val, (c1, c2)
    assert best is not None
    labels = [0] * n
    for pos, idx in enumerate(order):
        labels[idx] = 0 if pos < best_cuts[0] else (1 if pos < best_cuts[1] else 2)
    value = best / (n * den * den)  # weights 1/N; undo the integer scaling
    return value, tuple(labels), best_cuts


def population_labels(xs: Sequence[Fraction]) -> tuple[int, ...]:
    """DS18's half-open reference labeling ``{X<-1/3}, {-1/3<=X<1/3}, {X>=1/3}``."""
    third = F(1, 3)
    return tuple(0 if x < -third else (1 if x < third else 2) for x in xs)


def ds18_case(size: int, rep: int) -> dict[str, object]:
    rows = ds18_sample(size, seed_for(size, rep))
    weights = [F(1, size)] * size
    xs = [r[0] for r in rows]
    v_hat, labels, cuts = three_cell_scalar_optimum(xs)
    if size <= 256:
        dp_value, dp_labels, _ = interval_dp(xs, weights, 3, sorted_order(xs))
        assert dp_value == v_hat, "specialised two-cut enumeration disagrees with the generic DP"
    info = binned_information(rows, weights, labels, 3)
    phi, regular, _ = profiled_value(info)
    delta = v_hat - phi
    identity = (info[1][1] > 0) and (delta == info[0][1] * info[0][1] / info[1][1])
    v_direct = between_value(xs, weights, labels, 3)
    xbar = sum(x for x in xs) / size
    # uncentered between = centered between + xbar^2 (labeling-independent shift)
    centered = between_value([x - xbar for x in xs], weights, labels, 3)
    order = sorted(range(size), key=lambda i: xs[i])
    cut_values = [(xs[order[c - 1]] + xs[order[c]]) / 2 for c in cuts]
    pop = population_labels(xs)
    # cells are intervals in both labelings; compare after the natural order alignment
    disagree = sum(1 for a, b in zip(labels, pop, strict=True) if a != b)
    inequality = []
    for eta in (F(1, 10), F(1, 20), F(1, 40)):
        band = sum(1 for x in xs if abs(x - F(1, 3)) <= eta or abs(x + F(1, 3)) <= eta)
        rhs = 3 * delta / eta + F(band, size)
        inequality.append({"eta": eta, "lhs_disagreement_fraction": F(disagree, size), "rhs": rhs, "holds": F(disagree, size) <= rhs})
    return {
        "N": size, "rep": rep, "seed": seed_for(size, rep),
        "v_hat_3": v_hat, "phi_hat": phi, "delta": delta, "regular": regular,
        "delta_identity_holds": identity,
        "dp_value_equals_between_of_labels": v_direct == v_hat,
        "uncentered_equals_centered_plus_xbar_sq": v_hat == centered + xbar * xbar,
        "cross_block": info[0][1], "nuisance_block": info[1][1], "poi_block": info[0][0],
        "nuisance_block_minus_32_81": info[1][1] - F(32, 81),
        "cuts": cut_values, "cut_float": [float(c) for c in cut_values],
        "cell_masses": [F(labels.count(b), size) for b in range(3)],
        "disagreement_rows": disagree, "disagreement_fraction": F(disagree, size),
        "disagreement_inequality": inequality,
        "all_inequalities_hold": all(e["holds"] for e in inequality),
    }


def ds18_midpoint_table(size: int) -> Table:
    xs = [F(2 * i + 1 - size, size) for i in range(size)]
    return [(x, 3 * x * x - 1) for x in xs], [F(1, size)] * size


def ds18_exhaustive_tax(table: Table, name: str) -> dict[str, object]:
    scores, weights = table
    n = len(scores)
    xs = [r[0] for r in scores]
    partitions = list(canonical_partitions(n, 3))
    violations = 0
    centered_violations = 0
    regular = 0
    best = None
    xbar = sum(w * x for w, x in zip(weights, xs, strict=True))
    for z in partitions:
        info = binned_information(scores, weights, z, 3)
        phi, reg, _ = profiled_value(info)
        v0 = between_value(xs, weights, z, 3)
        if reg:
            regular += 1
            if phi != v0 - info[0][1] ** 2 / info[1][1]:
                violations += 1
        else:
            if not (info[0][1] == 0 and phi == v0):
                violations += 1
        centered = between_value([x - xbar for x in xs], weights, z, 3)
        if v0 != centered + xbar * xbar:
            centered_violations += 1
        best = v0 if best is None else max(best, v0)
    dp_value, _, _ = interval_dp(xs, weights, 3, sorted_order(xs))
    return {"name": name, "N": n, "partitions": len(partitions), "regular": regular, "tax_identity_violations": violations, "centering_identity_violations": centered_violations, "brute_v3": best, "dp_v3": dp_value, "contiguity_agrees": best == dp_value}


def stage_ds18() -> dict[str, object]:
    started = time.monotonic()
    cases = []
    for size in (64, 256, 1024, 4096):
        for rep in (0, 1, 2):
            cases.append(ds18_case(size, rep))
    exhaustive = [ds18_exhaustive_tax(ds18_midpoint_table(n), f"midpoint_n{n}") for n in range(4, 11)]
    for n in (4, 6, 8):
        rows = ds18_sample(n, seed_for(n, 9))
        exhaustive.append(ds18_exhaustive_tax((rows, [F(1, n)] * n), f"seeded_n{n}"))
    summary = {
        "samples": len(cases),
        "all_regular": all(c["regular"] for c in cases),
        "delta_identity_failures": sum(not c["delta_identity_holds"] for c in cases),
        "centering_identity_failures": sum(not c["uncentered_equals_centered_plus_xbar_sq"] for c in cases),
        "inequality_failures": sum(not c["all_inequalities_hold"] for c in cases),
        "delta_by_N": {str(c["N"]): [] for c in cases},
        "exhaustive_tables": len(exhaustive),
        "exhaustive_partitions": sum(e["partitions"] for e in exhaustive),
        "exhaustive_tax_violations": sum(e["tax_identity_violations"] for e in exhaustive),
        "exhaustive_centering_violations": sum(e["centering_identity_violations"] for e in exhaustive),
        "exhaustive_contiguity_disagreements": sum(not e["contiguity_agrees"] for e in exhaustive),
    }
    for c in cases:
        summary["delta_by_N"][str(c["N"])].append(float(c["delta"]))  # type: ignore[index]
    summary["max_abs_cross_by_N"] = {str(n): max(abs(float(c["cross_block"])) for c in cases if c["N"] == n) for n in (64, 256, 1024, 4096)}
    summary["max_abs_nuisance_dev_by_N"] = {str(n): max(abs(float(c["nuisance_block_minus_32_81"])) for c in cases if c["N"] == n) for n in (64, 256, 1024, 4096)}
    summary["max_disagreement_fraction_by_N"] = {str(n): max(float(c["disagreement_fraction"]) for c in cases if c["N"] == n) for n in (64, 256, 1024, 4096)}
    payload = {"provenance": provenance("ds18", started), "summary": summary, "samples": cases, "exhaustive": exhaustive}
    write_artifact("ds18", payload)
    print(f"ds18: {json.dumps(summary)}")
    return payload


# =========================================================================== #
# Stage: tierb (matrix tilt, d_psi = 2)
# =========================================================================== #
def matrix_tilt_form(info: Sequence[Sequence[Fraction]], B: Sequence[Sequence[Fraction]], dp: int) -> list[list[Fraction]]:
    """``V_z(B) = I_pp - B I_lp - I_pl B^T + B I_ll B^T`` for a d_psi x d_lambda matrix B."""
    dl = len(info) - dp
    out = [[ZERO] * dp for _ in range(dp)]
    for r in range(dp):
        for c in range(dp):
            v = info[r][c]
            for k in range(dl):
                v -= B[r][k] * info[dp + k][c] + info[r][dp + k] * B[c][k]
            for k in range(dl):
                for m in range(dl):
                    v += B[r][k] * info[dp + k][dp + m] * B[c][m]
            out[r][c] = v
    return out


def det2(m: Sequence[Sequence[Fraction]]) -> Fraction:
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def generalized_schur_2(info: Sequence[Sequence[Fraction]], dp: int) -> list[list[Fraction]]:
    """``S^+ = I_pp - I_pl I_ll^+ I_lp`` via row-wise normal equations (DS11)."""
    dl = len(info) - dp
    lam = [[info[dp + r][dp + c] for c in range(dl)] for r in range(dl)]
    B = []
    for r in range(dp):
        rhs = [info[r][dp + c] for c in range(dl)]
        solved = solve_normal_equation(lam, rhs)
        assert solved is not None
        B.append(solved[0])
    return matrix_tilt_form(info, B, dp)


def stage_tierb() -> dict[str, object]:
    started = time.monotonic()
    rows: list[Row] = []
    for j in range(4):
        for sgn in (2, -2):
            row = [ZERO] * 4
            row[j] = F(sgn)
            rows.append(tuple(row))
    weights = [F(1, 8)] * 8
    partitions = list(canonical_partitions(8, 8))
    info = binned_information(rows, weights, partitions[0], 8)
    identity = all(info[r][c] == (1 if r == c else 0) for r in range(4) for c in range(4))
    centered = all(sum(w * r[k] for r, w in zip(rows, weights, strict=True)) == 0 for k in range(4))
    B0 = [[F(4), ZERO], [ZERO, ZERO]]
    B1 = [[ZERO, ZERO], [ZERO, F(4)]]
    Bm = [[(a + b) / 2 for a, b in zip(ra, rb, strict=True)] for ra, rb in zip(B0, B1, strict=True)]
    dets = {name: det2(matrix_tilt_form(info, B, 2)) for name, B in (("B0", B0), ("B1", B1), ("B_mid", Bm))}
    schur = generalized_schur_2(info, 2)
    # closed form check: V(B) = I_2 + B B^T
    closed_form_ok = True
    for B in (B0, B1, Bm, [[F(1), F(-2)], [F(3), F(1, 2)]]):
        V = matrix_tilt_form(info, B, 2)
        expected = [[(1 if r == c else 0) + sum(B[r][k] * B[c][k] for k in range(2)) for c in range(2)] for r in range(2)]
        closed_form_ok &= V == expected
    # weak matrix-tilt duality on a multi-partition d_psi = d_lambda = 2 table
    multi_rows: list[Row] = [(F(1), F(0), F(1), F(0)), (F(-1), F(1), F(0), F(1)), (F(0), F(-1), F(-1), F(1)), (F(2), F(1), F(1), F(-1)), (F(-2), F(-1), F(-1), F(-1)), (F(1), F(-1), F(0), F(0))]
    multi_w = [F(1, 6)] * 6
    probes_B = [[[ZERO, ZERO], [ZERO, ZERO]], [[F(1), ZERO], [ZERO, F(1)]], [[F(1, 2), F(-1)], [F(2), F(1, 3)]], [[F(-1), F(2)], [F(1), F(-1)]]]
    weak_violations = 0
    max_schur_det = None
    min_over_probes_of_max = None
    checked = 0
    for k in (3, 4, 5):
        for z in canonical_partitions(6, k):
            inf = binned_information(multi_rows, multi_w, z, k)
            S = generalized_schur_2(inf, 2)
            ds = det2(S)
            if max_schur_det is None or ds > max_schur_det:
                max_schur_det = ds
            for B in probes_B:
                dv = det2(matrix_tilt_form(inf, B, 2))
                checked += 1
                if ds > dv:
                    weak_violations += 1
    for B in probes_B:
        mx = None
        for k in (3, 4, 5):
            for z in canonical_partitions(6, k):
                dv = det2(matrix_tilt_form(binned_information(multi_rows, multi_w, z, k), B, 2))
                mx = dv if mx is None else max(mx, dv)
        assert mx is not None
        min_over_probes_of_max = mx if min_over_probes_of_max is None else min(min_over_probes_of_max, mx)
    # smaller-support search for a midpoint violation of the outer map
    search = {"tables": 0, "found": []}
    diag_grid = [F(v) for v in (-4, -2, -1, 0, 1, 2, 4)]
    for n in (4, 5, 6):
        for rep in range(12):
            rng = Lcg(seed_for(n, rep) + 31)
            tab = [tuple(F(rng.next_int(7) - 3) for _ in range(4)) for _ in range(n)]
            w = [F(1, n)] * n
            for k in (n, n - 1):
                if k < 2:
                    continue
                search["tables"] += 1  # type: ignore[operator]
                parts = list(canonical_partitions(n, k))
                infos = [binned_information(tab, w, z, k) for z in parts]

                def f(B: list[list[Fraction]]) -> Fraction:
                    return max(det2(matrix_tilt_form(inf, B, 2)) for inf in infos)

                hit = None
                for a, b in product(diag_grid, repeat=2):
                    Ba = [[a, ZERO], [ZERO, ZERO]]
                    Bb = [[ZERO, ZERO], [ZERO, b]]
                    Bmid = [[a / 2, ZERO], [ZERO, b / 2]]
                    fa, fb, fm = f(Ba), f(Bb), f(Bmid)
                    if fm > max(fa, fb):
                        hit = {"N": n, "K": k, "a": a, "b": b, "f_B0": fa, "f_B1": fb, "f_mid": fm, "scores": tab}
                        break
                if hit is not None:
                    search["found"].append(hit)  # type: ignore[union-attr]
                    break
            if search["found"]:
                break
        if search["found"]:
            break
    result = {
        "provenance": provenance("tierb", started),
        "fixture": "CE-DS-MATRIX-TILT-NONQUASICONVEX-001",
        "rows": rows, "weights": weights, "K": 8,
        "canonical_partitions_K8": len(partitions),
        "rows_centered": centered,
        "binned_information_is_identity": identity,
        "generalized_schur": schur,
        "log_det_schur": "log det I_2 = 0",
        "closed_form_V_equals_I_plus_BBt": closed_form_ok,
        "determinants": dets,
        "midpoint_violation": dets["B_mid"] > max(dets["B0"], dets["B1"]),
        "weak_duality_at_probes": all(det2(matrix_tilt_form(info, B, 2)) >= det2(schur) for B in (B0, B1, Bm)),
        "multi_partition_table": {"rows": multi_rows, "weights": multi_w, "K": [3, 4, 5], "checks": checked, "weak_duality_violations": weak_violations, "max_schur_det": max_schur_det, "min_over_probe_B_of_max_det_V": min_over_probes_of_max, "weak_duality_holds": max_schur_det <= min_over_probes_of_max},
        "smaller_support_search": search,
    }
    write_artifact("tierb", result)
    print(f"tierb: dets={ {k: str(v) for k, v in dets.items()} } violation={result['midpoint_violation']} weak_ok={result['multi_partition_table']['weak_duality_holds']} smaller={[ (h['N'], h['K']) for h in search['found']]}")
    return result


# =========================================================================== #
# Stage: invariances (protocol G)
# =========================================================================== #
def stage_invariances() -> dict[str, object]:
    started = time.monotonic()
    scores, weights = fixture_001_table()
    bins = 3
    partitions = list(canonical_partitions(4, bins))
    phi = {z: profiled_value(binned_information(scores, weights, z, bins))[0] for z in partitions}
    d = exact_dual_min_1d(scores, weights, bins)
    out: dict[str, object] = {"provenance": provenance("invariances", started)}
    # 1. nuisance reparameterisation lambda -> a lambda
    a = F(-3, 2)
    re_scores = [(r[0], a * r[1]) for r in scores]
    phi_re = {z: profiled_value(binned_information(re_scores, weights, z, bins))[0] for z in partitions}
    d_re = exact_dual_min_1d(re_scores, weights, bins)
    out["reparameterisation"] = {"a": a, "phi_invariant": phi == phi_re, "d_invariant": d["value"] == d_re["value"], "beta_maps_as_beta_over_a": d_re["beta"] * a == d["beta"]}
    # 1b. d_lambda = 2 linear reparameterisation lambda -> A lambda
    name, (sc2, w2), _ = adversarial_tables_2d()[0]
    A = [[F(1), F(2)], [F(0), F(1)]]
    sc2_re = [(r[0], A[0][0] * r[1] + A[0][1] * r[2], A[1][0] * r[1] + A[1][1] * r[2]) for r in sc2]
    ok = True
    for beta in probe_tilts_2d():
        beta_A = [beta[0] * A[0][0] + beta[1] * A[1][0], beta[0] * A[0][1] + beta[1] * A[1][1]]
        v_re, _ = dp_value_any_dim(sc2_re, w2, 3, beta)
        v, _ = dp_value_any_dim(sc2, w2, 3, beta_A)
        ok &= v == v_re
    phi2 = [profiled_value(binned_information(sc2, w2, z, 3))[0] for z in canonical_partitions(5, 3)]
    phi2_re = [profiled_value(binned_information(sc2_re, w2, z, 3))[0] for z in canonical_partitions(5, 3)]
    out["reparameterisation_2d"] = {"A": A, "v_K_transforms_as_beta_A": ok, "phi_invariant": phi2 == phi2_re}
    # 2. row permutation
    perm = [2, 0, 3, 1]
    p_scores = [scores[i] for i in perm]
    p_weights = [weights[i] for i in perm]
    g_p = max(profiled_value(binned_information(p_scores, p_weights, z, bins))[0] for z in partitions)
    d_p = exact_dual_min_1d(p_scores, p_weights, bins)
    out["row_permutation"] = {"g_plus_invariant": g_p == max(phi.values()), "d_invariant": d_p["value"] == d["value"]}
    # 3. bin relabeling
    z = (0, 1, 2, 2)
    relabeled = (2, 0, 1, 1)
    out["bin_relabeling"] = {"phi_invariant": profiled_value(binned_information(scores, weights, z, bins))[0] == profiled_value(binned_information(scores, weights, relabeled, bins))[0]}
    # 4. uniform weight scaling
    c = F(3, 7)
    s_weights = [c * w for w in weights]
    phi_s = {z: profiled_value(binned_information(scores, s_weights, z, bins))[0] for z in partitions}
    d_s = exact_dual_min_1d(scores, s_weights, bins)
    out["weight_scaling"] = {"c": c, "phi_scales": all(phi_s[z] == c * phi[z] for z in partitions), "d_scales": d_s["value"] == c * d["value"], "closure_invariant": (max(phi_s.values()) == d_s["value"]) == (max(phi.values()) == d["value"])}
    # 5. split-weight duplication (row level) versus collapsed atoms
    dup_scores = [r for r in scores for _ in range(2)]
    dup_weights = [w / 2 for w in weights for _ in range(2)]
    pooled: dict[Row, Fraction] = {}
    for r, w in zip(dup_scores, dup_weights, strict=True):
        pooled[r] = pooled.get(r, ZERO) + w
    collapsed_equal = sorted(pooled.items()) == sorted(zip(scores, weights, strict=True))
    same_v = True
    for beta in probe_tilts_1d():
        v_row, _ = brute_dual_value(dup_scores, dup_weights, bins, [beta])
        v_atom, _ = brute_dual_value(scores, weights, bins, [beta])
        same_v &= v_row == v_atom
    g_row = max(profiled_value(binned_information(dup_scores, dup_weights, z, bins))[0] for z in canonical_partitions(8, bins))
    g_atom = max(phi.values())
    # K exceeding the atom count: row level feasible, atom level not
    g_row_k5 = max(profiled_value(binned_information(dup_scores, dup_weights, z, 5))[0] for z in canonical_partitions(8, 5))
    atom_k5 = list(canonical_partitions(4, 5))
    out["split_weight_duplication"] = {"collapsed_table_equals_original": collapsed_equal, "v_K_row_level_equals_atom_level_at_probes": same_v, "g_plus_row_level": g_row, "g_plus_atom_level": g_atom, "g_plus_equal": g_row == g_atom, "K5_row_level_g_plus": g_row_k5, "K5_atom_level_feasible": bool(atom_k5)}
    # duplicate-table domain difference on the adversarial duplicate table
    name_d, (dsc, dw), _ = adversarial_tables()[2]
    pooled2: dict[Row, Fraction] = {}
    for r, w in zip(dsc, dw, strict=True):
        pooled2[r] = pooled2.get(r, ZERO) + w
    atoms = sorted(pooled2)
    atom_w = [pooled2[a] for a in atoms]
    dom = {}
    for k in (2, 3):
        g_rows = max(profiled_value(binned_information(dsc, dw, z, k))[0] for z in canonical_partitions(len(dsc), k))
        g_atoms = max(profiled_value(binned_information(atoms, atom_w, z, k))[0] for z in canonical_partitions(len(atoms), k))
        d_rows = exact_dual_min_1d(dsc, dw, k)["value"]
        d_atoms = exact_dual_min_1d(atoms, atom_w, k)["value"]
        dom[str(k)] = {"g_plus_rows": g_rows, "g_plus_atoms": g_atoms, "rows_exceed_atoms": g_rows > g_atoms, "d_rows": d_rows, "d_atoms": d_atoms, "d_rows_ge_d_atoms": d_rows >= d_atoms}
    out["duplicate_domains"] = {"table": name_d, "atoms": len(atoms), "rows": len(dsc), "by_K": dom}
    # 6. exact-K versus at-most-K
    vk = {k: brute_dual_value(scores, weights, k, [ZERO])[0] for k in (2, 3, 4)}
    gk = {k: max(profiled_value(binned_information(scores, weights, z, k))[0] for z in canonical_partitions(4, k)) for k in (2, 3, 4)}
    out["cardinality_monotone"] = {"v_K_at_0": vk, "g_plus_K": gk, "v_monotone": vk[2] <= vk[3] <= vk[4], "g_monotone": gk[2] <= gk[3] <= gk[4]}
    # 7. zero-weight row: own cell undefined; shared cell inert
    zero_scores = list(scores) + [(F(7), F(-7))]
    zero_weights = list(weights) + [ZERO]
    try:
        binned_information(zero_scores, zero_weights, (0, 1, 2, 2, 3), 4)
        own_cell = "defined"
    except ValueError:
        own_cell = "undefined (0/0 cell mass)"
    inert = profiled_value(binned_information(zero_scores, zero_weights, (0, 1, 2, 2, 0), 3))[0] == phi[(0, 1, 2, 2)]
    out["zero_weight_row"] = {"own_cell": own_cell, "shared_cell_inert": inert}
    # 8. K = N closes (single labeling), K = N-1 need not
    kn = exact_dual_min_1d(scores, weights, 4)
    out["K_equals_N"] = {"d": kn["value"], "g_plus": profiled_value(binned_information(scores, weights, (0, 1, 2, 3), 4))[0], "closes": kn["value"] == profiled_value(binned_information(scores, weights, (0, 1, 2, 3), 4))[0]}
    write_artifact("invariances", out)
    flat = {k: v for k, v in out.items() if k != "provenance"}
    print(f"invariances: {json.dumps({k: (v if not isinstance(v, dict) else {kk: str(vv) for kk, vv in v.items()}) for k, v in flat.items()}, default=str)[:1500]}")
    return out


# =========================================================================== #
# Stage: fixtures (serialise the two new exact boundary cases)
# =========================================================================== #
def stage_fixtures() -> dict[str, object]:
    started = time.monotonic()
    witness = search_n3_k2_witness()
    minimal = witness["minimal"]
    assert minimal is not None
    scores = minimal["scores"]
    weights = minimal["weights"]
    cert = minimal["rational_certificate"]
    assert cert is not None
    phi = minimal["phi_plus"]
    optimum = max(phi, key=lambda k: phi[k])
    first = str(cert["labels_first"]) if phi[str(cert["labels_first"])] != minimal["g_plus"] else str(cert["labels_second"])
    fixture_gap = {
        "id": "CE-DS-TILT-DUAL-GAP-002",
        "criterion": "Ds",
        "level": "finite_assignment",
        "claim_falsified": (
            "The scalar-POI tilt-dual duality gap needs N>=4 (support minimality of "
            "CE-DS-TILT-DUAL-GAP-001 across all K). FALSE: at N=3, K=2 the exact dual "
            "minimum strictly exceeds the exact global profiled value, and N=3 is the "
            "smallest support at which any exact-K>=2 problem has more than one labeling."
        ),
        "scores": scores,
        "weights": weights,
        "K": 2,
        "labels_before": json.loads(first),
        "labels_after_or_optimum": json.loads(optimum),
        "poi_indices": [0],
        "nuisance_indices": [1],
        "objective_before": phi[first],
        "objective_after": phi[optimum],
        "comparison_domain": (
            "All three label-permutation-canonical nonempty K=2 row assignments; every "
            "nuisance block is nonsingular, so DS9 in-bin and DS11 pseudo-inverse domains coincide."
        ),
        "exact_quantities": {
            "canonical_partitions": 3,
            "regular_partitions": sum(minimal["regular"].values()),
            "phi_plus_by_labeling": phi,
            "tilt_quadratics_ABC_by_labeling": minimal["quadratics_ABC"],
            "global_profiled_value": minimal["g_plus"],
            "exact_dual_minimizer_beta": minimal["exact_dual_minimizer"],
            "exact_dual_minimum": minimal["exact_dual_minimum"],
            "exact_duality_gap": minimal["exact_gap"],
            "active_labelings_at_minimizer": minimal["active_at_minimizer"],
            "rational_certificate_alpha_on_first": cert["alpha_on_first"],
            "rational_certificate_first_labels": cert["labels_first"],
            "rational_certificate_second_labels": cert["labels_second"],
            "mixture_quadratic_ABC": cert["mixture_quadratic_ABC"],
            "mixture_vertex_beta": cert["mixture_vertex"],
            "mixture_global_minimum": cert["mixture_minimum"],
            "certified_duality_gap_lower_bound": cert["certified_gap_lower_bound"],
            "support_minimality": (
                "N=2 or K=N admits one labeling and closes; N=3, K=2 is the smallest exact-K "
                "problem with more than one labeling, so this witness is support-minimal over all K."
            ),
        },
        "search": {"grid": witness["grid"], "tables": witness["tables"], "tables_with_gap": witness["tables_with_gap"]},
        "verification": {
            "method": "exhaustive",
            "notes": (
                "All arithmetic is fractions.Fraction. The dual minimum is exact (a rational tilt "
                "certified by the one-sided subgradient condition D-(beta*) <= 0 <= D+(beta*)); the "
                "rational convex-mixture certificate independently lower-bounds it."
            ),
        },
        "source": "AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER independent falsification search",
        "date": "2026-09-02",
    }
    tm = tie_mask_search()
    ex = tm["smallest_regular_miss"] or tm["smallest_deterministic_miss"] or tm["smallest"]
    assert ex is not None
    t_scores, t_weights, k = ex["scores"], ex["weights"], ex["K"]
    t_parts = list(canonical_partitions(len(t_scores), k))
    t_phi = {z: profiled_value(binned_information(t_scores, t_weights, z, k)) for z in t_parts}
    beta_star = ex["beta_star"]
    assert beta_star.is_rational()
    bstar = beta_star.a
    t_quads = {z: tilt_quadratic_1d(binned_information(t_scores, t_weights, z, k)) for z in t_parts}
    closing = [z for z in t_parts if t_phi[z][0] == ex["g_plus"]]
    tilted = [r[0] - bstar * r[1] for r in t_scores]
    fixture_tie = {
        "id": "CE-DS-TILT-DUAL-TIE-MASK-001",
        "criterion": "Ds",
        "level": "finite_assignment",
        "claim_falsified": (
            "A deterministic tilt-DP implementation that reports an open bracket "
            "[Phi^+(z_DP), d] has exhibited a duality gap. FALSE: the bracket closes exactly "
            "(g^+ = d) but the DP-optimal set at the dual minimizer contains a non-closing "
            "labeling, which a deterministic tie policy can return."
        ),
        "scores": t_scores,
        "weights": t_weights,
        "K": k,
        "labels_before": list(ex["non_closing_active_at_beta_star"][0]),
        "labels_after_or_optimum": list(closing[0]),
        "poi_indices": [0],
        "nuisance_indices": [1],
        "objective_before": t_phi[tuple(ex["non_closing_active_at_beta_star"][0])][0],
        "objective_after": ex["g_plus"],
        "comparison_domain": "All canonical nonempty labelings; regularity of each is recorded below.",
        "exact_quantities": {
            "canonical_partitions": len(t_parts),
            "phi_plus_by_labeling": {str(list(z)): v[0] for z, v in t_phi.items()},
            "regular_by_labeling": {str(list(z)): v[1] for z, v in t_phi.items()},
            "tilt_quadratics_ABC_by_labeling": {str(list(z)): q for z, q in t_quads.items()},
            "global_generalized_value": ex["g_plus"],
            "exact_dual_minimizer_beta": bstar,
            "exact_dual_minimum": ex["d"],
            "bracket_closes": ex["closed"],
            "tilted_values_at_minimizer": tilted,
            "tilted_values_distinct": len(set(tilted)) == len(tilted),
            "dp_optimal_labelings_at_minimizer": ex["active_at_beta_star"],
            "closing_labelings": [list(z) for z in closing],
            "non_closing_dp_optimal_labelings": ex["non_closing_active_at_beta_star"],
            "derivative_of_each_active_quadratic_at_minimizer": {str(list(z)): 2 * t_quads[z][0] * bstar + t_quads[z][1] for z in map(tuple, ex["active_at_beta_star"])},
            "right_perturbation_dp_returns": ex["deterministic_dp_right_labeling"],
            "left_perturbation_dp_returns": ex["deterministic_dp_left_labeling"],
            "right_perturbation_dp_closes": ex["deterministic_dp_right_closes"],
            "left_perturbation_dp_closes": ex["deterministic_dp_left_closes"],
            "reported_open_interval_if_wrong_member": [t_phi[tuple(ex["non_closing_active_at_beta_star"][0])][0], ex["d"]],
        },
        "search": {"grids": tm["grids"], "tables": tm["tables_searched"], "found": tm["found"], "found_where_a_perturbation_order_misses": tm["found_where_deterministic_dp_reports_open"], "found_with_regular_closing_labeling": tm["found_with_regular_closing_labeling"], "singular_only_sibling": {"scores": tm["smallest_singular_miss"]["scores"], "g_plus": tm["smallest_singular_miss"]["g_plus"], "d": tm["smallest_singular_miss"]["d"], "beta_star": tm["smallest_singular_miss"]["beta_star"]} if tm["smallest_singular_miss"] else None},
        "verification": {
            "method": "exhaustive",
            "notes": (
                "The tilted values at beta* are pairwise distinct, so this is a DP value tie, not a "
                "tilted-value tie: two contiguous labelings attain v_K(beta*) with different "
                "derivatives, and only the zero-derivative one satisfies the normal equation."
            ),
        },
        "source": "AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER independent falsification search",
        "date": "2026-09-02",
    }
    FIXTURES.mkdir(exist_ok=True)
    for fx in (fixture_gap, fixture_tie):
        (FIXTURES / f"{fx['id']}.json").write_text(json.dumps(fx, indent=2, default=_json_default) + "\n", encoding="utf-8")
    payload = {"provenance": provenance("fixtures", started), "written": [fixture_gap["id"], fixture_tie["id"]], "gap_fixture": fixture_gap, "tie_mask_fixture": fixture_tie}
    write_artifact("fixtures", payload)
    print(f"fixtures: wrote {payload['written']}")
    return payload


# =========================================================================== #
# Entry point
# =========================================================================== #
STAGES: dict[str, Callable[[], dict[str, object]]] = {
    "witness": stage_witness,
    "ceiling": stage_ceiling,
    "saddle": stage_saddle,
    "ties": stage_ties,
    "compute": stage_compute,
    "family": stage_family,
    "ds18": stage_ds18,
    "tierb": stage_tierb,
    "invariances": stage_invariances,
    "fixtures": stage_fixtures,
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stage", choices=[*STAGES, "all"])
    args = parser.parse_args(argv)
    names = list(STAGES) if args.stage == "all" else [args.stage]
    for name in names:
        started = time.monotonic()
        STAGES[name]()
        print(f"  [{name} done in {time.monotonic() - started:.1f}s]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
