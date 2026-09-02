# Counterexample bank
**Purpose:** reusable falsification cases for theorem agents.

A counterexample is only useful if it is:

- exactly reproducible;
- stored with objective/criterion;
- explicit about finite/population level;
- explicit about weights, labels, and parameter split;
- verified by recomputation;
- accompanied by the exact claim it falsifies.

Do not store only screenshots or random seeds.

---

The quick table of every fixture is generated: see `INDEX.md`.

# Required JSON format for new cases
Each exact case should also have a `.json` file:

```json
{
  "id": "CE-...",
  "criterion": "D|Ds|E|A|...",
  "level": "finite_assignment",
  "claim_falsified": "...",
  "scores": [[...], [...]],
  "weights": [...],
  "K": 3,
  "labels_before": [...],
  "labels_after_or_optimum": [...],
  "poi_indices": [0],
  "nuisance_indices": [1],
  "objective_before": null,
  "objective_after": null,
  "verification": {
    "method": "exhaustive|exact_formula|high_precision",
    "notes": "..."
  },
  "source": "project test / theorem investigation",
  "date": "YYYY-MM-DD"
}
```

---

# Falsification checklist
For every new theorem candidate, deliberately test:

- \(d=1,2,3\);
- smallest rank-feasible \(K\);
- \(N\le10\) exhaustive partitions;
- unequal weights;
- tiny cells;
- singleton cells;
- duplicate score atoms;
- near-singular \(I_q\);
- repeated E minimum eigenvalues;
- weak/singular nuisance blocks;
- exact ties;
- rational/integer coordinates when possible.

The counterexample bank is part of the mathematical memory of the project, not merely a debugging directory.

---

# Catalogue

One entry per fixture: what it falsifies, the construction, and the
boundary resolution. The `.json` files are the machine source of truth.

## CE-A-DSTYLE-001 — A does not inherit D exchange-to-Voronoi theorem

**Status:** exact rational counterexample.

**Claim falsified:**

> The determinant-specific finite theorem extends to every smooth monotone matrix criterion — in particular, for the A criterion \(-\operatorname{tr}(I_q^{-1})\), a relocation with strictly positive first-order \(I_q^{-2}\) Mahalanobis margin must not decrease the exact objective.

\(N=6\), \(d=2\), \(K=3\), integer scores centered exactly, uniform weights.
Moving row 2 from cell 1 to cell 0 has first-order margin \(567/20 > 0\)
(the D-style screening says "must improve"), yet \(\operatorname{tr}(I_q^{-1})\)
rises from \(81/10\) to \(1512/125\) — exact A gain \(-999/250\). The log-det
coincidence that powers the D theorem does not survive replacing
\(\log\det\) by \(-\operatorname{tr}(I^{-1})\).

**Fixture:** `CE-A-DSTYLE-001.json`.

---

## CE-D-LLOYD-001 — adaptive D-Mahalanobis Lloyd can decrease log-det

**Status:** exact rational counterexample.

**Claim falsified:**

> Reassigning all points to their nearest current centroids under \(I_q^{-1}\), then recomputing centroids, monotonically increases \(\log\det I_q\).

**Reason the proof attempt fails:**

\[
\log\det J
\le
\log\det I
+
\operatorname{tr}(I^{-1}(J-I)).
\]

The tangent is an upper bound, so improvement of the fixed-metric trace surrogate is not a minorize-maximize step for log-det.

Eight exact-decimal rows in \(d=2\), uniform weights \(1/8\), \(K=3\), initial
labels \((1,0,0,1,2,2,2,1)\). The batch adaptive-Mahalanobis step (argmin
decided in exact rational arithmetic) relabels to \((0,0,1,1,2,1,0,1)\) and the
exact determinant strictly drops; the log-det decrease is \(\approx 0.136521\)
nat.

**Fixture:** `CE-D-LLOYD-001.json`.
**Regression:** `tests/test_research_claims.py::test_adaptive_mahalanobis_lloyd_step_can_decrease_d_objective`.

---

## CE-D-UNMERGED-DUPLICATES-001 — split duplicate atoms block strict D-Voronoi closure

**Status:** exact rational boundary counterexample.

**Claim falsified:**

> One-point exchange stability implies strict self-consistent nearest-centroid
> assignment even when coincident positive-weight score atoms may be assigned
> to different cells.

Take scalar scores \((1,1,-1)\), weights \((1/4,1/4,1/2)\), and put each row in
one of \(K=3\) singleton cells. Then \(I_q=1\), all cells are nonempty, and no
nonempty-preserving relocation exists. The labeling is therefore vacuously
exchange stable. The first two centroids coincide, however, so strict assignment
fails and no deterministic score-only rule can reproduce the split labels.

**Boundary resolution:** merge coincident score atoms before optimization, or
require labels to be constant on each duplicate class. The audited theorem then
forces distinct centroids and strict assignment.

**Fixture:** `CE-D-UNMERGED-DUPLICATES-001.json`.

---

## CE-D-VORONOI-CONVERSE-001 — D-Voronoi fixed does not imply exchange stable

**Status:** project negative result.

**Claim falsified:**

> Every self-consistent \(I_q^{-1}\)-Voronoi finite partition is one-point exchange stable.

The proven/project direction is the reverse:

\[
\text{exchange stable}
\Rightarrow
\text{strict D-Voronoi}.
\]

**Status:** exact rational counterexample, minimal (\(N=4\), \(d=1\), \(K=2\)).

Centered scalar scores \((-3/4,-3/4,1/4,5/4)\), uniform weights, labels
\((0,0,0,1)\). Every row is strictly nearest its own centroid (cell centroids
\(-5/12\) and \(5/4\)), so the partition is a strict self-consistent D-Voronoi
partition; yet relocating row 2 to cell 1 raises \(I_q\) from \(25/48\) to
\(9/16\). Voronoi fixed therefore does not imply one-point exchange stable.

**Fixture:** `CE-D-VORONOI-CONVERSE-001.json`.

---

## CE-DS-DEGENERATE-GLOBAL-TIE-001 — a finite global \(D_s\) optimum can be a 31-fold exact tie class with coincident projected centroids

**Status:** exact rational counterexample (exhaustive enumeration).

**Claim falsified:**

> An exact finite global profiled-\(D_s\) optimum is unique up to label
> permutation, keeps its efficient-projected centroids pairwise separated, and
> — when it has zero first-order violations — is reproducible from its own
> efficient-semimetric nearest-cell rule.

A centered equal-weight \(N=8,d=2,d_\psi=1,K=3\) sample (drawn from a
correlated Gaussian and rounded to exact eighths) whose global in-bin optimum
\(1083/4096\) is attained by exactly 31 labelings — the feasible refinements
of one reduced bipartition. Every tied optimum has two exactly coincident
projected centroids, so no efficient-semimetric rule separates them; the
unique nuisance-mean-equal refinement is infeasible (singular nuisance block)
with generalized pseudo-inverse value \(1191/4096\) **above** the feasible
optimum, showing the pseudo-inverse extension leaves the in-bin statistical
formulation. Theory: `KNOWN_RESULTS/05b-ds-bridge.md` DS11(c–d).

**Fixture:** `CE-DS-DEGENERATE-GLOBAL-TIE-001.json`.

---

## CE-DS-MARGINS-RANK-VACUITY-001 — at \(K=d_\lambda+1\) every feasible labeling has profiled value exactly zero

**Status:** exact rational boundary counterexample (exhaustive enumeration; the
mechanism is a two-line rank argument, universal over samples).

**Claim falsified:**

> DS15's margins dichotomy as first registered for general nuisance dimension
> under the bare cardinality assumption \(K\ge3\): conclusion (i) — value
> convergence to the positive unrestricted supremum \(v_K\) — for
> \(d_\lambda\ge2\) with \(K=d_\lambda+1\).

Exact centering gives \(\sum_b m_b=0\), so \(\operatorname{rank}(I_z)\le K-1\);
when the \(d_\lambda\times d_\lambda\) binned nuisance block is nonsingular
with \(d_\lambda=K-1\), Schur rank additivity forces the profiled value to be
exactly zero — for **every** sample and every feasible labeling. The minimized
witness (\(N=4\), integer scores with zero column sums, \(d_\lambda=2\),
\(K=3\)) has all six feasible labelings at value \(0\), efficient-score
interval optimum \(81/50>0\), and \(K=4=d_\lambda+2\) value \(9/5>0\) on the
same atoms. Hence the dichotomy needs \(K\ge d_\lambda+2\); at
\(d_\lambda=1\) that is exactly the recorded \(K\ge3\). Theory:
`KNOWN_RESULTS/05b-ds-bridge.md` DS15 (audited scope) and DS9/FI-RANK-CEILING.

**Fixture:** `CE-DS-MARGINS-RANK-VACUITY-001.json`.

---

## CE-DS-GLOBAL-GEOMETRY-001 / -002 — exact finite \(D_s\) geometry can fail

**Status:** two independent exact rational counterexamples for the same claim.

**Claim falsified:**

> A finite globally optimal or one-point exchange-stable \(D_s\) partition must assign each point according to the naive first-order efficient-score/common-metric rule.

**Known conclusion:** false in general.

- `CE-DS-GLOBAL-GEOMETRY-001.json` — the canonical fixture harvested from the
  26 Aug 2026 manuscript (\(N=8\), 966 partitions, optimum \(6241/984\),
  runner-up \(4232/669\)).
- `CE-DS-GLOBAL-GEOMETRY-002.json` — the independent witness pinned by the CI
  regression test (\(N=8\), optimum \(20449/1920\), margin to second best
  \(2929/21120\), row 6 violates its own efficient-semimetric rule by exactly
  \(8/195\)).
  **Regression:** `tests/test_research_claims.py::test_global_profiled_ds_partition_can_violate_its_own_metric_rule`.

The two instances are unrelated data sets; keep both and do not conflate them.

---

## CE-DS-POP-WASTED-CELLS-001 — population-stationary \(D_s\) partitions can defeat every efficient-semimetric rule

**Status:** exact rational construction (symmetric quadrature verification).

**Claim falsified:**

> A first-order stationary population profiled-\(D_s\) quantizer has
> pairwise-distinct efficient-projected centroids, so its cells can always be
> recovered from a common efficient-semimetric nearest-cell rule.

Under a nuisance-sign-symmetric law, a \(\psi\)-threshold partition with each
side split by \(\operatorname{sign}(s_\lambda)\) (K=4) is exactly stationary
(zero violations, ties allowed), its two extra cells add nuisance information
\(9/4\) but exactly zero profiled information, and its projected centroids
coincide pairwise — while its K=2 coarsening has an exactly singular binned
nuisance block. The symmetry argument applies verbatim to any
nuisance-sign-symmetric atomless law. Theory: `KNOWN_RESULTS/05b-ds-bridge.md` DS12.

**Fixture:** `CE-DS-POP-WASTED-CELLS-001.json`.

---

## CE-E-GEOMETRY-001 — naive E fixed-gradient rule fails

**Status:** project negative result.

**Claim falsified:**

> Choose one projector onto a minimum-eigenvalue eigenvector; every finite E-optimal partition is pointwise optimal under that fixed quadratic metric.

Repeated minimum eigenvalues make the criterion nonsmooth and there is no canonical unique gradient. The stored instance is stronger: the minimum eigenvalue is **simple** (spectral gap \(\approx 0.068\)) and the rank-one \(vv^\top\) rule still fails.

**Status:** float witness verified by exhaustive enumeration (high-precision, not exact-rational — eigenvalue computation).

\(N=8\), \(d=2\), \(K=3\), uniform weights. The unique global E optimum
\((0,1,1,2,0,0,0,1)\) has a simple minimum eigenvalue, yet row 7 is strictly
closer to cell 2 than to its own cell 1 under the \(vv^\top\) metric, with
margin \(\approx 0.068\).

**Fixture:** `CE-E-GEOMETRY-001.json`.
**Regression:** `tests/test_research_claims.py::test_global_e_partition_can_violate_simple_eigenvector_rule`.
**Next step:** test the stronger common-supergradient conjecture (`OPEN-E-COMMON-SUPERGRADIENT`).

---

## CE-DS-STABLE-MARGIN-RETAINING-001 — a non-global exchange-stable profiled-\(D_s\) labeling can retain macroscopic DS14 margins

**Status:** exact rational counterexample.

**Claim falsified:**

> One-point exchange stability forces the DS15 degeneracy on conditionally
> centered laws: every exchange-stable feasible profiled-\(D_s\) labeling is
> near the efficient-score interval supremum with a collapsing binned
> nuisance block, so the DS14 margin triple can never hold at a stable state.

An exactly centered \(N=8\), \(K=3\), \(d=2\) sample from the centered06 grid
law, equal weights \(1/8\), exact rational arithmetic throughout. The witness
labeling is one-point exchange-stable — all 16 admissible relocations have
exact profiled gain \(\le0\) — yet carries a macroscopic nuisance block
(\(I_{11}\approx0.523\)), conditioning lower bound
\(\det I/\operatorname{tr}I\ge0.1397\), minimum cell mass \(1/4\), and
projected-centroid separation \(\approx0.325\), at a \(7.7\%\) relative price
below the exact scalar efficient-score interval optimum \(v_K\). The exact
global optimum has a strictly larger profiled value but a nuisance block
(\(\approx0.131\)) four times smaller than the witness's: the optimizer's
value ranking is anti-aligned with the conditioning margin, the DS16 price
mechanism in exact form. Margin-retaining exchange-stable states exist at a
\(\Theta(1)\) information price, so the DS14 bridge's hypothesis set is
inhabited by non-global stable states and a margin-certified compile path is
not vacuous at finite \(N\); exchange stability does not preclude the DS14
margins, it prices them (DS16). Theory: `KNOWN_RESULTS/05b-ds-bridge.md`
DS16.

**Fixture:** `CE-DS-STABLE-MARGIN-RETAINING-001.json`.
**Regression:** `tests/test_research_claims.py::test_ds16_exchange_stable_state_can_retain_macroscopic_margins`.

---

## CE-DS-INTERVAL-SEED-UNSTABLE-001 — the efficient-score interval seed is not exchange-stable

**Status:** exact rational counterexample.

**Claim falsified:**

> The exact efficient-score interval labeling — the DP optimum of the
> full-sample efficient score, the documented initializer for profiled
> exchange and the finite analogue of DS15's degenerate attainer \(J^*\) —
> is itself one-point exchange-stable for the in-bin profiled-\(D_s\)
> objective.

An exactly centered \(N=8\), \(K=3\), \(d=2\) sample from the centered06 grid
law, equal weights \(1/8\), exact rational arithmetic throughout. Relocating
row 7 from the interval labeling's cell to cell 1 raises the profiled value
by exactly \(2335473863255583/5219865952157696\approx0.447\); the improving
move works by growing the binned nuisance block 27-fold
(\(1742559/419430400\approx0.0042\) to
\(46347881/419430400\approx0.111\)). Near the interval seed the projection
tax is the dominant term, so the profiled objective climbs by buying back
nuisance information — the finite mechanism behind DS15 Proposition 6's
steering. The documented profiled initializer is therefore generally not a
terminal state: seeding inside the DS15 degeneracy does not mean returning
it, so the optimizer's output is a genuinely different object from the
projected rule. Theory: `KNOWN_RESULTS/05b-ds-bridge.md` DS16.

**Fixture:** `CE-DS-INTERVAL-SEED-UNSTABLE-001.json`.
**Regression:** `tests/test_research_claims.py::test_ds16_efficient_score_interval_seed_is_not_exchange_stable`.

---

## CE-DS-LCM-SIGNSPLIT-MARGIN-001 — a wasted-cell K=3 state can carry full-rank margins with zero projected-centroid separation

**Status:** exact rational counterexample (population_quantizer level; boundary counterexample of DS17).

**Claim falsified:**

> The DS17 linear-conditional-mean obstruction extends to the (M5)-free
> margin pair: on an LCM law every bounded-packet stationary K=3
> configuration with positive cell masses has a rank-deficient binned
> information matrix, so the conditioning margin (M3) alone already empties
> the stationary class.

The K=3 sign-split sibling of CE-DS-POP-WASTED-CELLS-001, on the same
8-atom nuisance-sign-symmetric law: the left half \(\{s_\psi<0\}\) is split
by \(\operatorname{sign}(s_\lambda)\) into cells A and B, and the right half
\(\{s_\psi\ge0\}\) is left as one cell C. The binned information is full
rank, \(I_q=\operatorname{diag}(4,9/8)\), with minimum cell mass \(1/4\);
the projected centroids are \((-2,-2,2)\) — cells A and B coincide exactly,
zero separation — yet every atom satisfies the nearest-projected-centroid
stationarity rule with zero first-order violations (ties allowed). Merging
the coincident pair collapses to the K=2 \(s_\psi\)-threshold rule, whose
nuisance block is exactly singular: the compilable reduction carries no
margin. The continuous counterpart on \(N(0,I_2)\) — any zero-mean
measurable nuisance split of one threshold cell — is stationary with
\(I_q=\operatorname{diag}(2/\pi,1/\pi)\) and profiled value exactly
\(v_2=2/\pi\). Theory: `KNOWN_RESULTS/05b-ds-bridge.md` DS17.

(M5) is load-bearing for the DS17 obstruction: without separation, margins
survive only in wasted-cell configurations whose compilable reductions
carry no margin.

**Fixture:** `CE-DS-LCM-SIGNSPLIT-MARGIN-001.json`.
**Regression:** `tests/test_research_claims.py::test_ds17_signsplit_stationary_state_retains_margins_without_separation`.

---

## CE-DS-LCM-SIGNSPLIT-MINIMAL-001 — support-minimal atomic sign-split boundary

**Status:** exact rational boundary witness; no DS17 claim is falsified.

Three equally weighted atoms
\((-1,1),(-1,-1),(2,0)\), one per cell, are exactly centered and give

\[
I_q=\operatorname{diag}(2,2/3),\qquad B_q^*=0,
\]

with projected centroids \((-1,-1,2)\). Thus the first two cells coincide in
projection while the fine information remains full rank; merging them leaves
the two-cell POI-threshold rule with nuisance block exactly zero. This is
support-minimal for a three-cell construction because \(N=K=3\).

This fixture is deliberately **not** a counterexample to DS17. The law is
atomic, so atomlessness and (M4) fail; projected separation is zero, so (M5)
fails; and every cell is a singleton, so there is no admissible
nonempty-preserving one-point relocation and finite exchange stability is
packet-vacuous. It records only the smallest exact algebraic instance of the
wasted-cell/sign-split boundary.

**Fixture:** `CE-DS-LCM-SIGNSPLIT-MINIMAL-001.json`.

---

## CE-DS-NONCENTERED-POPULATION-CUT-UNSTABLE-001 — an exact population rule need not label a finite terminal

**Status:** exact rational boundary counterexample, support-minimal for a
nonempty-preserving move at (K=3).

For the off-((L)) law (S=(X,3X^2-1+Z)), take
(X=(-3/4,-1/4,1/4,3/4)) and (Z=(-1,-3/4,1,1)), with equal weights.
The population cuts (pm1/3) give labels ((0,1,1,2)) and profiled value
(363/2656). Moving row 2 from the middle to the right cell gives labels
((0,1,2,2)), value (49/352), and exact positive gain (37/14608).

This falsifies the tempting finite shortcut “label by the population rule and
the result is already exchange-stable.” It does **not** challenge the
almost-sure transfer through finite global optima: the post-move state is the
global optimum of this table, and (N=4) is the smallest sample with three
occupied cells and an admissible move.

**Fixture:** `CE-DS-NONCENTERED-POPULATION-CUT-UNSTABLE-001.json`.
**Regression:**
`tests/test_research_claims.py::test_ds18_population_cut_labels_need_not_be_exchange_stable`.
**Regression:** `tests/test_research_claims.py::test_ds17_minimal_atomic_signsplit_is_only_a_boundary_witness`.

---

## CE-DS-NONCENTERED-SINGULAR-DESTINATION-001 — a singular one-point destination beats the regular optimum

**Status:** exact rational boundary counterexample (exhaustive enumeration),
support-minimal at \(N=4\); a *convention* boundary, not a DS18 refutation.

**Claim falsified:**

> An exact global optimum over regular (nonsingular-nuisance) finite labelings
> is one-point exchange-stable under any feasibility convention, so DS18.2's
> finite stability step needs no convention.

Four rows on the named off-((L)) law's support, exactly centered:
\(X=(-1,0,\tfrac12,\tfrac12)\), \(Z=(-1,1,-\tfrac34,\tfrac14)\), giving
\(S=[(-1,1),(0,0),(\tfrac12,-1),(\tfrac12,0)]\) with equal weights. The exact
global optimum over regular labelings is \(1/12\), attained by exactly two
labelings, \((0,0,1,2)\) and \((0,1,1,2)\). The single labeling with an exactly
zero binned nuisance block, \((0,1,0,2)\), has
\(\hat I=\bigl[\begin{smallmatrix}3/32&0\\0&0\end{smallmatrix}\bigr]\) and DS11
pseudo-inverse value \(3/32\) — and **both** global regular optima reach it by
one source-nonempty relocation with exact gain \(3/32-1/12=1/96>0\), while
every other admissible move is non-improving.

**Boundary resolution:** at \(d_\lambda=1\) a zero binned nuisance block forces
every cell \(\lambda\)-sum to vanish, hence \(\sum_iS_{\lambda,i}=0\), an event
of probability zero under the named continuous law. Almost surely every
three-nonempty-cell labeling is regular, so this table cannot occur and DS18.2
is untouched. What it fixes is the *statement*: the in-bin (DS9) feasibility
convention — singular destinations are infeasible — is load-bearing and must be
named, because the pseudo-inverse convention reverses the conclusion at the
smallest support where any relocation exists. Distinct from
`CE-DS-DEGENERATE-GLOBAL-TIE-001`, which compares values at \(N=8\); this one
is an admissible one-point move from every global optimum.

**Fixture:** `CE-DS-NONCENTERED-SINGULAR-DESTINATION-001.json`.
**Regression:**
`tests/test_research_claims.py::test_ds18_singular_destination_beats_the_regular_optimum`.
**Audit:** `AUDITS/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001.md` §8.4, §15.

---

## CE-DS-TILT-DUAL-GAP-001 — the scalar tilt dual can stay macroscopically open

**Status:** exact rational counterexample, support-minimal at (N=4,K=3).

All six nonempty partitions of the equal-weight table

\[
(-11/2,39/8),\ (3/2,-65/8),\ (7/2,31/8),\ (9/2,-49/8)
\]

are nuisance-regular, so the in-bin and pseudo-inverse comparison domains
coincide. Exhaustion gives global profiled value (116805/11816). An exact
convex mixture of the tilt quadratics for labels ((0,0,1,2)) and
((0,1,2,2)) lower-bounds the dual by (61717893/5839400), leaving gap at
least (105329256/154014175>0.68). Adding bounded rational atoms with
vanishing total mass extends the witness to a positive-weight
(Theta(1))-gap family without assuming that unrestricted duplicate rows
must share labels.

**Fixture:** `CE-DS-TILT-DUAL-GAP-001.json`.
**Regression:**
`tests/test_research_claims.py::test_ds19_tilt_dual_has_a_support_minimal_exact_positive_gap`.

---

## CE-DS-MATRIX-TILT-NONQUASICONVEX-001 — the matrix-tilt outer map is not quasiconvex

**Status:** exact rational counterexample for Tier B.

For the centered equal-weight rows ({\pm2e_j:j=1,\ldots,4}), split two
coordinates as POI and two as nuisance and take (K=N=8). The unique
singleton partition gives (V(B)=I_2+BB^\top). At
(B_0=\operatorname{diag}(4,0)), (B_1=\operatorname{diag}(0,4)), and their
midpoint (operatorname{diag}(2,2)), the exact determinants are (17,17,25).
The midpoint therefore exceeds both endpoints, violating quasiconvexity and,
a fortiori, convexity.

**Fixture:** `CE-DS-MATRIX-TILT-NONQUASICONVEX-001.json`.
**Regression:**
`tests/test_research_claims.py::test_ds19_matrix_tilt_outer_map_is_not_quasiconvex`.

---
