# OPEN-DS-MARGINS-NONCENTERED — off-class stable basins and empirical transfer

**Programme:** P1 · **Opened:** 31 August 2026 · **Status:** active

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
- `DS-EXCHANGE-IMPLIES-COMPANION`

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

## Stop conditions

Stop when the off-(L) root-and-transfer statement is proved, disproved with a
minimized serialized counterexample, or reduced to explicitly named
regularity, isolation, and empirical-selection assumptions. Split off a new
packet if root existence is settled but empirical transfer remains
independent.

## Next dependency-blocking question

Does `OPEN-DS-MARGINS-NONCENTERED` admit a nondegenerate isolated solution of
the `DS-STABLE-BASINS-FIXED-POINT-GATE` system on a stated off-(L) law class,
and does that basin transfer to exact empirical one-point exchange stability
against \(O(1/N)\)-scale boundary noise?
