# OPEN-DS-MARGINS-NONCENTERED — off-class stable basins and empirical transfer

**Programme:** P1 · **Opened:** 31 August 2026 · **Completed:** 31 August 2026 · **Status:** completed

## Goal

For an explicitly stated class of scalar-interest, scalar-nuisance score laws
outside conditional-centering class (L), determine whether the necessary
population system

\[
q=h(T_\beta),\qquad
T_\beta=S_\psi-\beta S_\lambda,\qquad
E[h(T_\beta)S_\lambda]=0
\]

has a nondegenerate Lloyd-stationary solution with fixed positive mass,
information, and projected-separation margins. If it does, prove or refute
that an isolated strict population basin transfers almost surely to exact
one-point exchange-stable empirical labelings despite
\(O(1/N)\)-scale boundary noise. “Done” means a theorem for a named law class,
an exact counterexample, or a reduction to individually listed regularity and
selection assumptions; another finite scan is not enough.

## Why it matters

DS17 makes the DS14 companion compile path asymptotically empty on class (L).
This packet asks whether the path genuinely survives off that class and, if
so, whether it can support a theorem-backed compiler rather than a measured
diagnostic.

## Relevant claims

- `OPEN-DS-MARGINS-NONCENTERED`
- `DS-STABLE-BASINS-FIXED-POINT-GATE`
- `DS-STABLE-BASINS-GATE-SCANS`
- `DS-STABLE-BASINS-CENTERED-OBSTRUCTION`
- `DS-STABLE-BASINS-LCM-CLASSIFICATION`
- `DS-PROFILED-COMPILE-CERTIFICATE`
- `OPEN-DS-FINITE-POP-BRIDGE`

## Known blockers

- The DS17.4 equation is necessary, not sufficient: a root must also be a
  genuine Lloyd fixed point and satisfy the declared margins.
- Root consistency remains meaningful when
  \(I_{\lambda\lambda}(q)=0\); regular tilt consistency
  \(B_q^*=\beta\) does not. Singular roots must be separated rather than
  counted as usable basins.
- The compact search range depends on the law and declared margin:
  \(|\beta|\le 2M/\kappa\). A convenient fixed window cannot certify absence.
- A multistart scan cannot establish branch completeness, root uniqueness, or
  global optimality. The mix3 root is evidence only.
- Population stationarity does not by itself imply empirical exact exchange
  stability. Boundary events have the same \(O(1/N)\) scale as one-point
  move gains and require a uniform transfer argument.
- Conditional centering is a population property. Sample-centering scores is
  forbidden and cannot be used to manufacture or remove class (L).
- `DS-STABLE-STATE-SELECTION` remains measured and cannot carry theorem
  authority. The foundational `DS-SCHUR`, `FI-QUANT-IDENTITY`, and
  `FI-RANK-CEILING` edges require separate audits.

## Recommended starting points

- Start from the hardened proof and gate derivation in
  `KNOWN_RESULTS/05b-ds-bridge.md` DS17 and
  `AUDITS/AUDIT-DS-STABLE-BASINS-001.md`.
- Use `py/audit_ds_stable_basins.py search` only as a reproducible
  falsification instrument. Its mix3 root at \(\beta=0\), cuts
  \(\pm1.0047634\), and \(\lambda_{\min}\approx1.7363948\) is a candidate,
  not a premise.
- Seek an analytic off-(L) family with differentiable strip moments and an
  isolated negative-definite Lloyd/root Jacobian. Prove local root
  persistence before studying empirical labels.
- For empirical transfer, isolate boundary tubes, obtain uniform laws for
  move gains and cell moments on a compact basin, and prove a strict buffer
  exceeding the stochastic and one-point scales.
- Keep \(v^*(\kappa)\), \(v^{*+}(\kappa)\), population stationary rules,
  and empirical stable labelings as four distinct objects.

## Required deliverables

- Verdict-driven patches to `OPEN-DS-MARGINS-NONCENTERED` and every proved
  claim actually established.
- A theorem or counterexample with explicit hypotheses, quantifiers, and the
  DS17.4 root equation as its population necessity test.
- Independent exact or interval-certified artifacts for any claimed root
  existence/absence, plus deterministic empirical-transfer tests if a basin
  theorem is claimed.
- New `NUMERICAL_EVIDENCE.md` rows only for reproducible measurements; no
  scan may be promoted to theorem authority.
- A separate publication-grade audit packet before any new compile path is
  copied into `src/`.

## Outcome

The packet stop condition is **PROVED for an explicit off-(L) law**. Let

\[
X,Z\stackrel{\mathrm{iid}}{\sim}\operatorname{Unif}[-1,1],\qquad
S_\psi=X,\qquad S_\lambda=3X^2-1+Z,
\]

and use \(K=3\). The equal-third rule with cuts \(\pm1/3\) is, up to labels,
the unique population global \(D_s\) optimizer. Its exact data are

\[
I_{\rm full}=\operatorname{diag}(1/3,17/15),\qquad
I_q=\operatorname{diag}(8/27,32/81),\qquad
\beta=0,qquad \eta_{D_s}=8/9.
\]

The cell masses are \(1/3\), the minimum projected-centroid separation is
\(2/3\), and the eventual margins \(c_0=1/4\), \(\kappa=1/4\), and
\(\gamma=1/2\) are valid. The law lies off (L) because
\(E[S_\lambda\mid X]=3X^2-1\) is not zero.

The proof first sandwiches every profiled rule by the scalar between-cell
variance of \(X\), then proves that the uniform scalar three-cell optimum is
uniquely the three equal intervals. The stated rule attains equality in the
sandwich and is therefore a strictly isolated global optimum. Empirically,
the fixed population rule supplies a lower bound and the empirical scalar
three-bin optimum supplies the upper bound. DS15 grouping rigidity then
forces, almost surely, every sequence of finite global regular \(D_s\)
optimizers to converge in labels and moments, up to relabeling. Finite global
optimality itself gives exact ordinary one-point exchange stability. No score
is sample-centered.

This does **not** prove that raw population-cut labels are stable at finite
\(N\), or that generic local exchange ascent selects the basin. The exact
support-minimal \(N=4\) fixture
`CE-DS-NONCENTERED-POPULATION-CUT-UNSTABLE-001` has a strict improving move
of size \(37/14608\) from the raw population-cut labeling.

## Falsification and provenance

- `py/ds_noncentered_global_basin.py` uses pure-stdlib `Fraction` arithmetic.
  It verifies the exact population moments and the minimized boundary
  counterexample, then enumerates 13,744 canonical midpoint partitions,
  10,386 product-grid partitions, and 428 adversarial partitions through
  \(N=10\), including unequal weights, duplicates, singletons, ties, and
  singular nuisance blocks. It found no sandwich or claimed-global-bound
  violation.
- `WORK/artifacts/OPEN-DS-MARGINS-NONCENTERED/exact-falsification.json`
  records the run and exact fractions.
- `tests/test_research_claims.py` pins both the theorem arithmetic and the
  counterexample.
- `LITERATURE/audits/OPEN-DS-MARGINS-NONCENTERED-31-August-2026.md`
  triangulates the five nearest classical sources. The combined profiled
  information/global-isolation/empirical-transfer statement remains a
  `search_gap`, not a novelty claim.

## Deployment boundary

`DS-NONCENTERED-GLOBAL-BASIN-TRANSFER` is a population and empirical
existence theorem. It authorizes no `src/` or public API change. The fresh
independent audit ran on 31 August 2026 and closed as **verified with hardened
assumptions**
(`WORK/completed/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER.md`,
`AUDITS/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001.md`); the verdict
deliberately leaves the deployment boundary where it was, so no compile surface
may consume DS18.

## Stop conditions

Satisfied by `DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`: **PROVED for an explicit
off-(L) law**, with an exact nondegenerate gate root and almost-sure exact
exchange-stable empirical labelings supplied by finite global regular
optimizers. Practical basin selection is outside this result.

## Next dependency-blocking question

Can a practical profiled solver be proved to select this full-rank basin
without global combinatorial optimization, while retaining computable
margins and value guarantees under perturbations of the law?
