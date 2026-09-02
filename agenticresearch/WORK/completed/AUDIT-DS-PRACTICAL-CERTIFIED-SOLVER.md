# AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER — independent adversarial audit of DS19

**Programme:** P1 (closed; audit gate) · **Opened:** 2 September 2026 · **Closed:** 2 September 2026 · **Status:** completed
**Source frozen:** `research-ds-practical-certified-solver` at `2c9cb77`

## Goal

Independently verify, harden, refute, or reduce the DS19 theorem complex,
using `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER` as the umbrella target and issuing
separate verdicts for:

- `DS-TILT-DUAL-CERTIFICATE`;
- `DS-TILT-DUAL-STRONG-DUALITY-FAILS`;
- `DS-STRIP-DP-DELTA-CONSISTENCY`;
- `DS-MATRIX-TILT-NONQUASICONVEX`; and
- the DS19 clauses of `DS-PROFILED-COMPILE-CERTIFICATE`.

The audit must decide whether DS19's domain split, weak ceiling, saddle
closure condition, computation claims, order-one family, DS18 value transfer,
Tier B counterexample, and observable deployment table survive independent
attack. The primary deliverable is the 16-item publication-grade report
`AUDITS/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001.md`.

## Why it matters

DS19 closed P1's deployment question by reduction and registered several
load-bearing internal guarantees. The escalation ladder requires a fresh
independent audit before any of those guarantees may support a library or
publication claim. This packet authorizes no `src/`, public API, example, or
compile-path change.

## Independence contract

- Run in a brand-new session that did not produce DS19 and has not received
  the researcher's chat transcript. The frozen repository, this packet, and
  the registered artifacts are the complete handoff.
- Create an audit branch from the packet-bearing research branch. Treat
  commit `2c9cb77` as the frozen theorem source even though the packet itself
  is added by a later bookkeeping commit.
- Do not import, extend, or copy
  `py/ds_practical_certified_solver.py`. Build the audit instrument
  independently as `py/audit_ds_practical_certified_solver.py`.
- Use `fractions.Fraction` for every claim-relevant finite computation. A
  separate symbolic, interval, or proof route must check asymptotic and
  algebraic-complexity statements.
- Recheck the dependency closure returned by `registry.py show`; do not
  re-prove audited `project_proved` dependencies. If one appears false,
  record a separate audit task and its blast radius.
- Treat the existing proof, harness, fixtures, tests, literature audit, and
  self-adversarial notes as claims to attack, not as audit evidence.
- Preserve the distinction between finite labels, empirical inductive rules,
  and population quantizers. Never sample-center the score rows.

## Relevant claims and artifacts

Start from:

```bash
uv run python agenticresearch/py/registry.py show OPEN-DS-PRACTICAL-CERTIFIED-SOLVER --deps --proof
```

Then inspect the component nodes listed in the goal and their converse or
boundary edges. The frozen research artifacts are:

- `KNOWN_RESULTS/05b-ds-bridge.md`, DS19;
- `COUNTEREXAMPLES/CE-DS-TILT-DUAL-GAP-001.json`;
- `COUNTEREXAMPLES/CE-DS-MATRIX-TILT-NONQUASICONVEX-001.json`;
- `WORK/artifacts/DS-PRACTICAL-CERTIFIED-SOLVER/`;
- `LITERATURE/audits/OPEN-DS-PRACTICAL-CERTIFIED-SOLVER-1-September-2026.md`;
- `py/ds_practical_certified_solver.py`; and
- the DS19 regressions in `tests/test_research_claims.py`.

The inherited load-bearing nodes include
`DS-PROFILED-VARIATIONAL`, `DS-SCALAR-EFFICIENT-DP`,
`DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`, and
`AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`.

## Required attacks

1. **Registry and quantifier audit.** Resolve the umbrella and every component
   through the registry. Check status, level, comparison domain,
   exact-\(K\)-nonempty convention, weight assumptions, tie semantics, and all
   `dependencies`/`implies` edges. Confirm that the P1 closeout did not turn a
   reduced computation claim or a measured scan into theorem authority.

2. **Fixed-partition algebra and domain split.** Starting from the already
   audited DS11 identity, independently check its use for raw uncentered
   finite score tables. Verify

   \[
   \Phi^+(z)=\min_\beta V_z(\beta)
   \]

   including singular nuisance blocks and normal-equation solution sets.
   Prove or refute that the same dual ceiling covers the whole DS11
   pseudo-inverse class and therefore the regular DS9 subclass. Check that a
   singular DP state is never presented as a DS9 lower bound.

3. **Weak bracket and primal definition.** Audit the definitions and
   attainment of \(p^+,p_{\rm reg},g^+,g_{\rm reg},d\). Check deterministic
   tie policies, all DP-optimal refinements at exact ties, duplicate full-score
   atoms, zero-weight rows versus the theorem's positive-weight scope, and
   collapsed-atom versus unrestricted-row semantics. Try to falsify every
   inequality before accepting it.

4. **Saddle closure equivalence.** Re-prove both directions of the claimed
   iff without assuming minimax interchange. Verify dual attainment after
   quotienting common nuisance-null directions and confirm that

   \[
   z^*\in\mathcal D(\beta^*),\qquad
   \beta^*I_{\lambda\lambda}(z^*)=I_{\psi\lambda}(z^*)
   \]

   is sufficient and necessary for bracket closure. Attack singular blocks,
   nonunique dual minimizers, nonunique DP states, ordering-cell boundaries,
   and the extra regularity needed to certify the ordinary in-bin optimum.

5. **Three computation guarantees.** Keep these claims separate and audit
   their bit models, not merely arithmetic-operation counts:

   - exact rational \(O(KN^2)\) interval-DP value, active labeling, and active
     subgradient at a supplied rational tilt;
   - polynomial-time certified rational \(\varepsilon\)-minimization of the
     convex envelope, including a polynomial-bit search radius, effective
     nuisance-span quotient, separation oracle, stopping certificate, and
     dependence on \(\log(1/\varepsilon)\); and
   - exact algebraic minimization for fixed \((K,d_\lambda)\), including the
     tilt-order arrangement, tie faces, algebraic output representation, and
     comparison complexity.

   In particular, try to break the claimed coercivity/radius argument and the
   fixed-dimensional polynomial bound. Confirm that no approximate convex
   solve is called exact. The variable-\((K,d_\lambda)\) claim must remain
   precisely `OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY` unless the audit supplies a
   proof or a valid hardness obstruction.

6. **Exact scalar dual-gap witness.** With an implementation independent of
   the research harness, enumerate all six \(N=4,K=3\) partitions and
   recompute regularity, global value \(116805/11816\), both active
   quadratics, mixture weight \(14/25\), vertex \(-10128/29197\), mixture
   minimum \(61717893/5839400\), and gap lower bound
   \(105329256/154014175>0.68\). Verify support minimality under the stated
   exact-\(K\) semantics and distinguish a lower certificate on the dual from
   an exact computation of its minimizer.

7. **Genuine order-one family.** Audit the positive-weight bounded rational
   augmentation family without invoking unrestricted split-duplicate
   invariance. Supply uniform cellwise bounds over every exact-\(K\) labeling,
   control singular generalized-Schur cells, and justify one common compact
   set for dual minimizers. Check the requested \(o(1)\) perturbation of the
   primal, global, and dual values separately. If the frozen proof establishes
   only the global-versus-dual gap, harden the statement rather than silently
   granting the stronger primal convergence claim.

8. **DS18 \(\Delta\)-consistency.** On the exact DS18 law, independently prove
   or refute that the raw, uncentered \(\beta=0\) three-interval DP labeling
   \(\tilde z_N\) is eventually regular and

   \[
   0\le \hat v_{3,N}(X)-\hat\Phi_{D_s}(\tilde z_N)
   =\hat I_{\psi\lambda}(\tilde z_N)^2/
     \hat I_{\lambda\lambda}(\tilde z_N)\to0
   \quad\text{a.s.}
   \]

   Check uniqueness/consistency of the empirical scalar optimum, convergence
   of data-dependent DP cells and moments, selection-independent probability-
   one events, boundary ties, and the limits \(0\) and \(32/81\). Re-derive
   exactly which DS18 disagreement inequality applies to this labeling. Do
   not infer exchange stability, local-ascent basin selection, perturbation
   robustness, or compile authorization.

9. **Tier B counterexample.** Independently recompute the centered
   \(\{\pm2e_j\}_{j=1}^4\), \(K=N=8\) singleton construction, derive
   \(V(B)=I_2+BB^\top\), and check the exact determinant midpoint violation
   \(17,17,25\). Confirm that it disproves quasiconvexity of the stated
   log-determinant outer map while leaving weak matrix-tilt duality intact.

10. **Independent falsification sweep.** Follow `protocols/numerical.md` with
    an independently written exact oracle. At minimum cover \(N\le10\), the
    smallest rank-feasible cardinalities, unequal/tiny positive weights,
    ties, duplicates, singletons, near-singular and singular nuisance blocks,
    DS9 and DS11 domains, and collapsed-atom and unrestricted-row semantics.
    Search for ceiling failures, false saddle closures, stronger support-
    minimal witnesses, DS18 tax failures, and matrix-tilt counterexamples.
    Store provenance-complete summaries, never raw enumeration output.

11. **Fresh literature triangulation.** Apply `protocols/literature.md`
    independently. Give three to five six-field comparisons covering fixed-
    partition generalized Schur minimization, design-side \(D_s\) duality,
    scalar grouping/contiguity, parametric shortest-path or segmentation
    complexity, and the empirical quantizer-consistency step used by DS18.
    Treat Li--Mathias, Silvey--Titterington, Fisher, and
    Gajjar--Radhakrishnan as comparison material, not audit conclusions.
    Record direct antecedents and `search_gap` separately; never claim novelty.

12. **Downstream blast radius and programme closeout.** Audit the five-case
    observable table in `DS-PROFILED-COMPILE-CERTIFICATE`, the reduced verdict
    in `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`, OP31's exact-complexity scope,
    the OP29/OP30 rescope, and removal of P1 from `registry.json`. A verified
    audit may remove the "unaudited" warning, but it must not itself implement
    a compile path. If any component is narrowed or fails, patch every
    downstream statement in the same audit.

13. **Full protocol-G sweep.** Apply every adversarial attack in
    `protocols/theorem.md` section G and every relevant numerical checklist
    item. Explicitly cover reparameterization, bin relabeling, event ordering,
    uniform weight scaling, split-weight duplication within its valid
    semantics, empty cells, exact ties, finite versus population levels, and
    exact versus estimated scores.

## Required 16-item report

Write `AUDITS/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001.md` with these sections
in this order:

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

The front matter must carry `**Claims:**`, `**Audit:**`, `**Date:**`,
`**Source frozen:**`, and `**Result:**`. Use
`AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md` as the rigor exemplar. Give a verdict
for every component claim, not only an aggregate verdict.

## Verdict rules

- **Verified**: the complete registered statement follows with its existing
  quantifiers and assumptions.
- **Verified with hardened assumptions**: the mathematical core survives but
  statement, proof, assumptions, graph, or boundary wording requires a
  correction that is fully incorporated.
- **Refuted**: an exact counterexample or nonrepairable logical failure defeats
  the claim; minimize, serialize, and regression-pin it.
- **Reduced**: the result survives only under individually named unresolved
  assumptions. Do not hide a reduction behind caveat language.

## Required deliverables

- The complete 16-item report
  `AUDITS/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001.md`.
- Independent instrument `py/audit_ds_practical_certified_solver.py` and
  provenance-rich records under
  `AUDITS/artifacts/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001/`, including git
  revision, script SHA-256, Python/platform versions, arithmetic mode, search
  counts, and deterministic seed formulas where relevant.
- New node `claims/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER.json`, with all audited
  components among its dependencies, the report as `proof_location`, and the
  audit script as `artifact`.
- Verdict-driven patches to every audited claim: audit pointers, complete
  assumptions/warnings, dependency edges, literature status, and downstream
  wording. Do not alter an inherited proved claim merely for convenience.
- Any new exact boundary failure minimized into
  `COUNTEREXAMPLES/<ID>.json`, catalogued, linked, and pinned by a deterministic
  test that recomputes it from raw data.
- Independent regression tests for the scalar witness, weak ceiling, saddle
  closure, DS9/DS11 split, computation boundaries, DS18 tax identity, and Tier
  B midpoint violation.
- `LITERATURE/audits/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-2-September-2026.md`
  plus graph/review/gap/topic updates and a `**Key:**` annotation for every
  new bibliography key.
- `NUMERICAL_EVIDENCE.md` rows for independent measurements only, citing the
  audit claim and executable source.
- `KNOWN_RESULTS/05b-ds-bridge.md`, `OPEN_PROBLEMS.md`, and
  `manuscripts/README.md` patches wherever the verdict hardens or changes the
  frozen wording.
- Move this packet to `WORK/completed/` in the closing commit and add
  `## Outcome`, `## Artifacts`, and `## Validation` sections.
- No `src/`, public API, example, benchmark, or compile-path implementation.

Never hand-edit generated indexes.

## Validation and commits

Commit the independent falsification, verdict/claim graph, and final
bookkeeping as separate cohesive milestones. Before finishing, all commands
below must be green:

```bash
uv run python agenticresearch/py/registry.py reindex
uv run python agenticresearch/py/registry.py validate
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_research_claims.py tests/test_research_registry.py
uv run ruff check .
uv run ruff format --check .
uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
```

Finish with a clean worktree. Do not push, merge, publish, or implement the
audited capability.

## Stop conditions

Close only after every component has a named audit verdict; the weak ceiling,
saddle iff, all three computation guarantees, order-one family, DS18 value
chain, Tier B witness, and observable refusal table have each received an
independent adversarial decision; the 16-item report and audit node are
registered; every boundary failure is serialized; downstream wording and
indexes are synchronized; this packet is moved to `WORK/completed/`; and all
validation commands are green.

A numerical sweep without an algebraic verdict is not completion. A verified
weak ceiling does not verify exact polynomial computation. A verified
\(\Delta\)-value statement does not verify exchange stability or compilation.


## Outcome

**Verified with hardened assumptions (Tier A); verified (DS18 value chain and
Tier B); umbrella reduced with a narrower remainder.** Every component
received an independent adversarial decision
(`AUDITS/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001.md`, sixteen items):

- **Weak ceiling and domain split** — verified on both the DS11 and DS9
  domains; 125,491 canonical partitions, zero violations; singular DP states
  never counted as in-bin bounds; five tables where the generalized value
  exceeds the regular one.
- **Saddle iff** — re-proved in both directions without minimax interchange;
  exact on 54/54 tables with exact algebraic dual minima. **H2:** the gate is
  set-valued; a deterministic DP tie policy can hide a closure
  (`CE-DS-TILT-DUAL-TIE-MASK-001`, \(N=3,K=2\)), so an open *reported*
  bracket is not a gap certificate.
- **Three computation guarantees** — fixed-tilt DP verified, with the missing
  **tie lemma** supplied (H1) and the bound tightened to \(O(KN)\) after
  sorting; certified-\(\varepsilon\) bracket verified with an explicit bit
  model (H3: radius, LP certificate, rounding); exact computation **widened**:
  polynomial-bit exact minimisation at \(d_\lambda=1\) for every \(K\)
  (audit proof, implemented and certified), arithmetic-polynomial for fixed
  \(d_\lambda\ge2\) by Toledo (1993). OP31 narrowed accordingly.
- **Order-one family** — verified as an asymptotic global-versus-dual
  statement; constants recorded; primal convergence explicitly not claimed.
- **Scalar witness** — all rationals reproduced; exact \(d=44729/4232\),
  exact gap \(534361/781333\). **H4:** support minimality is \(K=3\)-only;
  the overall minimum `CE-DS-TILT-DUAL-GAP-002` (\(N=3,K=2\), gap \(1/6\))
  is serialized.
- **DS18 \(\Delta\)-value chain** — verified; the uncentered/centered
  identity makes the strip DP the empirical 3-means labeling, DS18's
  selection-independent event applies, and the finite-\(N\) bound holds with
  the labeling's own \(\Delta_N\) (exact on 12 samples to \(N=4096\)).
- **Tier B** — verified from raw rows; weak matrix duality intact.
- **Observable refusal table** — verified with the tie-mask caveat on row (2).

No `src/`, public API, example, benchmark, or compile-path change was made;
the audit removes the "unaudited" warnings and nothing more.

## Artifacts

- `AUDITS/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001.md` — the 16-item report
- `py/audit_ds_practical_certified_solver.py` — the independent instrument
  (stages `witness`, `ceiling`, `saddle`, `ties`, `compute`, `family`,
  `ds18`, `tierb`, `invariances`, `fixtures`)
- `AUDITS/artifacts/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001/*.json` — ten
  provenance-stamped records
- `claims/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER.json` — new audit node
- `COUNTEREXAMPLES/CE-DS-TILT-DUAL-GAP-002.json`,
  `COUNTEREXAMPLES/CE-DS-TILT-DUAL-TIE-MASK-001.json` — new exact fixtures
- `LITERATURE/audits/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-2-September-2026.md`
  and six new bibliography keys (`Toledo-1993`, `Megiddo-1983`,
  `Gronlund-etal-2017`, `Wang-Song-2011`, `Pukelsheim-Titterington-1983`,
  `Carstensen-1983`)
- patched: `claims/{DS-TILT-DUAL-CERTIFICATE,DS-TILT-DUAL-STRONG-DUALITY-FAILS,DS-STRIP-DP-DELTA-CONSISTENCY,DS-MATRIX-TILT-NONQUASICONVEX,DS-PROFILED-COMPILE-CERTIFICATE,OPEN-DS-PRACTICAL-CERTIFIED-SOLVER,OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY}.json`,
  `KNOWN_RESULTS/05b-ds-bridge.md` (DS19), `OPEN_PROBLEMS.md` (P1 block,
  OP31), `manuscripts/README.md`, `NUMERICAL_EVIDENCE.md` (seven
  `N-DS-AUDIT19-*` rows), `COUNTEREXAMPLES/README.md`, `registry.json`,
  `LITERATURE/{graph.json,reviewed.md,gaps.md,topics/01-optimal-design.md,topics/04-vector-quantization.md}`,
  `tests/test_research_claims.py` (eight new exact regressions)

## Validation

All closure checks green on 2 September 2026:

- `uv run python agenticresearch/py/audit_ds_practical_certified_solver.py all`
- `uv run python agenticresearch/py/registry.py reindex` (`indexes current`)
  and `validate` (`registry clean`)
- `JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_research_claims.py tests/test_research_registry.py`
- `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check src`
- `JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto`
- `JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py`
- `uv build`, `uv run mkdocs build --strict`

## Next dependency-blocking question

**Answered branch: verified and hardened.** The remaining question is the
narrowed OP31: does `OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY` admit a polynomial
*bit* algorithm for fixed \(d_\lambda\ge2\) with variable \(K\), and is
variable \(d_\lambda\) hard? The deployment-facing blocker is a selection
theorem for the labeling a practical solver returns. The original packet text
follows.

If DS19 is verified or hardened, does
`OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY` admit an exact polynomial-bit algorithm
for variable \((K,d_\lambda)\), including tie refinements, or a valid hardness
obstruction? If DS19 is refuted or further reduced, what is the strongest
corrected certificate/value-transfer statement, and which P1 closeout or
compile-certificate consequences must be withdrawn?
