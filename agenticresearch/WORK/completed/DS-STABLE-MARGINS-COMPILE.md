# DS-STABLE-MARGINS-COMPILE — margins at exchange-stable \(D_s\) states and the profiled compile rule

**Programme:** P1 (OPEN_PROBLEMS.md) · **Opened:** 30 Aug 2026 · **Status:** completed 30 Aug 2026
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

## Outcome

**All three stop conditions were hit, and the compile question is decided.**
DS16 (`KNOWN_RESULTS/05b-ds-bridge.md`; claims `DS-STABLE-MARGINS-PRICE`
project_proved, `DS-STABLE-STATE-SELECTION` measured,
`DS-PROFILED-COMPILE-CERTIFICATE` project_proved):

- **The question reframed.** Global optima are themselves exchange-stable, so
  "do stable sequences retain margins" was never a universal question — DS15
  already gives stable sequences where (M3) fails. What decides deployment is
  whether margins are *priced* and which regime the optimizer's terminals
  occupy.
- **Proved (price).** For every \(\kappa>0\): any labeling sequence with
  \(\hat I_{\lambda\lambda}\ge\kappa\) — stable or not, however seeded — has
  \(\limsup\hat\Phi_s\le v_K-\delta(\kappa)\), \(\delta(\kappa)>0\). Since
  \(\lambda_{\min}\le\hat I_{\lambda\lambda}\), the DS14 (M3) certificate has
  an intrinsic, stability-independent price. (R) is not needed.
- **Proved (funnel).** Any value-convergent sequence
  (\(\hat\Phi_s\to v_K\)) — every asymptotically successful solver run —
  inherits DS15's fate: (M2) holds, (M3) fails, cells converge to \(J^*\).
  DS15's degeneracy is value-topological, not a property of exact global
  optimality. This answers the packet's seeding blocker at theorem level: no
  seed can rescue the margins without sacrificing value.
- **Refuted with exact witnesses.** Stability certifies nothing in either
  direction: `CE-DS-STABLE-MARGIN-RETAINING-001` (N=8) is a non-global
  exchange-stable state with macroscopic margin triple
  (\(\hat I_{\lambda\lambda}\approx0.523\), \(\lambda_{\min}\ge0.14\), min
  mass 1/4, separation 0.32) at a 7.7% price;
  `CE-DS-INTERVAL-SEED-UNSTABLE-001` (N=8) shows the documented
  efficient-score initializer is not even a terminal state (exact improving
  gain 0.447, the move growing the nuisance block 27-fold — the finite face
  of DS15's steering).
- **Measured (selection).** Exact census N=10–14: stable states span both
  regimes, gap and nuisance block anti-correlated; margin-retaining
  non-global stable states exist in every instance. Library scale
  N=100–1000: every seeding (efficient-score, k-means++, random) terminates
  in the funnel on the centered law (\(N\hat I_{\lambda\lambda}\) median
  0.5–3.0, log-gap 0.004–0.046) while mix3 keeps
  \(\lambda_{\min}\approx1.7\) — the class boundary at terminal-state level.
- **Reduced (remainder).** Asymptotic inhabitation of the margin-retaining
  stable branch, attainment of \(v^*(\kappa)\), and the seeded-ascent
  selection law are `OPEN-DS-STABLE-BASINS` (OP30).
- **Compile verdict (the gating question).** The projected efficient-score
  interval rule is the **only unconditional** theorem-backed compile path on
  the class; a **certificate-gated** DS14 companion rule is legitimate only
  under the measured margin triple + DS13 stability, at the exactly
  computable and mandatorily reported price \(\hat v_K-\hat\Phi_s\) — and,
  measured, the free optimizer does not produce certifiable states at
  realistic N, so that path operationally requires margin-constrained
  optimization (OP7/OP30). The two-track story survives, but as
  *certificate-gated*, never automatic.

Cardinality restated before use (packet precondition): the mechanism is
\(\sum_b m_b=\hat\mu\), so a centered sample needs `n_bins > dimension`
(\(K\ge d_\psi+d_\lambda+1\)); the registered \(K\ge d_\lambda+2\) is its
\(d_\psi=1\) case (commit `891bbf3`; DS16 preamble; OP29 bullet corrected).
Prior-art triangulation cleared the round-3 snowball
(`LITERATURE/audits/DS-STABLE-MARGINS-PRICE-30-August-2026.md`): the
Silvey–Titterington line's stationarity-implies-global convexity is exactly
what hard partitions lack; no theory community covers the margin-price axis;
`search_gap` maintained.

## Artifacts

- `KNOWN_RESULTS/05b-ds-bridge.md` — new section DS16 (cardinality
  restatement, price/funnel/floor theorem with the empirical
  grouping-rigidity lemma, measured selection, compile verdict).
- `claims/` — new `DS-STABLE-MARGINS-PRICE`, `DS-STABLE-STATE-SELECTION`,
  `DS-PROFILED-COMPILE-CERTIFICATE`, `OPEN-DS-STABLE-BASINS`;
  `OPEN-DS-MARGINS-NONCENTERED` rescoped (branch (c) resolved; cardinality
  corrected).
- `COUNTEREXAMPLES/CE-DS-STABLE-MARGIN-RETAINING-001.json`,
  `CE-DS-INTERVAL-SEED-UNSTABLE-001.json` + catalogue entries; pinned by
  `tests/test_research_claims.py::test_ds16_exchange_stable_state_can_retain_macroscopic_margins`
  and `::test_ds16_efficient_score_interval_seed_is_not_exchange_stable`.
- `py/ds_stable_margins.py` — integer-exact full-lattice stable-state census
  (selftested against the audit-stack oracle), exact ascent, adversarial
  configs, library seed-dependence mode;
  `WORK/artifacts/DS-STABLE-MARGINS-COMPILE/census-summary.json`.
- `NUMERICAL_EVIDENCE.md` — rows N-DS-STABLE-CENSUS, N-DS-STABLE-ASCENT,
  N-DS-STABLE-LIBRARY.
- `OPEN_PROBLEMS.md` — P1 status updated; OP29 amended; OP30 added.
- `LITERATURE/audits/DS-STABLE-MARGINS-PRICE-30-August-2026.md`.
- `manuscripts/README.md` — staleness subsection (DS16 absent from v8).

## Proposed library surface (recorded, NOT implemented — audit gate first)

For the independent adversarial audit and the subsequent implementation
packet; nothing under `src/` changes in this session:

- `PartitionResult.compile_quantizer()` under `ProfiledDOptimality` keeps its
  refusal as the default, with the message upgraded from "no canonical
  inductive rule" to the DS16 reason: value-successful profiled terminals are
  nuisance-degenerate in the limit (funnel), so the free terminal is not
  stably compilable; route to the projected efficient-score workflow
  (`efficient_score_bound` → `ScalarDPConfig` via `fit_quantizer`), where the
  nuisance stays unbinned/full-sample.
- A future margin-certified path (gated on OP30/OP7 and the audit):
  `compile_quantizer(margins=ProfiledMarginPolicy(min_mass=c0, lambda_min=κ,
  separation=γ))` compiles the DS14 companion rule — assign by nearest
  projected centroid \(\hat e_b\) of \(\hat e(s)=s_\psi-\hat B_z s_\lambda\)
  in the \(S_\psi(\hat I_N)^{-1}\) metric — **iff** the terminal state is
  exchange-stable (DS13 certificate) and passes the measured triple;
  coincident/near-coincident centroids fall back to the DS11(d)/DS14 merged
  reduced rule or refuse. The result must report the certified triple and
  the price \(\hat v_K-\hat\Phi_s\) (from `efficient_score_bound`), and its
  report must state the retention cap \(\le1-\delta(\kappa)/v_K\) relative
  to the K-cell ceiling (invariant 7).
- `ScalarDPConfig` + `ProfiledDOptimality` pairing in `fit_quantizer` (the
  Track-1 rule as a first-class fit) may cite DS15/DS16 as its theorem
  backing; `api.py`'s solver-table comment should replace "no canonical
  inductive rule to compile" with a pointer to the certificate story.

## Falsification discipline

The census classifier was selftested against the independent audit-stack
oracle on 782 full-lattice states and 9,360 exact move updates before any
science was read off it; the exact sandwich and tax identities were verified
at all 3,155 stable states; DS13 held at every spot check; the adversarial
configs (duplicates, unequal weights, exact ties, near-singular nuisance,
tiny cells) ran through the independent Fraction path; the witnesses were
minimized to N=8 and pinned in CI before the theorem text was finalized.

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

`OPEN-DS-STABLE-BASINS` (OP30): **is the DS16 certificate branch inhabited
asymptotically — do margin-compatible exchange-stable sequences exist a.s.
as \(N\to\infty\), and is \(v^*(\kappa)\) attained by margin-compatible
stationary rules — and does seeded exchange ascent converge in value to
\(v_K\) a.s. (making terminal degeneracy a theorem rather than a
measurement)?** This is what blocks the next product increment: the
margin-certified compile path is theorem-legitimate (DS14 + DS16) but
operationally empty until either a margin-constrained solver exists (OP7
design, gated on OP30(a)) or the selection law is settled. The mathematical
halves of OP29 (non-centered laws, \(d_\psi>1\), \(d_\lambda\ge2\)
vector-(R) steering) proceed independently and feed P6/C2.
