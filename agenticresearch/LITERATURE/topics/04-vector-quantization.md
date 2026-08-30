# 4. Vector quantization and Voronoi theory

> Curated theorem-level annotations. Machine records for the citation graph
> live in `graph.json`; `BIBLIOGRAPHY.md` (generated) maps every registry
> bibliography key to the heading that annotates it.

## Pollard (1981, 1982) and the k-means consistency cluster

**Key:** Pollard-1981

**Papers:** *Strong Consistency of K-Means Clustering* (Ann. Statist. 9:135–140);
*A Central Limit Theorem for k-Means Clustering* (Ann. Probab. 10:919–926);
*Quantization and the Method of k-Means* (IEEE IT 28:199–205).
Refinements: Abaya & Wise (1984, SIAM J. Appl. Math. 44:183–189, optimal
quantizers under weakly converging sources); Sverdrup-Thygeson (1981, Ann.
Statist. 9:141–145); Cuesta-Albertos & Matrán (1988, PTRF 78:523–534);
Lember (2003, J. Approx. Theory 120:20–35, minimizing sequences /
non-unique optima); Linder (2000, CISM 464 survey, VC/covering-number
finite-sample bounds).

**Use (triangulated 28 Aug 2026 for the DS14 bridge):** the two-step "uniform
LLN over configuration classes + argmin continuity" skeleton is the direct
template for DS14 Steps 3–5; Lember/Abaya–Wise handle non-unique optima
(needed for the Ds tie degeneracy DS11(c)).

**Does not transfer:** every member assumes a fixed source-independent metric
and per-point additive distortion; none covers a solution-dependent
semimetric (the fitted \(G_s\)) or a determinant/Schur functional of
aggregated cell moments; center-convergence uniqueness conditions have no
log-det analogue.

- DOI: https://doi.org/10.1214/aos/1176345339

## Graf & Luschgy (2000, 2002)

**Key:** Graf-Luschgy-2000

**Papers:** *Foundations of Quantization for Probability Distributions*
(Springer LNM 1730; Ch. 4 existence/stationarity of optimal quantizers under
moment conditions); *Rates of convergence for the empirical quantization
error* (Ann. Probab. 30:874–897; bracketing-entropy uniform LLN over
Voronoi-cell indicator classes).

**Use:** nearest published instance of a uniform LLN over Voronoi-type
partition classes (DS14 Step 3 companion to C1) and of
existence/stationarity machinery for population quantizers. Thm 4.1/4.2
(secondary-verified via Levrard and Liu–Pagès): every cell of an optimal
quantizer carries positive mass with null overlaps — the population (M2)
analogue on the distortion side, and the deletion-vs-\(W_{K-1}\) mechanism
reused in DS15's rigidity lemma. Thm 5.1: scalar log-concave uniqueness (the
book anchor for DS15's assumption (S)).

**Does not transfer:** the whole framework is additive per-point distortion;
no result covers a global nonlinear matrix functional of cell moments.

## Sabin & Gray (1986)

**Paper:** *Global convergence and empirical consistency of the generalized
Lloyd algorithm* (IEEE IT 32:148–155).

**Use:** closest structural precedent for the DS14 bridge shape — set
convergence of empirical *fixed-point* (locally certified, not globally
optimal) quantizers to the population fixed-point set, for convex additive
distortions.

**Does not transfer:** ordinary nearest-neighbor fixed points under a
source-independent convex cost; no margin/rate analysis; no
Schur-complement self-consistency.

## Set-valued M-estimation / epi-convergence templates

**Sources:** van der Vaart & Wellner (1996, Thm. 3.2.2 argmax theorem);
Rockafellar & Wets, *Variational Analysis* (1998, Ch. 7 epi-convergence:
inf-value convergence + cluster points of minimizers are minimizers);
Royset & Wets (2020, Ann. Statist. 48:2759–2790, constrained M-estimators
with set-valued minimizers); Molchanov, *Theory of Random Sets* (2005/2017,
argmin sets as random closed sets).

**Use:** abstract shell for "empirical optimizer set converges to population
optimizer set" that is agnostic to additivity and metric structure; the
right vocabulary for the exchange-stable solution *set*.

**Does not transfer:** supplies no concrete entropy or margin estimates for
partition classes — those come from C1/Graf–Luschgy-style VC arguments.

## Margin conditions in quantization

**Key:** Levrard-2015

**Sources:** Levrard (2015, Ann. Statist. 43:592–619, k-means margin
condition bounding mass near optimal cell boundaries, fast rates; survey
2018 J. SFdS 159:1–48); Mammen & Tsybakov (1999, Ann. Statist.
27:1808–1829); Antos, Györfi & György (2005, individual rates).

**Use:** conceptual template for the DS14 slab-margin assumption (M4) and
for a future fast-rate refinement of the bridge. Levrard's \(p_{\min}\)
(mass) and \(B\) (separation) are the published codification of what
(M2)/(M5) buy; their positivity at population optima is inherited from
Graf–Luschgy, never assumed of empirical optima.

**Does not transfer:** fast-rate mechanics rely on a Pythagorean identity for
squared Euclidean distortion with no known log-det/Schur analogue; the
margin condition is a hypothesis on the law, never proven automatic.

## Scalar quantizer uniqueness (log-concave laws)

**Key:** Kieffer-1983, Liu-Pages-2020, Mease-Nair-2006

**Sources:** Kieffer (1983, IEEE IT 29:42–47): log-concave density + convex,
strictly increasing, \(C^1\) error weight ⟹ the locally optimal \(K\)-level
scalar quantizer is unique, hence globally optimal, and Lloyd iterations
converge to it (secondary-verified via Kazıklı–Sarıtaş–Gezici–Linder–Yüksel,
arXiv:2012.08265, Thm 3, and Liu & Pagès, JMLR 21(86), Lemma 10). Fleischer
(1964, IEEE Conv. Rec. 12:104–111, verbatim): strict log-concavity ⟹ unique
stationary point of the \(N\)-level MSE quantizer; Gaussian, Laplacian,
Rayleigh covered explicitly. Trushkin (1982, IEEE IT 28:187–198): convex
error weights (hypotheses unverified, cited by Liu–Pagès). Liu & Pagès
Prop 11: strictly log-concave density ⟹ positive-definite distortion Hessian
at the optimum — a published population-level conditioning statement at the
scalar optimum. Mease & Nair (2006, Statistica Sinica 16:1299–1312,
verbatim, 30 Aug 2026 audit): uniqueness under log-concavity of the density
via likelihood-ratio ordering — and an explicit counterexample refuting
Eubank (1988)'s weaker sufficient condition (log-concavity of
\(f(F^{-1}(u))\)): a spliced exponential/Weibull density with three
stationary solutions. **Boundary for (S): the assumption must stay pinned to
log-concavity of the density itself; Eubank-type weakenings are
known-broken.**

**Use:** DS15's assumption (S) — uniqueness of the optimal efficient-score
interval quantizer — holds for Gaussian efficient scores by any of these;
with Pollard (1981) this makes the population→empirical transfer of the
scalar optimum fully rigorous in one dimension.

**Does not transfer:** one-dimensional and distortion-side only; uniqueness
for \(d_\psi>1\) fails in general (rotational symmetry), which is exactly why
DS15 is stated for \(d_\psi=1\).

## Scalar grouping and 1-D contiguity (30 Aug 2026)

**Key:** Fisher-1958

**Sources:** W. D. Fisher (1958, JASA 53:789–798, verbatim): optimal
one-dimensional weighted least-squares partitions are contiguous in the
sorted order (appendix proof), reducing the search to
\(\binom{K-1}{G-1}\) contiguous partitions; credits the
continuous-distribution analogue to Dalenius (1950) and Cox (1957). Bellman
(1961, CACM 4:284): dynamic programming for segmented least squares — the
exact-DP citation. Wang & Song (2011, R Journal 3(2):29–33):
`Ckmeans.1d.dp`, modern guaranteed-optimal 1-D DP.

**Use:** the classical anchors for DS8 (scalar efficient-score DP) and the
\(\mathrm{btw}\le\hat v_K\) leg of DS15's Proposition 4; the DS15 audit
verified contiguity against full partition lattices, including duplicate
values and unequal weights.

**Does not transfer:** one-dimensional SSE only; nothing about matrix
criteria or feasibility constraints.

## Constraint-restored consistency of empirical clustering (30 Aug 2026)

**Key:** Blanchard-Jaffe-Zhivotovskiy-2025

**Sources:** Blanchard, Jaffe & Zhivotovskiy (arXiv:2507.06226, abstract):
under only a finite first moment, empirical k-means centers can fail to
converge even when the population optimum is unique — the failure mode is
extreme cluster imbalance — and an a priori balance (minimum-size)
constraint restores consistency. Kanungo et al. (2004, Comput. Geom.
28:89–112): single-swap local search with bounded worst-case cost. Bradley,
Bennett & Demiriz (2000, MSR TR-2000-65): minimum-cluster-size constrained
assignment via network flow.

**Use:** the closest published *structure* to DS15's Proposition 6 —
constraints imposed at asymptotically negligible cost — and the reference to
engage before any publication of the steering construction.

**Does not transfer:** their constraint repairs a moment pathology of the
scalar-distortion objective; DS15's margin fights the profiled criterion's
own drive to nuisance degeneracy, and no published theorem provides
swap-steering to a side constraint at \(\tilde O(N^{-3/4})\) cost.

## Outlier and singleton cells at exact clustering optima

**Key:** Garcia-Escudero-Gordaliza-1999, Hennig-2004

**Sources:** García-Escudero & Gordaliza (1999, JASA 94:956–969): generalized
\(k\)-means are non-robust — contamination drives a cluster to chase an
outlier; trimming repairs it. Hennig (2004, Ann. Statist. 32:1313–1340;
restated verbatim in arXiv:2308.14478): adding a single far-enough point to a
fixed-\(K\) ML clustering makes the exact optimum give the outlier a
one-point cluster and merge two original clusters. Georgogiannis (NeurIPS
2016): universal breakdown points 1/n–2/n for robust \(k\)-means variants.

**Use:** the published record of the finite-sample singleton phenomenon at
exact optima — the qualitative shape of the \(N\le18\) evidence
(N-DS-BRIDGE-TREND). Hennig also supplies the normative point that one-point
clusters are a modeling choice, not an invalidity.

**Does not transfer:** all statements are adversarial-contamination
("there exists a modification"), not i.i.d. extreme-value asymptotics; none
quantifies when the sample's own maximum earns a singleton, and for
distortion criteria the singleton is a failure mode where for \(D_s\) it is
objective-rewarded. The i.i.d. extreme-cell question itself is a confirmed
search gap (29 Aug 2026, OP28 audit): no published result addresses whether
exact optimal partitions of an i.i.d. sample isolate extreme points, under
any criterion. Resolved for \(D_s\) by DS15: they do not, asymptotically —
min cell mass at exact scalar optima converges to the positive population
masses (N-DS-SCALAR-MASS).

## Determinant-criterion consistency — confirmed search gap (28 Aug 2026)

Targeted triangulation found **no published consistency theory, at any rate,
for D- or \(D_s\)-type (determinant/Schur) partition criteria estimated from
i.i.d. samples** — neither in the sequential/asymptotic optimal-design
literature (fixed or regression-design point sets, not sampled partitions)
nor in determinant clustering (Friedman–Rubin line: algorithms only). DS14
appears to be the first such bridge; recorded as a search gap, not a novelty
claim.

## Du, Faber & Gunzburger (1999)

**Key:** Du-Faber-Gunzburger-1999

**Paper:** *Centroidal Voronoi Tessellations: Applications and Algorithms*  
**Use:** CVT theory, Lloyd algorithm, geometric quantization.

- DOI: https://doi.org/10.1137/S0036144599352836

## Du, Emelianenko & Ju (2006)

**Paper:** *Convergence of the Lloyd Algorithm for Computing Centroidal Voronoi Tessellations*  
**Use:** convergence methods and assumptions for Lloyd/CVT.

- DOI: https://doi.org/10.1137/040617364

## Richter & Alexa (2015)

**Key:** Richter-Alexa-2015

**Paper:** *Mahalanobis centroidal Voronoi tessellations*  
**Use:** adjacent common/anisotropic metric Voronoi geometry.

- DOI: https://doi.org/10.1016/j.cag.2014.09.009

## Bregman Voronoi / quantization literature

**Use:** generalized centroid/dual-space geometry and local distortion approximations.

**Caution:** ScoreQuant D objective is global/nonadditive, so Bregman/CVT results do not transfer automatically.

---
