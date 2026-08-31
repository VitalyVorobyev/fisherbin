# AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER — independent DS18 audit

**Programme:** P1 · **Opened:** 31 August 2026 · **Status:** active

## Audit object

Independently audit `DS-NONCENTERED-GLOBAL-BASIN-TRANSFER` and DS18 in
`KNOWN_RESULTS/05b-ds-bridge.md`. Treat the registered proof as a target to
attack, not as derivation context. Do not reuse
`py/ds_noncentered_global_basin.py` or its helper code in the audit oracle.

## Required attacks

1. Recompute from the law definition, preferably through a second symbolic
   route, the full and binned information matrices, the gate root, the
   off-(L) condition, efficiency, masses, separation, and the stated fixed
   margins. Check the (M4) boundary-tube bound on the actual two-dimensional
   score law.
2. Audit the scalar uniform three-bin theorem, including globality,
   uniqueness up to labels, every equality condition, and the upgrade from a
   unique maximizer to strict isolation in the chosen population topology.
3. Audit both inequalities in the profiled variational sandwich and prove
   that equality forces the stated rule; pay special attention to singular
   nuisance blocks and normal-equation solution sets.
4. Audit the empirical squeeze with its exact quantifiers: **every** sequence
   of finite global regular \(D_s\) optimizers, almost surely, up to labels.
   Verify the use and hypotheses of DS15 grouping rigidity, label and moment
   convergence, and that no sample-centering is hidden anywhere.
5. Check that finite global optimality really implies the claimed ordinary
   one-point exchange stability under the project's feasibility convention.
   Enumerate moves whose source or destination becomes singular and state
   exactly which moves belong to the ordinary comparison domain.
6. Reproduce the minimized \(N=4\) raw-population-cut counterexample with an
   independent exact implementation. Search smaller supports and adversarial
   unequal-weight, duplicate, singleton, tie, and singular cases.
7. Run a fresh prior-art search for the combined claim: profiled Fisher/
   Schur-complement quantization, equal-interval scalar uniform quantization,
   empirical optimal-quantizer consistency, and finite exact exchange
   stability. Record direct antecedents and search gaps separately.

## Required outputs

- A publication-grade audit report under `AUDITS/` with an independent
  artifact under `AUDITS/artifacts/`.
- Claim patches for every hardened, narrowed, or rejected statement.
- Independent regression tests for the exact law and boundary fixture.
- A clear deployment verdict. No `src/` or public API change belongs in this
  audit.

## Stop condition

Stop only after the exact population theorem, equality/strict-isolation
chain, empirical quantifiers, ordinary-exchange feasibility boundary, and
serialized counterexample have each received an independent adversarial
verdict.
