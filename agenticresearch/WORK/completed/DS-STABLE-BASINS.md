# DS-STABLE-BASINS — inhabit the margin-certified profiled branch

**Programme:** P1 · **Opened:** 30 August 2026 · **Closed:** 31 August 2026 · **Status:** completed

## Goal

Determine whether the DS14 companion-rule branch is non-vacuous on the
audited DS15/DS16 class. Concretely: for (d_\psi=d_\lambda=1), (K=3), and
at least the canonical nonsingular jointly Gaussian score law satisfying
(L)+(S), decide whether there are a fixed (\kappa>0) and an almost-sure
sequence of **unconstrained one-point exchange-stable** empirical labelings
whose mass, conditioning, and projected-separation margins satisfy DS14
eventually.

Prove existence, disprove it on the canonical law, or reduce it to explicit
population conditions whose truth can be independently checked. Do not
silently replace unconstrained exchange stability by stability only among
moves that preserve the margin.

## Why it matters

DS16 proves that every margin-retaining state pays a strict information price,
but it does not prove that exchange-stable states carrying such a margin exist
asymptotically. Until this packet is resolved, the DS14 companion rule is a
valid conditional theorem rather than an inhabited deployment path.

## Relevant claims

- `OPEN-DS-STABLE-BASINS` — primary target;
- `DS-STABLE-MARGINS-PRICE` — audited price/funnel/floor boundary;
- `DS-PROFILED-COMPILE-CERTIFICATE` — deployment consequence to harden or
  unlock;
- `OPEN-DS-FINITE-POP-BRIDGE` — DS14 sequence hypotheses and companion rule;
- `OPEN-DS-MARGINS-AT-OPTIMA` — audited DS15 law class and scalar limit;
- `DS-EXCHANGE-LEVERAGE-BOUND` and `DS-EXCHANGE-TERMINATES` — exact finite
  stability machinery;
- `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER` — downstream algorithmic branch;
- `DS-STABLE-STATE-SELECTION` — measured evidence only, never theorem
  authority.

## Known blockers

1. The DS16 audit (`AUDITS/AUDIT-DS-STABLE-MARGINS-COMPILE-001.md`) leaves
   attainment and one-sided continuity of both
   (v^{*+}(\kappa)=\sup\{\Phi(q):I_{q,\lambda\lambda}>\kappa\}) and
   (v^*(\kappa)=\sup\{\Phi(q):\lambda_{\min}(I_q)\ge\kappa\}) open. Do not
   conflate the strict nuisance-block constraint with the closed full-matrix
   constraint.
2. A margin-constrained exchange terminal need not be stable against a move
   that violates the constraint. DS14 requires ordinary one-point exchange
   stability. Any constrained-maximizer argument must prove the constraint is
   eventually slack by more than the (O(1/N)) effect of every single move.
3. A finite state passing mass/conditioning/separation checks is diagnostic
   only. DS14 also imports the law hypotheses and eventual uniform constants
   along a sequence.
4. Population stationarity does not automatically imply exact finite
   one-point stability: observations occur arbitrarily close to decision
   boundaries, where gains are on the same scale as finite-sample errors.
5. The free optimum cannot solve the problem on class (L)+(S): DS16 forces its
   nuisance block to zero. The desired states, if they exist, are necessarily
   non-global and priced.
6. The exact small-(N) census proves only that margin-retaining stable states
   occur before the asymptotic regime. Library free ascent entering the funnel
   through (N=1000) does not disprove other stable basins.

## Recommended starting points

1. Start from the exact Proposition-4 sandwich and the audited DS14/DS16
   statements. Recheck their hypotheses but do not re-prove DS11--DS16; open
   an audit task if an imported result appears wrong.
2. Formulate a population existence lemma with honest quantifiers. A promising
   route is a compact family of three-cell affine/efficient-Voronoi rules with
   explicit positive mass, conditioning, and separation margins. Determine
   whether the Gaussian law has a strict margin-compatible population local
   maximum or fixed point in that family.
3. If using constrained maximizers, separate three questions:
   attainment in a closed compact rule class; strict slack of the nuisance or
   eigenvalue constraint at the maximizer; and transfer from an empirical
   neighborhood maximizer to **unconstrained** one-point stability.
4. Derive the exact order of a one-point move's objective and margin changes
   near a population boundary. Attack the possibility that stochastic
   boundary points prevent eventual exact stability even around a strict
   population fixed point. A conditional transfer theorem is useful only if
   every condition is explicit and one nontrivial law is shown to satisfy it.
5. Build a new research instrument rather than extending
   `py/ds_stable_margins.py` blindly. Use deterministic high-accuracy Gaussian
   quadrature or exact rational finite approximations to search for candidate
   margin-compatible stationary rules, then independently recompute all
   population/finite margins and every finite move. Record seeds, revision,
   environment, and script hash under
   `WORK/artifacts/DS-STABLE-BASINS/`.
6. Falsify aggressively: vary (\kappa); include exact ties, duplicate
   efficient scores, tiny cells, near-singular nuisance blocks, and candidates
   whose constraint is active. Compare unconstrained ascent with genuinely
   constrained ascent and record which notion of stability each terminal
   satisfies.
7. Run a targeted primary-source pass on consistency of Hartigan/local
   empirical minima, constrained or balanced k-means, stability of strict
   population fixed points, and existence/attainment for information-based
   partition criteria. Follow `protocols/literature.md`; a gap is not novelty.

## Required deliverables

- A theorem, counterexample, or explicit conditional reduction recorded in a
  new DS17 section of `KNOWN_RESULTS/05b-ds-bridge.md`.
- A fully patched `OPEN-DS-STABLE-BASINS` node, plus consequences for
  `DS-PROFILED-COMPILE-CERTIFICATE` and
  `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER` if warranted.
- An independent executable and provenance-complete artifacts under
  `WORK/artifacts/DS-STABLE-BASINS/`; add measured rows to
  `NUMERICAL_EVIDENCE.md` without presenting them as proof.
- A targeted literature audit under `LITERATURE/audits/`, with registry and
  topic annotations for any new sources.
- Any falsifying boundary minimized into `COUNTEREXAMPLES/` and pinned in
  `tests/test_research_claims.py`.
- An explicit deployment statement distinguishing: an actually inhabited
  DS14 sequence, a finite diagnostic candidate, and a constrained terminal
  that is not unconstrained-stable.
- A manuscript staleness entry and a fresh independent-audit handoff if a new
  theorem would support a library compile guarantee. The research session
  must not audit its own result.
- No `src/` change in this packet.

## Stop conditions

Stop with one of these scientifically checkable outcomes:

1. **Proved:** for the canonical Gaussian law (or a stated nontrivial subclass
   of (L)+(S)), exhibit (\kappa,c_0,\gamma>0) and prove an almost-sure
   sequence of ordinary exchange-stable labelings satisfying DS14's eventual
   margins; identify the limiting companion rule and its strict DS16 price.
2. **Disproved:** give a rigorous obstruction showing no such sequence can
   exist on the canonical law or under a clearly stated law class. Serialize
   the smallest exact finite boundary witness if the obstruction has one.
3. **Reduced:** prove a necessary-and-sufficient or clearly sufficient
   population condition for inhabitation, prove the empirical transfer under
   that condition, and isolate one precise unresolved condition (not a list of
   informal hopes). Numerical satisfaction alone leaves that condition open.

Do not close merely because a constrained optimizer found a finite stable-
under-constraint state or because a long free-ascent run failed to find one.

## Next dependency-blocking question

If inhabitation is established, can a practical margin-constrained solver be
proved to select the inhabited basin with a computable gap to the attained
constrained value (`OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`)? If inhabitation is
refuted, what weaker certificate or alternative representation can replace
the DS14 companion branch without contradicting
`DS-STABLE-MARGINS-PRICE`?

---

## Outcome (31 August 2026)

**Stop condition 2 — DISPROVED — hit on the packet's own class, in a form
stronger than the packet asked for.** The goal question ("are there
\(\kappa,c_0,\gamma\) and an a.s. sequence of unconstrained exchange-stable
labelings with eventual DS14 margins, on at least the canonical Gaussian?")
is answered **no on every law of the DS15/DS16 class at once**, and not
merely for sequences: almost surely, for all large \(N\), no single
margin-compatible stable labeling exists.

- **The theorem** (`KNOWN_RESULTS/05b-ds-bridge.md` §DS17;
  `DS-STABLE-BASINS-CENTERED-OBSTRUCTION`): the exact tilt-residual identity
  \(B^*(I_q)-\beta=E[h(T_\beta)S_\lambda]/I_{\lambda\lambda}\) plus the
  conditional Chebyshev association inequality shows that on any atomless
  (L)-law no tilt-consistent strip rule keeps a positive nuisance block, at
  any tilt; the pathwise DS14′ lemma (DS17.0) chains this to eventual
  emptiness of the (M2)+(M3)+(M5) stable class. Neither (S) nor (R) is
  needed; jointly Gaussian, elliptical (with an independent LCM rank-one
  second proof and the Möbius discriminant identity), product-nuisance, and
  dependent (L)-laws are all instances.
- **The (M5)-free escape is classified**
  (`DS-STABLE-BASINS-LCM-CLASSIFICATION`): margin-compatible stationary
  configurations exist on the canonical law (sign-split family,
  \(\lambda_{\min}\) up to \(1/\pi\)) but are wasted-cell structures — value
  pinned at \(v_2\) in every scanned instance, compilable reductions with
  \(\lambda_{\min}=0\). This also proves DS16's constraint class
  \(\{\lambda_{\min}(I_q)\ge\kappa\}\) nonempty for \(\kappa\le1/\pi\):
  the audit's attainment subproblem has a nonvacuous feasible set. Fixture
  `CE-DS-LCM-SIGNSPLIT-MARGIN-001` ((M5) is load-bearing), CI-pinned.
- **The gate** (`DS-STABLE-BASINS-FIXED-POINT-GATE`): inhabitation reduces
  per law to the scalar root equation \(E[h(T_\beta)S_\lambda]=0\) over
  Lloyd-stationary branches. Measured (`DS-STABLE-BASINS-GATE-SCANS`,
  instrument `py/ds_stable_basins.py`): eight (L)-laws across three
  structural families have zero roots (the theorem's falsification evidence,
  run before the proof was trusted); mix3 — off-class — has exactly one
  root, the efficient interval optimum itself, carrying
  \(\lambda_{\min}=1.7364\) at price \(\approx0\): conditional centering,
  not binning, is what makes margins expensive.
- **Blockers honored:** unconstrained one-point stability was never traded
  for stability-under-constraint (blocker on silent replacement); the
  \(N\le14\) margin-retaining census states are pre-asymptotic exactly as
  blocker 3/6 warned — the geometry scan shows the class boundary in the
  recorded DS16 terminals (2% companion-exact on centered06 vs 61% on mix3).

## Deployment statement (required deliverable)

- *Inhabited DS14 sequence:* *impossible* on class (L) — the certified
  compile branch is vacuous asymptotically; `compile_quantizer`'s refusal
  needs no certificate carve-out there.
- *Finite diagnostic:* still legitimate as a diagnostic (the \(N=8\) witness
  is even companion-exact) but transient on the class; it certifies nothing
  asymptotic.
- *Constrained terminal:* the only object a margin-constrained solver can
  deliver on the class, and it is not ordinary-exchange-stable eventually;
  any future `ProfiledMarginPolicy` surface must present it as constrained,
  priced (\(\hat v_K-\hat\Phi_s\)), and non-inductive on this class. Off the
  class, target the gate roots (OP29(a)); on mix3-like laws certification is
  free.

No `src/` file changed. The result goes to a fresh independent adversarial
audit before any library change (the session did not audit itself).

## Artifacts

- `KNOWN_RESULTS/05b-ds-bridge.md` §DS17 (theorems DS17.0–DS17.4, protocol
  F/G passes, measured, verdict).
- Claims: `DS-STABLE-BASINS-{CENTERED-OBSTRUCTION, LCM-CLASSIFICATION,
  FIXED-POINT-GATE, GATE-SCANS}` new;
  `OPEN-DS-STABLE-BASINS` rerouted; `DS-PROFILED-COMPILE-CERTIFICATE`,
  `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`, `OPEN-DS-MARGINS-NONCENTERED`
  patched; OP30/OP29/OP7/P1 updated in `OPEN_PROBLEMS.md`.
- `COUNTEREXAMPLES/CE-DS-LCM-SIGNSPLIT-MARGIN-001.json` + catalogue entry +
  pin `tests/test_research_claims.py::test_ds17_signsplit_stationary_state_retains_margins_without_separation`.
- Instrument `py/ds_stable_basins.py` (selftest-validated against the public
  Gauss–Legendre quadrature at \(10^{-9}\) and exact 8-atom rationals);
  provenance-complete artifacts under `WORK/artifacts/DS-STABLE-BASINS/`;
  ledger rows N-DS-BASINS-* in `NUMERICAL_EVIDENCE.md`.
- Literature round 4: Flury-1990, Tarpey-Flury-1996, Tarpey-Li-Flury-1995,
  Serinko-Babu-1992 registered; triangulation
  `LITERATURE/audits/DS-STABLE-BASINS-31-August-2026.md`; cluster note in
  `topics/04-vector-quantization.md`; `search_gap` maintained.
- `manuscripts/README.md` staleness block "Added 31 August 2026".
- Erratum note (registry hygiene, not acted on in the permanent audit
  artifact): `AUDITS/AUDIT-DS-STABLE-MARGINS-COMPILE-001.md` §15 cites the
  test name `test_ds16_interval_initializer_can_be_exchange_unstable`; the
  actual CI pin is
  `test_ds16_efficient_score_interval_seed_is_not_exchange_stable`.

## Falsification discipline

The population scans ran before the proofs were trusted and were built to
find roots, not to confirm their absence: branch-tracked continuation over
Lloyd-*stationary* (not only optimal) branches, asymmetric mode-splitting
branches included, plus the off-class control that *does* produce a root.
The instrument's evaluator was validated against an independent quadrature
path through the shipped library and exact rationals before any scan was
believed.

## Next dependency-blocking question

`OPEN-DS-MARGINS-NONCENTERED` (OP29 branch (a)), now carrying the live
question with a concrete tool: for non-centered laws, does the
`DS-STABLE-BASINS-FIXED-POINT-GATE` root equation admit nondegenerate
solutions on a stated class (measured yes on mix3, at price \(\approx0\)),
and does the empirical transfer hold — from a nondegenerate root's basin to
exact one-point exchange stability against \(O(1/N)\)-scale boundary noise
(DS14 Step-1)? Behind it: DS16's \(v^*(\kappa)\) attainment on the now
provably nonempty constraint class (OP30(a″)), and OP7's constrained-solver
design under the DS17 constraints.
