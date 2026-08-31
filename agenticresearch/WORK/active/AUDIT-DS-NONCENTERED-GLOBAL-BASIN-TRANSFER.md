# AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER — independent DS18 audit

**Programme:** P1 · **Opened:** 31 August 2026 · **Status:** active
**Source frozen:** `research-open-ds-margins-noncentered` at `b1855c1`

## Goal

Independently verify, harden, refute, or reduce
`DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`, the DS18 theorem complex, and the
DS18-dependent clauses added to `OPEN-DS-MARGINS-NONCENTERED`,
`DS-PROFILED-COMPILE-CERTIFICATE`, and
`OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`.

DS18 is the first exact positive off-(L) population-to-empirical transfer
theorem in the project. It is promising and potentially load-bearing, but it
is currently `publication_status: internal`, explicitly unaudited, and
authorizes no `src/` change. Therefore `protocols/audit.md` applies in full.
The primary deliverable is the 16-item publication-grade report
`AUDITS/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001.md`.

## Independence contract

- Use a brand-new agent session with no research-session transcript or
  inherited derivation context. The frozen repository state and this packet
  are the complete handoff.
- Do not import, extend, or translate
  `py/ds_noncentered_global_basin.py`. Build the audit oracle independently
  as `py/audit_ds_noncentered_global_basin_transfer.py`; use pure-stdlib
  `fractions.Fraction` for exact claims and a genuinely separate symbolic or
  interval/numerical route for continuous-law checks.
- Recheck every dependency returned by `registry.py show`; do not re-prove a
  previously audited `project_proved` dependency unless an explicit defect is
  found. Record a separate audit task for an inherited defect rather than
  silently repairing it inside DS18.
- Treat the existing exact artifact, literature triangulation, proof's
  self-adversarial notes, and test expectations as claims to attack, not audit
  evidence.
- Do not edit `src/`, public APIs, examples, or deployment code.

## Audit object and exact target

Independently audit `DS-NONCENTERED-GLOBAL-BASIN-TRANSFER` and DS18 in
`KNOWN_RESULTS/05b-ds-bridge.md`. Treat the registered proof as a target to
attack, not as derivation context. Do not reuse
`py/ds_noncentered_global_basin.py` or its helper code in the audit oracle.

The frozen target is the following compound claim. For

\[
X,Z\stackrel{\mathrm{iid}}{\sim}\operatorname{Unif}[-1,1],\qquad
S_\psi=X,\qquad S_\lambda=3X^2-1+Z,\qquad K=3,
\]

the cuts \(\pm1/3\) form the unique strict population global profiled
\(D_s\) optimum up to labels, with

\[
I_{\rm full}=\operatorname{diag}(1/3,17/15),\qquad
I_q=\operatorname{diag}(8/27,32/81),\qquad
\beta=0,\qquad \eta_{D_s}=8/9.
\]

For equal-weight i.i.d. samples with exact, uncentered scores, every sequence
of finite global regular profiled optimizers converges in labels and moments
to that rule and is eventually exactly ordinary one-point exchange-stable
with \((c_0,\kappa,\gamma)=(1/4,1/4,1/2)\). The theorem does not claim finite
stability of the raw population-cut labels or basin selection by local
exchange ascent.

## Required attacks

1. **Claim graph and objective convention.** Start from
   `registry.py show DS-NONCENTERED-GLOBAL-BASIN-TRANSFER --deps --proof`.
   Recheck the statuses, hypotheses, and exact statements of every dependency
   and every converse/boundary edge. Confirm that DS18 consistently uses the
   Schur-complement value versus its logarithm and that monotonic equivalence
   is sufficient wherever “global optimizer” is used.
2. **Exact law and gate.** Recompute from the law definition, through a second symbolic
   route, the full and binned information matrices, the gate root, the
   off-(L) condition, efficiency, masses, separation, and the stated fixed
   margins. Check the pushforward density and the (M4) boundary-tube bound on
   the actual two-dimensional score law, including the rectangle/slab area
   constant and uniformity over all slab directions and offsets.
3. **Scalar upper problem.** Audit the scalar uniform three-bin theorem, including globality,
   uniqueness up to labels, every equality condition, and the upgrade from a
   unique maximizer to strict isolation. Do not assume cells are intervals:
   derive the nearest-centroid reassignment reduction for arbitrary measurable
   score-space cells and handle midpoint ties explicitly.
4. **Profiled sandwich and equality.** Audit both inequalities in
   \(\Phi_{D_s}(q)\le\operatorname{Var}(E[X\mid q])\le8/27\) and prove that
   simultaneous equality forces the stated rule up to labels. Pay special
   attention to arbitrary cells that depend on \(Z\), singular nuisance
   blocks, normal-equation solution sets, and whether regularity is needed
   for the population uniqueness statement.
5. **Strict isolation.** Give a complete compactness/rigidity proof in the
   declared decision distance, not merely a uniqueness argument. Verify that
   DS15's grouping-rigidity lemma applies to arbitrary \((X,Z)\)-measurable
   cells and supplies a uniform value gap at fixed decision distance.
6. **Empirical transfer.** Audit the empirical squeeze with its exact quantifiers: **every** sequence
   of finite global regular \(D_s\) optimizers, almost surely, up to labels.
   Verify eventual existence of a regular finite competitor/global optimizer,
   selection-independent probability-one events, scalar empirical-optimum
   consistency, the empirical form of grouping rigidity, label and moment
   convergence, uniform integrability, and that no sample-centering is hidden
   anywhere.
7. **Finite ordinary stability.** Check that finite global optimality really implies the claimed ordinary
   one-point exchange stability under the project's feasibility convention.
   Enumerate moves whose source or destination becomes singular and state
   exactly which moves belong to the ordinary comparison domain. Confirm that
   optimization over regular labelings cannot hide an improving move that the
   ordinary stability definition regards as feasible.
8. **Independent falsification.** Reproduce the minimized \(N=4\) raw-population-cut counterexample with an
   independent exact implementation. Search smaller supports and adversarial
   unequal-weight, duplicate, singleton, tie, and singular cases.
   Independently enumerate at least the declared \(N\le10\) search classes,
   recording canonical-partition counts and minimization evidence without
   importing the research harness.
9. **Protocol-G sweep.** Apply every adversarial attack in
   `protocols/theorem.md` §G and every relevant item in
   `protocols/numerical.md`, including score-estimation exclusion, label
   permutation, zero weights, atomic boundaries, empty cells, exact ties,
   near singularity, and the distinction between transductive labels and a
   rule for unseen observations.
10. **Fresh literature.** Run a fresh prior-art search for the combined claim: profiled Fisher/
   Schur-complement quantization, equal-interval scalar uniform quantization,
   empirical optimal-quantizer consistency, and finite exact exchange
   stability. Independently triangulate three to five nearest sources in the
   six fields required by `protocols/literature.md`; the existing DS18
   triangulation is comparison material only. Record direct antecedents and
   search gaps separately.
11. **Downstream blast radius.** Audit the DS18-dependent wording in OP29,
   `DS-PROFILED-COMPILE-CERTIFICATE`, and
   `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`. If DS18 is narrowed or fails, patch
   every downstream statement in the same audit. Even a verified theorem
   must retain the global-oracle/no-local-selection/no-`src/` boundary.

## Required 16-item report

Write the permanent audit report with these sections in this order:

1. Target statement
2. Criterion and problem level
3. Status before attempt
4. Dependencies rechecked
5. Nearest literature
6. Counterexample search
7. Algebraic reduction
8. Proof, counterexample, or conditional result
9. Adversarial audit
10. Algorithmic consequence
11. Deployability consequence
12. Information-loss consequence
13. Updated status
14. Registry patch
15. Counterexample/regression artifact
16. Next dependency-blocking question

The front matter must carry `**Claim:**`, `**Audit:**`, `**Date:**`,
`**Source frozen:**`, and `**Result:**`. Use
`AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md` as the size/rigor exemplar.

## Verdict rules

- **Verified** (possibly with hardened assumptions): the complete registered
  statement follows with all quantifiers, dependencies, and boundaries made
  explicit.
- **Refuted:** an exact counterexample or nonrepairable logical failure
  defeats the statement; minimize, serialize, and regression-pin it.
- **Reduced:** the theorem survives only under individually named unresolved
  assumptions. Do not hide a reduced result behind “verified with caveats.”

## Required outputs

- `AUDITS/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001.md`, containing the
  complete 16-item report.
- Independent instrument
  `py/audit_ds_noncentered_global_basin_transfer.py` and provenance-rich run
  records under
  `AUDITS/artifacts/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001/`, carrying
  `git_revision`, script SHA-256, Python/platform versions, exact search
  counts, and deterministic seed formulas where seeds are used.
- Verdict-driven patches to `DS-NONCENTERED-GLOBAL-BASIN-TRANSFER` and every
  affected downstream claim. A verified/hardened target gains an `audit`
  pointer and fully explicit assumptions/warning.
- New audit node `claims/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER.json`,
  with the report as `proof_location`, the independent script as `artifact`,
  and the audited target among its dependencies.
- Any new boundary failure minimized into `COUNTEREXAMPLES/<ID>.json`, added
  to the catalogue, linked through `boundary_counterexamples`, and pinned by
  a deterministic exact test in `tests/test_research_claims.py`.
- Independent regression tests for the exact law, equality chain, and the
  existing boundary fixture; the test must recompute from raw data rather
  than compare copied constants alone.
- `LITERATURE/audits/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-<date>.md`,
  graph/review/gap updates, and bibliography/topic registration for every new
  source.
- `NUMERICAL_EVIDENCE.md` rows for independent recomputation and search,
  citing the audit claim and executable source.
- `KNOWN_RESULTS/05b-ds-bridge.md`, `OPEN_PROBLEMS.md`, and
  `manuscripts/README.md` patches wherever the verdict changes or hardens
  wording.
- A clear algorithmic/deployment verdict. No `src/` or public API change
  belongs in this audit.
- Move this packet to `WORK/completed/` in the closing commit and add
  `## Outcome`, `## Artifacts`, and `## Validation` sections.

Never hand-edit generated indexes.

## Validation and commits

Commit independent falsification, the audit verdict/claim graph, and final
bookkeeping as separate cohesive milestones. Before finishing, all of the
following must be green:

```bash
uv run python agenticresearch/py/registry.py reindex && uv run python agenticresearch/py/registry.py validate
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_research_claims.py tests/test_research_registry.py
uv run ruff check .
uv run ruff format --check .
uv run ty check src
uv build
uv run mkdocs build --strict
```

## Stop condition

Stop only after the exact population theorem, equality/strict-isolation
chain, empirical quantifiers, ordinary-exchange feasibility boundary, and
serialized counterexample have each received an independent adversarial
verdict; the 16-item report and audit claim are registered; all affected
downstream wording is synchronized; the packet is moved to `WORK/completed/`;
and every validation command is green.

## Next dependency-blocking question

If DS18 is verified or hardened: can a practical profiled solver be proved to
select this full-rank basin without global combinatorial optimization, while
retaining computable margins and value guarantees under perturbations of the
law? If DS18 is refuted or reduced: what is the weakest corrected off-(L)
root-to-empirical transfer statement, and which OP29/compile-certificate
consequences must be withdrawn?
