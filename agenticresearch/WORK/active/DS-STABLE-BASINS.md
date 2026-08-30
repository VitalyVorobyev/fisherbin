# DS-STABLE-BASINS — inhabit the margin-certified profiled branch

**Programme:** P1 · **Opened:** 30 August 2026 · **Status:** active

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
