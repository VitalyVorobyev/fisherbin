# Research plan — goal, session model, and roadmap

**Version:** 1.1 · 28 August 2026
**Status:** canonical narrative. The executable priority queue lives in
`OPEN_PROBLEMS.md` (eight programmes P1–P8); this file holds the goal, the
session model, and the roadmap rationale. On any priority conflict,
`OPEN_PROBLEMS.md` wins.

ScoreQuant research is organized around **one scientific question**, not
around a collection of individual theorems.

## Session status ledger (28 August 2026)

The twelve sessions below were drafted before the product-first decision and
before the first audit completed. Current state:

| Session | State | Where |
|---|---|---|
| 1 — freeze the problem | **done** | `PROBLEM.md` |
| 2 — finite D audit | **done** | `AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md`, `WORK/completed/` |
| 3 — population D geometry | open | programme P6 (OP8/OP9 context) |
| 4 — finite ↔ population D | open | programme P6 (OP8, OP9) |
| 5 — solver theory | **largely embodied** | claims D5/D6, library `partition.py`, ADR-0014; residuals → P7 (OP12) |
| 6 — global optimization/certification | **partially done** | library `certify.py`; residuals → P7 (OP11, OP13) |
| 7 — empirical advantage over k-means | open | programme P6 |
| 8 — \(D_s\) as a separate theory | open, **promoted to "Now"** | programme P1, packet `WORK/active/DS-POPULATION-BRIDGE.md` |
| 9 — HEP mixture specialization | open | programme P5 (OP20–OP22) |
| 10 — learned score / ratio oracle | open, **promoted to "Now"** | programme P2, packet `WORK/active/SCORE-ORACLE-ROBUSTNESS.md` |
| 11 — information loss vs systematics | open | programmes P3/P5 |
| 12 — synthesis and novelty audit | **deferred** until the publication decision | programme P8 note |

**Why the reorder (product-first decision, 28 Aug 2026):** this research is
attached to a shipping library, not free-standing. The library hard-refuses
profiled compilation today (Session 8's theorem is the blocker), and every
real dataset already runs through an estimated score (Session 10's gap). Those
are the two theorems users are waiting on, so they move from "Later" to "Now";
the D-core paper sessions (3, 4, 7) stay queued as programme P6 but no longer
gate everything else. The paper is harvested from the ledger when its spine
completes — it is a by-product, not the driver.

## Natural top-level research goal

> **Develop a rigorous theory and practical methodology for constructing deployable hard partitions of statistical score space that retain as much information as possible for parameter inference, with particular emphasis on full-matrix D-optimality and nuisance-aware inference.**

More concretely, the project should answer:

> Given a statistical experiment and only \(K\) allowed event categories, what partition should we use, how can we compute it, what information does it retain, and what can we prove about its geometry, optimality and deployment to unseen events?

I think this is the right level because it naturally contains all the things we have been investigating:

$$
X
\longrightarrow
s(X)
\longrightarrow
q(s)\in\{1,\dots,K\}
\longrightarrow
I_q
$$

and then asks four connected questions:

1. **Statistics:** What exactly is the Fisher information after quantization?
2. **Geometry:** What form must an optimal or locally optimal partition have?
3. **Optimization:** How do we find such a partition reliably?
4. **Deployment:** How do we turn a finite training sample into a deterministic rule for future observations?

The HEP use case is then an important specialization rather than the mathematical definition of the problem.

---

# What I think should be the central paper-level objective

For the first serious publication, I would make the scope narrower:

> **Establish the theory and algorithms of D-optimal hard score quantization, from exact finite-sample optimization to self-consistent population quantizers, and quantify its advantage over conventional trace/\(k\)-means quantization.**

That gives us a coherent story:

$$
\text{Fisher information}
\rightarrow
\text{D objective}
\rightarrow
\text{exact exchange}
\rightarrow
\text{geometry}
\rightarrow
\text{population quantizer}
\rightarrow
\text{algorithm}
\rightarrow
\text{benchmarks}.
$$

\(D_s\), classifier proxies, HEP mixtures, robustness, etc. remain closely connected, but they should not be allowed to prevent us from finishing this core.

---

# Research roadmap

I would use approximately **10 substantial research sessions**. A session is a coherent investigation that may touch many claim nodes. It is not "prove Lemma 4.3."

## Session 1 — Freeze the mathematical problem

**Question:** What exactly is ScoreQuant optimizing?

Settle permanently:

* score-space versus observation-space quantization;
* population versus empirical quantization;
* deterministic versus randomized quantizers;
* weighted finite samples;
* exact definition of

$$
I_q=\sum_b W_b\mu_b\mu_b^\top;
$$

* conditions for nonsingularity;
* invariances;
* minimum \(K\);
* trace objective versus D objective.

### Exit condition

We can write the formal problem statement without caveats that later change the feasible set.

This session should produce the canonical definitions against which every later theorem is checked.

---

## Session 2 — Publication-grade audit of finite D theory

This is basically the investigation you are doing now.

Audit as one coherent package:

* exact one-point move formula;
* determinant gain formula;
* leverage inequality;
* exchange-stability \(\Rightarrow\) Voronoi;
* ties;
* singleton cells;
* duplicate score atoms;
* converse failure.

The purpose isn't to generate more lemmas. It is to decide whether the **finite D structural theorem is solid**.

### Exit condition

Either:

> We have a publication-ready theorem characterizing every one-point D-exchange-stable solution geometrically,

or we know precisely what weaker theorem survives.

This is probably the single most important theoretical session.

---

## Session 3 — Understand population D-optimal geometry

This is conceptually distinct from finite exchange.

Main question:

> What can actually be proved about an optimal quantizer of a continuous score distribution?

Investigate:

* existence;
* first variation;
* necessary stationarity;
* common \(I_q^{-1}\) Mahalanobis metric;
* affine/Voronoi cells;
* boundary measure zero;
* purification;
* relationship between global optimum and stationary partitions;
* finite-sample \(\rightarrow\) population convergence.

A particularly important distinction is:

$$
\text{population optimum}
\Rightarrow
\text{stationary Voronoi}
$$

versus the much stronger and probably false statement that every stationary Voronoi solution is optimal.

### Exit condition

A precise population theorem with all regularity assumptions visible.

---

## Session 4 — Connect finite and population problems

This is where the project becomes a genuine **quantization method** rather than a sample clustering method.

Question:

> If we optimize on an empirical score sample, when does the resulting partition approximate a population-optimal deployable quantizer?

Study:

* empirical objective consistency;
* convergence of \(I_{\hat q}\);
* convergence of centroids/metrics;
* nonuniqueness and label symmetry;
* stability of cell boundaries;
* sample complexity, if tractable;
* what happens with score atoms.

This session may turn out to require serious empirical-process theory. It is perfectly acceptable if the result is partial.

### Exit condition

We can say exactly what statistical guarantee the learned quantizer has—or explicitly state that this remains open.

---

## Session 5 — Solver theory

Now ask:

> Given the structural results, what algorithm should users actually run?

Compare the meaningful alternatives:

* exact one-point exchange;
* self-consistent Mahalanobis-Voronoi iterations;
* guarded Lloyd-type iterations;
* direct centroid optimization;
* generic discrete optimization;
* multi-start methods.

Important questions include:

* monotonicity;
* termination;
* exchange stability;
* whether the final solution is necessarily deployable;
* whether a Voronoi representation can be reconstructed;
* computational complexity.

### Exit condition

One clearly recommended local solver with a theorem describing exactly what its terminal state guarantees.

Ideally something like:

$$
\text{algorithm terminates}
\Rightarrow
\text{exchange stable}
\Rightarrow
\text{self-consistent D-Voronoi}.
$$

That is a very strong software story if the theorem survives the audit.

---

## Session 6 — Global optimization and certification

This should be treated separately from the practical local solver.

Question:

> Can we know when we have the global optimum?

Investigate:

* exact enumeration via affine/Voronoi partitions;
* fixed-\((d,K)\) complexity;
* branch-and-bound;
* upper bounds from refinement;
* practical certificates;
* hardness when \(d\) or \(K\) varies;
* prior art in clustering/computational geometry.

### Exit condition

We know which of these claims are:

* rigorous;
* algorithmically useful;
* only theoretical;
* open.

This also makes small-instance exact benchmarking possible.

---

## Session 7 — Establish the empirical advantage over \(k\)-means

Only after the theoretical object is stable should we ask:

> Does D-optimal quantization actually produce meaningfully different and better partitions?

Benchmark on controlled distributions:

* isotropic Gaussian-like cases;
* strongly anisotropic score distributions;
* correlated directions;
* weakly informed parameter directions;
* mixtures;
* highly unequal local sensitivities.

Compare:

* whitened \(k\)-means / trace optimality;
* ordinary \(k\)-means;
* D-optimal local solver;
* exact global D optimum on small cases.

Metrics:

$$
\log\det I_q,
\qquad
\det(I_q)^{1/d},
\qquad
\lambda(I_q),
\qquad
I_{\rm full}-I_q.
$$

### Exit condition

We understand **when D differs from trace**, rather than merely showing that it sometimes wins on its own objective.

That is essential to answering "why should anybody care?"

---

# Then branch into the second research programme

At this point I would consider the core D paper substantially defined.

The next programme is nuisance-aware inference.

---

## Session 8 — \(D_s\) as a separate theory

Do not assume that anything from D carries over.

Formulate:

$$
\theta=(\psi,\eta),
$$

with parameters of interest \(\psi\) and nuisances \(\eta\), and the profiled/effective information

$$
I_{\psi\mid\eta}
=
I_{\psi\psi}
-
I_{\psi\eta}
I_{\eta\eta}^{-1}
I_{\eta\psi}.
$$

Then systematically investigate:

* exact finite moves;
* gradient;
* stationarity;
* geometry;
* exchange stability;
* counterexamples;
* whether a common metric exists.

We already have reasons to expect the D theorem does **not** transfer naively.

### Exit condition

A clean statement of what survives from D and what fundamentally breaks.

This could eventually be a second paper rather than an appendix.

---

## Session 9 — HEP linear-mixture specialization

Now specialize the abstract framework to the actual motivating inference model.

For mixture/template models such as

$$
p(x\mid\theta)
=
\sum_j \theta_j f_j(x),
$$

derive explicitly:

* the score;
* redundancy from normalization constraints;
* useful parameterizations;
* density-ratio representation;
* reference-component ratios;
* binned Fisher information;
* nuisance treatment.

A major practical result should be to show that we do not need all absolute densities.

For instance, choosing a reference component \(f_0\),

$$
r_j(x)=\frac{f_j(x)}{f_0(x)}
$$

may contain all information necessary to reconstruct the relevant score coordinates.

### Exit condition

The connection to a real multicomponent template fit is mathematically explicit rather than motivational prose.

---

## Session 10 — Learned score / density-ratio oracle

This should be a **measurement layer**, not a redefinition of the quantization problem.

Question:

> What happens when \(s(x)\) is not analytically available?

Investigate:

$$
x
\xrightarrow{\text{classifier / ratio estimator}}
\hat s(x)
\xrightarrow{\text{ScoreQuant}}
q(\hat s).
$$

Study:

* multiclass classifier probabilities;
* density-ratio estimation;
* calibration;
* score reconstruction;
* training/reference mismatch;
* error propagation from \(\hat s\) into \(I_q\);
* cross-validation / sample splitting.

### Exit condition

We know exactly what the library requires from a learned proxy and what guarantees are lost when the proxy is imperfect.

---

# A third programme is particularly important for HEP

## Session 11 — Information loss versus systematics gain

This may eventually be the strongest HEP motivation.

Binning deliberately loses statistical information:

$$
I_q \preceq I_{\rm full}.
$$

So the scientific question cannot merely be "maximize retained information."

The practically relevant question is closer to:

> How much statistical information do we sacrifice by using \(K\) robust categories, and what do we gain in systematic-error modelling and control?

Investigate:

* information retention versus \(K\);
* diminishing returns;
* coarse-bin stability;
* Monte-Carlo template uncertainty;
* nuisance modelling;
* calibration uncertainty;
* mismodeling sensitivity.

There may eventually be a combined objective, but I would **not invent one prematurely**.

First characterize the tradeoff.

---

# Session 12 — Synthesis and adversarial novelty audit

Only now ask:

> What is the actual research contribution?

Run an adversarial literature review against the final theorem set, not against early speculative claims.

Separate:

**Known**

* Fisher-information quantization;
* trace/\(k\)-means equivalence;
* optimal design;
* determinant clustering;
* vector quantization;
* inference-aware categorization.

**Possibly novel**

Whatever survives, for example:

* exact D relocation algebra;
* finite exchange \(\Rightarrow\) common-metric Voronoi;
* exact/certifiable D score quantization;
* finite-to-population connection.

### Exit condition

Every central statement in the manuscript is labelled:

> known / direct corollary / adaptation / apparently new / unresolved.

---

# What a normal research session should look like

I would make the unit of work approximately:

> **one substantial scientific question that can change our understanding of the project.**

Not one claim.

A session prompt should usually fit on one screen:

```text
RESEARCH GOAL
Determine whether finite one-point D stability really implies
self-consistent Mahalanobis-Voronoi geometry.

WHY IT MATTERS
This connects the strongest practical local optimizer to an
inductive partition usable for unseen events.

STARTING STATE
Relevant claims: [...]
Known formulas: [...]
Known counterexamples: [...]

INVESTIGATE
- attack assumptions
- derive independently
- search prior art
- run exact numerical falsification if useful

STOP WHEN
The theorem is proved, disproved, or reduced to a precise
unresolved condition.

UPDATE
All affected research artifacts.
```

The **agent is free to create twenty temporary subproblems internally**.

They do not become twenty project tasks.

(This one-screen prompt is the ancestor of the standing packet format in
`WORK/TEMPLATE.md`; new packets use the template.)

---

# Priority order (product-first, 28 August 2026)

The executable form of this ordering is the programme queue in
`OPEN_PROBLEMS.md`; this is the rationale.

**Now**

1. **P1 · DS-POPULATION-BRIDGE** — the finite→population profiled-\(D_s\)
   theory (was Session 8, "Later"). Unblocks the profiled compile bridge the
   library currently refuses.
2. **P2 · SCORE-ORACLE-ROBUSTNESS** — perturbation theory for estimated
   scores and classifier calibration (was Session 10). Turns reported
   retention into a number with an honest error story on real data.

**Then (product-facing theory)**

3. **P3 · INFORMATION-BUDGET** — sharp \(\eta_D(K)\), high-rate asymptotics,
   and the bins-for-target-efficiency inversion.
4. **P4 · DEPLOYMENT-ROBUSTNESS** — \(\theta_0\)-mismatch degradation,
   minimax/multi-reference design, retention error bars.
5. **P5 · HEP-SPECIALIZATION** — mixture parameterizations, count+shape,
   nuisance scalability (Session 9).

**Queued (the paper's spine, not blocking)**

6. **P6 · D-CORE-COMPLETION** — population D geometry, finite↔population D
   consistency, and the D-vs-k-means benchmark study (Sessions 3, 4, 7).

**Background**

7. **P7 · FOUNDATIONS** — why D is special, complexity/certificates,
   randomization limits.
8. **P8 · LITERATURE-GRAPH** — citation snowballing to saturation; the final
   claim-by-claim novelty audit (Session 12) waits for frozen theorem
   statements at the publication decision.

The important discipline is unchanged: **resist opening every interesting
mathematical branch simultaneously.** The programme queue is the enforcement
mechanism — a session executes one `WORK/active/` packet drawn from the
highest programme that is not blocked.

The clearest north-star sentence for the project is therefore:

> **Find and characterize the best deployable \(K\)-category compression of score information for statistical inference, and provide algorithms whose statistical and optimization guarantees are understood.**

That is broad enough to guide years of work, while the D-optimal programme gives us a concrete first research campaign.
