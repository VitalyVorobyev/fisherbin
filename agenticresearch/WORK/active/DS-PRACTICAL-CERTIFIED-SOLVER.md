# DS-PRACTICAL-CERTIFIED-SOLVER — a polynomial-time profiled solver with a two-sided certificate

**Programme:** P1 · **Opened:** 1 September 2026 · **Status:** active

## Goal

Decide whether the finite profiled \(D_s\) problem admits a **computable
two-sided certificate** that a polynomial-time algorithm can produce, and whether
its primal side is value-consistent. Concretely, for the tilted score
\(T_\beta=S_\psi-\beta S_\lambda\), DS11's variational form gives
\(\hat\Phi_{D_s}(z)=\min_\beta\operatorname{btw}(T_\beta;z)\) at
\(d_\psi=1\), hence the candidate bracket

\[
\underbrace{\max_\beta\hat\Phi_{D_s}\bigl(\mathrm{DP}_K(T_\beta)\bigr)}_{\textbf{primal }\hat p_N}
\;\le\;\max_z\hat\Phi_{D_s}(z)\;\le\;
\underbrace{\min_\beta\hat v_K(T_\beta)}_{\textbf{dual }\hat d_N}
\;\le\;\hat v_K(\hat s_N),
\]

where \(\mathrm{DP}_K\) is the exact scalar interval DP and \(\hat v_K(\cdot)\)
its optimal value. Four decidable questions:

1. **Validity and computability.** Is \(\hat d_N\) a valid ceiling on the *whole*
   comparison domain (in-bin DS9 **and** DS11 pseudo-inverse)? Is it exactly
   computable in polynomial time, including ties and duplicates?
2. **Exactness.** Characterize when the bracket closes
   (\(\hat p_N=\hat d_N\), certifying exact finite global optimality), and
   whether the gap can be \(\Theta(1)\).
3. **\(\Delta\)-consistency.** Does \(\Delta_N=\hat v_{K,N}-\hat\Phi_{D_s}(\tilde z_N)\to0\)
   a.s. for the polynomial-time primal \(\tilde z_N\) on the DS18 law? This is the
   exact question the DS18 audit left; any affirmative answer inherits the
   audited finite-\(N\) rate
   \(P_N(z\ne q^*)\le3\Delta_N/\eta+P_N(\text{band }\eta)\) and hence the whole
   transfer, converting a global-oracle theorem into a solver certificate.
4. **The compile decision rule.** State, as a theorem with observable inputs,
   what a bracket state plus a measured nuisance-block floor authorizes: the
   projected efficient-score interval rule, a DS14 companion rule, or refusal.

"Done" means a theorem, an exact counterexample, or a reduction to individually
listed assumptions — for **Tier A** at minimum. Another finite scan is not a
verdict.

### Tier A (load-bearing) — \(d_\psi=1\), \(d_\lambda\ge1\)

All four questions above. Vector nuisance makes \(\beta\in\mathbb R^{d_\lambda}\)
and the dual a \(d_\lambda\)-dimensional convex program; it requires
\(K\ge d_\psi+d_\lambda+1\) (`CE-DS-MARGINS-RANK-VACUITY-001`). Tier A must reach
a stop-condition verdict.

### Tier B (stretch, separately scored) — \(d_\psi>1\)

Weak duality does **not** need convexity: for *any* fixed tilt matrix \(B_0\),
the Loewner inequality \(V_z(B_0)\succeq S_\psi^+(I_z)\) makes
\(\max_z\log\det V_z(B_0)\) a valid certified ceiling, and that inner problem is
the \(d_\psi\)-dimensional D quantization problem on \(T_{B_0}\) — exactly what
`certify.py` branch-and-bound already solves. Questions: is the outer map
\(B_0\mapsto\max_z\log\det V_z(B_0)\) convex or quasiconvex (log-det is
concave-monotone and \(V_z\) matrix-convex, so this is **not** automatic)? Does
minimizing it give a usable certified upper problem where the library currently
refuses rather than approximates? Tier B carries its **own** stop condition and
must not consume Tier A's budget.

## Why it matters

This is the last question in P1 that gates the library. `compile_quantizer`
refuses profiled criteria (`src/scorequant/result.py:338-342`) and
`docs/roadmap.md:324-332` defers the profiled compile path explicitly pending
this programme. The dual side is not speculative product value: the library's
shipped `efficient_score_bound` (`src/scorequant/information.py:547`) is exactly
\(\hat v_K(\hat s_N)\) — the bracket evaluated at the single tilt
\(\beta=\hat B^*_N\) — so \(\hat d_N\) can only tighten an existing certificate.
And by DS17.1a the dual's Danskin stationarity condition,
\(I_{\psi\lambda}(z_\beta)=\beta I_{\lambda\lambda}(z_\beta)\), *is* the DS17.4
fixed-point gate: the gate stops being a per-law population scan and becomes a
finite-sample bisection.

On success, P1's deployment question is answered and the programme can exit
"Now", promoting P2 (`SCORE-ORACLE-ROBUSTNESS`).

## Relevant claims

- `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER` (target, OP7)
- `DS-PROFILED-VARIATIONAL` (DS11 — the bracket's source identity)
- `DS-EFFICIENT-SCORE-GLOBAL-UPPER`, `DS-SCALAR-EFFICIENT-DP` (the shipped ceiling)
- `DS-STABLE-BASINS-FIXED-POINT-GATE` (DS17.4 — the stationarity condition)
- `DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`, `AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER` (DS18 — the consumer of \(\Delta_N\))
- `DS-PROFILED-COMPILE-CERTIFICATE`, `DS-STABLE-MARGINS-PRICE` (DS16 — the verdict this would amend)
- `OPEN-DS-FINITE-POP-BRIDGE` (DS14 — the companion rule)
- `OPEN-DS-MARGINS-AT-OPTIMA` (DS15 — the (L)-side asymmetry)
- `DS-EXACT-MOVE-ORACLE`, `DS-EXCHANGE-LEVERAGE-BOUND` (refinement, if used)
- `DS-GLOBAL-NONGEOMETRIC`, `DS-FINITE-GEOMETRY-FAILS` (why the primal is only a bound)

## Known blockers

- **Weak duality is free; strong duality is not.** The primal maximizes over a
  finite nonconvex set. A \(\Theta(1)\) duality gap would kill question 2 — search
  for it before proving anything.
- **Finite global \(D_s\) optima need not be strip/geometric**
  (`CE-DS-GLOBAL-GEOMETRY-001`, `-002`). The strip-DP primal is therefore a lower
  bound *by construction* and may be strictly loose; do not assume otherwise.
- **The in-bin (DS9) feasibility convention is load-bearing**
  (`CE-DS-NONCENTERED-SINGULAR-DESTINATION-001`: at \(N=4\) on the DS18 law's own
  support, a pseudo-inverse comparison domain lets every global regular optimum
  escape by one move with gain \(1/96\)). The dual bounds the *larger*
  pseudo-inverse class — state that as a scope fact, do not gloss it.
- **\(\Delta\)-consistency is a value statement.** The DP interval seed is
  exchange-unstable (`CE-DS-INTERVAL-SEED-UNSTABLE-001`, exact gain \(0.447\)) and
  raw population-cut labels are unstable at the support-minimal \(N=4\)
  (`CE-DS-NONCENTERED-POPULATION-CUT-UNSTABLE-001`, exact gain \(37/14608\)).
  Do not upgrade a value result to exchange stability, to basin selection by
  local ascent, or to a compile authorization.
- **The (L) side is expected to fail \(\Delta\)-consistency.** By DS15
  Proposition 6 the tax is a \(\Theta_p(1)\) random *ratio* at the plain interval
  labeling, and the value \(v_K\) is reached only by steering. That asymmetry is
  what makes the certificate a decision rule rather than a defect — but it must
  be *proved*, on both sides, not asserted.
- **The exact dual minimizer is generally interior to a tilt-ordering cell**, not
  at a crossing of the \(N\) lines \(\beta\mapsto s_{\psi i}-\beta s_{\lambda i}\).
  A crossings grid is a heuristic, not an exact minimizer. Ties, duplicate scores,
  and non-differentiable points of the piecewise-quadratic max all need explicit
  treatment.
- **Cardinality.** \(K\ge d_\psi+d_\lambda+1\) is required for a centered sample
  (`CE-DS-MARGINS-RANK-VACUITY-001`); below it every feasible labeling has
  profiled value exactly \(0\).
- **`measured` nodes carry no theorem authority:** `DS-STABLE-STATE-SELECTION`
  and `DS-STABLE-BASINS-GATE-SCANS`. The mix3 root is evidence, not a premise.
- **Foundational edges are unaudited:** `DS-SCHUR`, `FI-QUANT-IDENTITY`,
  `FI-RANK-CEILING`. If one looks wrong, record an audit task; do not re-derive.
- **No sample centering.** Conditional centering is a population property. The
  chapter convention is uncentered second moments about the score-space origin,
  and DS18.2 explicitly performs no sample centering — mixing conventions is the
  defect (H1) the DS18 audit had to repair.

## Recommended starting points

- **The identity.** `KNOWN_RESULTS/05b-ds-bridge.md` DS11 (boxed variational
  form, and DS11(b) refinement monotonicity for the general-\(d_\psi\) Loewner
  gap), then DS17.1a for
  \(\frac{d}{d\beta}\operatorname{btw}(T_\beta;z)=-2(I_{\psi\lambda}(z)-\beta I_{\lambda\lambda}(z))\).
  Danskin plus convexity of the pointwise max is the whole dual algorithm:
  bisect on the sign of \(I_{\psi\lambda}(z_\beta)-\beta I_{\lambda\lambda}(z_\beta)\).
- **Exact computation.** The \(N\) lines have at most \(\binom N2+1\) distinct
  orderings, so the tilt arrangement gives an exact route; within an ordering cell
  the dual is a max of finitely many convex quadratics. Decide between exact
  arrangement sweep and certified convex bisection, and handle ties exactly.
- **Falsify first** (`protocols/numerical.md`, exact rationals): duality gap on
  adversarial small tables — ties, duplicates, singletons, near-singular nuisance
  blocks, unequal weights, both feasibility conventions.
- **The DS18 law** \(S_\psi=X\), \(S_\lambda=3X^2-1+Z\), \(X,Z\) iid
  \(\mathrm{Unif}[-1,1]\), \(K=3\), with \(q^*\) = equal thirds,
  \(I_{q^*}=\mathrm{diag}(8/27,32/81)\), \(\eta_{D_s}=8/9\). Note
  \(I_{\psi\lambda}(q^*)=0\) and \(I_{\lambda\lambda}(q^*)=32/81>0\), so the
  population tax vanishes and \(\Delta\)-consistency is plausible — check whether
  the empirical tax is \(O(1/N)\), which is the crux.
- **Harnesses.** `py/ds_noncentered_global_basin.py` (stdlib `Fraction`,
  exhaustive canonical/product-grid/adversarial enumeration through \(N=10\)) and
  `py/audit_ds_noncentered_global_basin_transfer.py` are the reproducible
  falsification instruments to extend, not to trust.
- **Library seam.** `src/scorequant/information.py:547` (`efficient_score_bound`,
  the single-tilt ceiling), `src/scorequant/reports.py:342`
  (`EfficientScoreBound.gap_to`), `src/scorequant/result.py:338-342` (the
  refusal), `src/scorequant/certify.py:110` (`certify_partition`, the Tier B inner
  solver).
- **Prior art to triangulate** (`protocols/literature.md`, before investing in a
  proof): Lagrangian/minimax duality for partially minimized quadratic criteria;
  \(D_s\)- versus c-optimality duality in optimal design (Elfving 1952, Silvey
  1978, Pukelsheim); Fisher (1958) grouping-for-maximum-homogeneity and its
  contiguity theorem; parametric/tilted 1-D clustering sweeps. An empty result is
  a search gap, never novelty.

### Planning probe — non-authoritative

An exact-rational probe run while drafting this packet (tiny \(N\), a
crossings+midpoints \(\beta\) grid, brute-force global optimum) found: on the
DS18 law weak duality held at \(N=7,8,9\) with dual gaps
\(2.5\times10^{-4}\), \(1.3\times10^{-3}\), \(3.2\times10^{-6}\), and the strip-DP
primal was exactly globally optimal at \(N=7,9\) but **not** at \(N=8\). On an
independent-coordinate (L)-type law the dual was strictly below
\(\hat v_K(\hat s_N)\) in both trials, and at \(N=9\) the strip primal landed on a
full-rank state (\(\hat I_{\lambda\lambda}=0.108\)) while the true global optimum
was the degenerate one (\(0.0035\)). This is a **probe**: a heuristic grid, no
tie handling, no convention sweep, three samples. It is recorded to show the
question is live in both directions, and carries no evidentiary weight. Reproduce
it properly under `protocols/numerical.md` before citing anything.

## Required deliverables

- Verdict-driven patch to `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER` and a new claim
  node for every result actually established, with `assumptions`, `warning`,
  `literature_search_status`, and `programme` set.
- A theorem or an exact counterexample with explicit hypotheses and quantifiers,
  naming the feasibility convention it is stated under.
- An exact-rational falsification harness under `agenticresearch/py/`, its run
  serialized to `WORK/artifacts/DS-PRACTICAL-CERTIFIED-SOLVER/`, and any
  counterexample minimized and serialized to `COUNTEREXAMPLES/` with a pinned
  test in `tests/test_research_claims.py`.
- A `KNOWN_RESULTS/05b-ds-bridge.md` **DS19** section in the chapter's style
  (normalization block, statement, proof, self-adversarial notes, deployability,
  what is deliberately not claimed).
- New `NUMERICAL_EVIDENCE.md` rows for reproducible measurements only; no scan
  promoted to theorem authority.
- A targeted `LITERATURE/` triangulation with exact theorem/page metadata, papers
  linked to claim ids, and a `**Key:**` line for any new bibliography key.
- `manuscripts/README.md` staleness note.
- **P1 closeout (specific to this packet).** On a *proved* or *reduced* Tier A
  verdict: rewrite the P1 block of `OPEN_PROBLEMS.md` to record that the
  deployment question is answered, and move the remaining academic branches out
  of P1 into P6/P7 — \(d_\psi>1\) dichotomy (if Tier B does not close),
  \(d_\lambda\ge2\) vector-(R) steering, (M5)-free wasted-cell tracking,
  \(v^*(\kappa)\)/\(v^{*+}(\kappa)\) attainment and one-sided continuity —
  patching each affected claim node's `programme` field and the `registry.json`
  programme ranks so P2 becomes rank 1. Indexes are generated: `reindex`, never
  hand-edit.
- **Deployment boundary.** This packet authorizes **no** `src/` or public API
  change. A compile surface requires a fresh independent audit
  (`protocols/audit.md`, `PLAYBOOK.md` §2) on the registered claim first.

## Stop conditions

**Tier A** — one of:

1. **Proved.** The bracket is a valid, exactly computable, polynomial-time
   certificate on a named comparison domain; its exactness condition is
   characterized; \(\Delta\)-consistency of \(\tilde z_N\) is settled on the DS18
   law; and the compile decision rule is stated with observable inputs.
2. **Disproved.** A serialized exact counterexample: a \(\Theta(1)\) duality gap,
   an invalidity of \(\hat d_N\) as a ceiling, or \(\Delta\)-inconsistency of the
   strip-DP primal.
3. **Reduced** to individually listed unresolved assumptions, each named with the
   object it constrains.

**Tier B** — its own verdict among the same three, or an explicit
"not attempted / budget exhausted" with the partial results recorded. Tier B
closing as *reduced* does not block a Tier A closure.

A numerical scan, however wide, is not a verdict for either tier.

## Next dependency-blocking question

To be filled by the session. Required by `protocols/theorem.md`; do not close
this packet without it. If Tier A proves, the expected successor is the audit
packet for the registered claim, followed by the `src/` landing named in
`docs/roadmap.md:324-332`.
