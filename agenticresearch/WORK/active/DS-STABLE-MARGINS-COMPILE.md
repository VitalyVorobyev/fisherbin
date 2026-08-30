# DS-STABLE-MARGINS-COMPILE — margins at exchange-stable \(D_s\) states and the profiled compile rule

**Programme:** P1 (OPEN_PROBLEMS.md) · **Opened:** 30 Aug 2026 · **Status:** active
**Target claim:** `OPEN-DS-MARGINS-NONCENTERED` (OP29, deployment-facing branch)
**Descends from:** `WORK/completed/DS-MARGINS-AT-OPTIMA.md` and
`WORK/completed/AUDIT-DS-MARGINS-AT-OPTIMA.md`, whose next dependency-blocking
questions are identical to this packet's goal.

## Goal

Decide whether one-point **exchange-stable, non-global** finite \(D_s\)
labelings — what the library's optimizer actually returns — retain the DS14
margins (M2) mass, (M3) conditioning, (M5) projected-centroid separation on the
DS15 class (conditionally centered laws, \(d_\psi=d_\lambda=1\),
\(K\ge d_\lambda+2\)), almost surely along the sequence; and if so, at what
information cost \(v_K-\hat\Phi_s\) relative to the unrestricted supremum.

Then answer the question that gates the product: **does that yield a
theorem-backed inductive compile rule for `ProfiledDOptimality`, or is the
projected efficient-score interval rule the only such path?** DS15 settled this
at free global optima (it is the projected rule, because (M3) provably fails
there); the solver's terminal states are a different object and DS15 asserts
nothing about them.

"Done" is decidable three ways: a proof for the stated class; a counterexample
law (or exact finite witness) under which a margin fails along stable states
infinitely often; or a reduction to explicitly listed unresolved conditions.

## Why it matters

This is P1's product payoff and the last thing between existing theory and the
largest math-gated library feature. `docs/roadmap.md` defers
"Profiled-\(D_s\) compile-to-quantizer via the projected efficient-score
interval rule" naming *exactly this question* as its precondition;
`compile_quantizer` refuses profiled criteria today (`src/scorequant/result.py`,
the `isinstance(self.criterion, DOptimality)` guard), and `api.py`'s solver
table pairs `ScalarDPConfig` with `DOptimality` only, with a comment stating the
reason — "a profiled partition has no canonical inductive rule to compile into a
reusable quantizer".

A positive answer gives a certified **two-track** story: the projected
efficient-score rule at the optimum, and a margin-certified in-bin rule near it
with a stated \(\delta(\kappa)\) price. A negative answer makes the projected
rule the only theorem-backed compile path — also a shippable conclusion, and a
simpler one.

## Relevant claims

Target: `OPEN-DS-MARGINS-NONCENTERED`.

Branch the session owns: `OPEN-DS-MARGINS-AT-OPTIMA` (DS15),
`OPEN-DS-FINITE-POP-BRIDGE` (DS14 — read its `warning` field first),
`DS-EXCHANGE-LEVERAGE-BOUND` (DS13), `DS-PROFILED-VARIATIONAL` (DS11),
`OPEN-DS-POP-COMMON-METRIC` (DS12), `DS-SCALAR-EFFICIENT-DP`,
`DS-EFFICIENT-SCORE-DOMINATION`, `DS-EFFICIENT-SCORE-GLOBAL-UPPER`,
`DS-PROJECTED-K-REQUIREMENT`, `DS-EXCHANGE-TERMINATES`,
`DS-FULL-PROFILE-K-LE-D-SINGULAR`, `DS-GLOBAL-TIE-DEGENERACY`,
`DS-FINITE-GEOMETRY-FAILS`, `DS-GRADIENT-EFFICIENT-SEMIMETRIC`.

Use `py/registry.py show <ID> --deps --proof`; never read `claims/` linearly.

## Known blockers

- **DS15 does not transfer.** Its degeneracy conclusion is a statement about
  *global* optima, proved via an achievability (steering) construction that
  needs the global sup. A stable state is only locally unimprovable; the
  argument has no obvious analogue. Expect to need a different mechanism.
- **Nearby negative results.** `DS-FINITE-GEOMETRY-FAILS` (finite stability does
  not give the profiled geometry the D case enjoys) and
  `CE-DS-DEGENERATE-GLOBAL-TIE-001` sit directly next door; the profiled
  `GeometryReport` is deliberately a *different object* from D's for this reason
  (see `result.py`'s docstring on `geometry` vs `profiled_geometry`).
- **Cardinality.** `CE-DS-MARGINS-RANK-VACUITY-001` bounds what is even
  feasible. Note the registered \(K\ge d_\lambda+2\) is a \(d_\psi=1\) artifact:
  the library-side measurement in commit `891bbf3` established the real
  mechanism is \(\sum_b w_b m_b=\mu\), so a centered sample needs
  `n_bins > dimension`, which equals \(d_\lambda+2\) only when \(d_\psi=1\).
  Restate the condition correctly before using it.
- **Honest pricing.** Invariant 7 requires every result to report information
  loss versus unbinned inference. A two-track compile story is only admissible
  with \(\delta(\kappa)=v_K-v^*(\kappa)>0\) measured, not asserted.
- **Selection effects.** "What the optimizer returns" depends on
  initialization. `efficient_score_bound(...).labels` is the documented
  profiled initializer, and it is *the DS15 degenerate attainer* — so the
  solver may be seeded inside the degeneracy. Whether the margin verdict is a
  property of stable states or of the seeding is part of the question, and must
  be separated deliberately (compare seeds: efficient-score labels vs k-means vs
  random restarts).

## Recommended starting points

- **Reuse the harnesses, don't rebuild them.** `py/ds_margins_at_optima.py`
  (`trend` / `scalar` / `popref` / `anchor`) and
  `py/audit_ds_margins_at_optima.py` (`exhaustive`, `identities`, `vacuity`)
  already do exact-rational enumeration; the audit demonstrated ~42.6M exact
  evaluations is affordable in one session. The new experiment is
  **stable-state** enumeration rather than global-optimum enumeration. The
  D-side scripts are the closest template: `py/dopt_experiments.py` reaches and
  studies exchange-stable states (`exchange`, `e4_exchange_vs_voronoi`,
  `u5_theorem_check`) and has full-lattice helpers (`all_partitions`,
  `exhaustive_best`); `py/audit_d_exchange_voronoi.py` is the independent
  exact-rational version of the same sweep.
- The natural exact quantity: over the full lattice, enumerate *all* one-point
  exchange-stable labelings (not just the optimum) and track the same margin
  triple plus the value gap to \(v_K\). That is a superset of the existing
  optimum-only sweeps, and it directly measures the \(\delta\) price.
- Falsify first (`protocols/numerical.md`): ties, duplicates, singletons,
  singular information, nuisance singularity, unequal weights.
- Library cross-checks as certified ground truth: `efficient_score_bound`
  (exact scalar DP upper bound + attaining labels), `ScalarDPConfig`,
  `DExchangeConfig`, `profiled_information_report`.
- **Prior-art triangulation must now clear the round-3 snowball**
  (`LITERATURE/graph.json`, merged 30 Aug 2026): `Alsing-Wandelt-2019`
  (nuisance-hardened compression — the closest published antecedent to
  efficient-score domination), `Silvey-Titterington-1973` and
  `Silvey-Titterington-Torsney-1978` (geometric D/\(D_s\) duality; monotone
  finite-design-space algorithms — the algorithmic precedent for stable-state
  arguments), `Zhang-Blum-Kaplan-Lu-2018` (rank obstruction). Round 3 is
  explicitly **not** a saturation claim (`LITERATURE/gaps.md`).

## Required deliverables

- A new DS16 section in `KNOWN_RESULTS/05b-ds-bridge.md` with a `**Claims:**`
  line, stating the verdict and — if positive — the certificate a compile rule
  would check, together with its refusal conditions.
- Patched claim nodes under `claims/`, then `py/registry.py reindex`.
- Any counterexample minimized, serialized to `COUNTEREXAMPLES/` in the required
  format, and pinned by a deterministic test in `tests/test_research_claims.py`.
- `NUMERICAL_EVIDENCE.md` rows naming claim ids and executable sources.
- The P1 status line in `OPEN_PROBLEMS.md` updated; OP29's branch list amended
  (including the \(d_\psi\ge2\) cardinality correction above).
- `manuscripts/README.md` staleness note — item 7 of `protocols/theorem.md`; it
  has no other updater.
- The proposed library surface recorded **in this packet, not implemented**:
  what `compile_quantizer` (or a profiled `ScalarDPConfig` pairing) would
  return, what it would certify, and what it must still refuse.

## Out of scope

Deliberately, so the session does not drift:

- OP7 (`OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`) — solver benchmarking and the
  multivariate certified relaxation are a separate packet with different tools.
- OP29's mathematical branches — non-centered laws and \(d_\psi>1\). They feed
  P6/C2 and proceed independently.
- Any edit under `src/`. This result is a guarantee the library will ship, so it
  goes to an independent adversarial audit (`PLAYBOOK.md` §2) before any code
  change; the researcher must not embed its conclusions in the library first.

**Stretch, only after the deployment half reaches a verdict:** the
\(d_\lambda\ge2\), \(K\ge d_\lambda+2\) dichotomy via a vector-(R) steering
construction spanning the nuisance directions — the audit named it "behind it,
same node".

## Stop conditions

Proved for the stated class; refuted with a minimized serialized counterexample;
or reduced to explicitly listed unresolved conditions. All three are legitimate
closes — both prior P1 packets closed on the disjunction.

## Next dependency-blocking question

To be filled at close, named with its claim id, per `protocols/theorem.md`.
Do not close this packet without it.
