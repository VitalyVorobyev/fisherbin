# Independent prior-art audit: DS17 stable basins

**Claims:** `DS-STABLE-BASINS-CENTERED-OBSTRUCTION`,
`DS-STABLE-BASINS-LCM-CLASSIFICATION`,
`DS-STABLE-BASINS-FIXED-POINT-GATE`,
`DS-STABLE-BASINS-GATE-SCANS`  
**Date:** 31 August 2026  
**Mode:** independent audit literature round  
**Comparison only:** `LITERATURE/audits/DS-STABLE-BASINS-31-August-2026.md`  
**Search verdict:** exact-theorem search gap, with classical ingredients and one
claim-level structural predecessor requiring re-attribution

## 1. Frozen questions and independence

The search was run against the registered DS17 statements, not against the
researcher's novelty summary. It asked four separate questions:

1. Is the tilt-residual identity or its zero-residual interpretation already a
   standard efficient-score / least-favourable-direction normal equation?
2. Is the conditional covariance sign and, especially, its equality case a
   classical Chebyshev/association result?
3. Do principal-points or self-consistency theorems already force the LCM
   geometry claimed in DS17?
4. Does prior work combine an endogenous projection coefficient, hard interval
   cells, nuisance/profiled information, and empirical stable-state
   nonexistence?

The existing researcher round was used only after the independent search to
compare source coverage. Its negative conclusion was not imported.

## 2. Retrieval and primary-text record

- **Read from primary full text:** Flury (1990); Tarpey & Flury (1996);
  Esary, Proschan & Walkup (1967); Jakubowski (2021); Serinko & Babu
  (1992, already held as a primary-text review in the workspace and checked
  against the publisher record).
- **Classical monograph theorem cross-checked:** Bickel, Klaassen, Ritov &
  Wellner (1993), against the authors' bibliographic record, the existing DS
  population-bridge audit, and independent semiparametric sources using the
  same projection definition.
- **Exact theorem scope cross-checked, primary proof inaccessible:** Tarpey,
  Li & Flury (1995). Tarpey & Flury (1996) explicitly identifies its own
  Theorem 4.1 as the generalization of the 1995 finite-distinct-support result;
  later papers restate the 1995 Theorem 4.1 verbatim for principal points.
- **Abstract/theorem context screened, primary theorem inaccessible:** Tarpey
  & Loperfido (2015), the missed forward source.

No inaccessible proof is used to assert a technique transfer.

## 3. Query log

Thirty-six exact searches were issued. Punctuation and spelling variants were
collapsed only in this display.

### Efficient score / residual orthogonality (6)

1. `efficient score nuisance projection normal equation`
2. `least favourable direction orthogonality nuisance score`
3. `Bickel Klaassen Ritov Wellner efficient score projection nuisance tangent space`
4. `van der Vaart section 25.4 efficient score nuisance tangent projection`
5. `binned categorical efficient score Schur complement`
6. `profile likelihood information projection residual score finite partition`

### Chebyshev equality / association (8)

7. `Chebyshev integral inequality equality monotone covariance`
8. `covariance identity iid copy monotone function equality iff constant`
9. `conditional covariance monotone transform equality`
10. `Hoeffding covariance identity monotone functions equality condition`
11. `Association of Random Variables with Applications Esary Proschan Walkup`
12. `A complement to the Chebyshev integral inequality Jakubowski`
13. `FKG inequality quantization self-consistent points association`
14. `Chebyshev association conditional distribution equality step function`

### Principal points / self-consistency / LCM (12)

15. `Principal Points Flury 1990 primary text`
16. `Principal Points and Self-Consistent Points of Elliptical Distributions theorem`
17. `Tarpey Li Flury principal subspace theorem leading eigenvectors`
18. `Self-consistency a fundamental concept in statistics theorem 4.1`
19. `self-consistent points linear conditional means`
20. `principal subspace theorem conditional expectation`
21. `self-consistency degeneracy nonexistence`
22. `elliptical quantizer collinear centroids`
23. `Self-consistency and a generalized principal subspace theorem`
24. `Tarpey Loperfido generalized principal subspace theorem`
25. `principal points location mixtures spherical distributions`
26. `self-consistent patterns symmetric multivariate distributions`

### Lloyd gates / empirical nonregularity (6)

27. `parameter dependent Lloyd fixed point endogenous projection`
28. `self-consistent quantizer fixed point nonexistence`
29. `stationary interval quantizer root equation`
30. `bifurcation Lloyd stationary branches mixture distribution`
31. `Weak limit theorems univariate k-mean clustering nonregular condition`
32. `empirical k-means stationary points margin consistency`

### Exact-combination search (4)

33. `profiled Fisher hard quantization nuisance self-consistency`
34. `hard partition efficient score fixed point nonexistence`
35. `conditional mean orthogonality self-consistent quantizer nuisance information`
36. `exchange stable clustering population limit profiled Fisher`

## 4. Round counts

This audit is round 5 in `LITERATURE/graph.json`.

| Quantity | Count | Scope |
|---|---:|---|
| exact queries | 36 | the five families above |
| distinct scholarly candidates | 55 | title/DOI deduplicated visible first-page records |
| theorem-relevant sources | 9 | linked to at least one audited claim |
| primary texts deeply reviewed | 4 | newly/re-reviewed in this audit; Serinko–Babu retained from its existing primary review |
| new graph records | 5 | BKRW, Esary–Proschan–Walkup, Hastie–Stuetzle, Jakubowski, Tarpey–Loperfido |

This was a targeted bidirectional one-hop round, not a field-saturation claim.

## 5. Six-field triangulation

### 5.1 Bickel, Klaassen, Ritov & Wellner (1993)

**Key:** Bickel-Klaassen-Ritov-Wellner-1993

**Exact problem.** Efficient estimation of a finite-dimensional target in the
presence of nuisance tangent directions.  
**Exact result.** The efficient score is the (L^2) residual after projecting
the target score onto the nuisance tangent space; least-favourable directions
satisfy the corresponding orthogonality/normal equations. In a regular finite
parametric block this is the familiar score residual with Schur-complement
variance.  
**Objective.** Minimum regular asymptotic variance / semiparametric efficiency.  
**Feasible set.** Regular estimators and tangent/submodel directions, not hard
partitions.  
**What transfers.** The interpretation of
\(\widehat S=S_\psi-B^*S_\lambda\) and the zero cross-moment normal equation are
classical. The numerator in DS17.1a is a partition-specific instance of this
projection algebra.  
**What does not.** No binned \(B^*(I_q)\), step function \(h\), endogenous
\(\beta=B^*(I_q)\), hard-cell fixed point, or stable-state nonexistence.

### 5.2 Jakubowski (2021)

**Key:** Jakubowski-2021

**Exact problem.** Characterize equality in Chebyshev's monotone covariance
inequality for an arbitrary real random variable.  
**Exact result.** For nondecreasing \(f,g\) with existing covariance,
\(\operatorname{Cov}(f(X),g(X))=0\) iff \(f(X)\) or \(g(X)\) is a.s. constant.
The proof begins with the exact independent-copy identity

\[
2\operatorname{Cov}(f(X),g(X))
=E[(f(X)-f(X'))(g(X)-g(X'))].
\]

**Objective.** A covariance inequality and its equality case.  
**Feasible set.** A scalar probability law and integrable monotone transforms.  
**What transfers.** Conditional on \(\widehat s\), take one transform to be the
identity and the other to be \(h(\widehat s-\delta X)\), reversing sign when
needed. This is the precise classical equality mechanism used in DS17.1.  
**What does not.** The theorem does not prove existence of a regular
conditional distribution, cell-indicator measurability, conditional centering,
or zero binned nuisance information. Those deductions must remain explicit in
the DS17 proof.

### 5.3 Tarpey & Flury (1996)

**Exact problem.** Unify principal components, curves, points, variables, and
other summaries through random-vector self-consistency
\(E[X\mid Y]=Y\).  
**Exact result.** Theorem 4.1 assumes linear conditional means. If a
self-consistent \(Y\) has support spanning a \(q\)-dimensional subspace and is
measurable with respect to the orthogonal projection of \(X\) onto that span,
the span is generated by \(q\) covariance eigenvectors. They need not be the
leading \(q\).  
**Objective.** \(L^2\)/MSE approximation and fixed-point self-consistency.  
**Feasible set.** Random-vector summaries; finite self-consistent points are a
special case with Euclidean attraction regions.  
**What transfers.** This is direct prior art for the LCM principle that
self-consistency restricts support geometry to covariance eigenspaces. It is
closer to DS17.3 conclusion (1) than the researcher round acknowledged.  
**What does not.** Fixed Euclidean projection is not DS17's endogenous
efficient-score tilt. There is no profiled Fisher block, zero-nuisance-rank
theorem, reduced compilable rule, margin certificate, or empirical eventual
emptiness.

### 5.4 Tarpey, Li & Flury (1995)

**Exact problem.** Principal and self-consistent finite point sets of centered
elliptical distributions.  
**Exact result.** For \(n\) *principal points* spanning dimension \(q\), the
span is the leading \(q\)-eigenspace of the covariance. Tarpey & Flury (1996)
describes the finite-distinct self-consistency result as the special case from
which its broader LCM theorem was generalized.  
**Objective.** Global Euclidean squared-error approximation for principal
points; self-consistency for the broader fixed-point discussion.  
**Feasible set.** Finite Euclidean codebooks and their nearest-point cells.  
**What transfers.** Forced subspace alignment under elliptical/LCM structure;
this is a genuine structural predecessor of the LCM branch.  
**What does not.** The leading-eigenspace conclusion for global principal
points must not be silently assigned to every self-consistent point set. No
nuisance/profiled information, endogenous tilt, conditional-centering class,
or nonexistence result appears.

### 5.5 Tarpey & Loperfido (2015)

**Exact problem.** Extend principal-subspace restrictions for self-consistent
summaries beyond centered elliptical laws, including location-mixture and
skew-normal settings.  
**Exact result.** The published abstract and later theorem context describe a
generalized principal-subspace theorem based on self-consistency. The primary
theorem text was library-inaccessible in this audit, so no narrower hypothesis
or proof technique is asserted here.  
**Objective.** Squared-error approximation and self-consistent subspace
geometry.  
**Feasible set.** Self-consistent summaries for the paper's declared
non-elliptical distribution families, not profiled-information hard
partitions.  
**What transfers.** It is the closest forward source on the width of the LCM
and beyond-elliptical structural programme; any claim that the relevant prior
art ends with elliptical laws must cite and compare it.  
**What does not.** Nothing accessible establishes DS17's endogenous tilt,
nuisance-rank collapse, fixed positive information margins, empirical
exchange stability, or eventual nonexistence. The inaccessible primary proof
cannot be used to claim technique transfer.

## 6. Source corrections and snowball findings

### Flury (1990)

Primary review overturns the previous abstract-level annotation. Flury:

- defines principal points as *global* squared-error minimizers;
- proves that two elliptical principal points lie on a leading covariance
  eigenvector;
- proves only the general rank bound
  \(\dim\operatorname{span}\{\xi_j-\mu\}\le k-1\);
- states the \(k>2\) leading principal-subspace result as a conjecture.

It does not provide a general existence theorem or an arbitrary
self-consistent-point theorem. The existence-direction contrast previously
attached to DS17 was therefore over-attributed.

### Terminology provenance

**Key:** Hastie-Stuetzle-1989

Tarpey & Flury explicitly say that Hastie & Stuetzle (1989) introduced
self-consistency for principal curves and that they generalize it to random
vectors. Tarpey–Flury is the source for the unified random-vector definition,
not the origin of the term.

### Missed forward source

**Key:** Tarpey-Loperfido-2015

Tarpey & Loperfido (2015), *Self-consistency and a generalized principal
subspace theorem*, extends the subspace programme beyond elliptical laws,
including location-mixture/skew-normal settings. It remains an MSE/subspace
theorem, not a profiled-information obstruction, but it is a mandatory
comparison for any claim that DS17's structural cousin stops at elliptical
laws.

### Association rather than FKG

**Key:** Esary-Proschan-Walkup-1967

Esary, Proschan & Walkup (1967) is the historical association source.
Jakubowski supplies the exact equality theorem. FKG is a stronger lattice
correlation framework and is neither necessary nor the closest attribution
for DS17's one-variable conditional calculation.

### Scalar empirical nonregularity comparator

Serinko & Babu (1992) parameterize univariate \(k\)-means by ordered split
points and prove nonstandard empirical limits when the population Hessian is
singular. This is a useful transfer warning, but singular curvature is not
DS17's zero nuisance-information rank, wasted-cell geometry, or absence of an
admissible fixed point.

## 7. Per-claim verdict

### `DS-STABLE-BASINS-CENTERED-OBSTRUCTION`

**Verdict: `search_gap`, with mandatory re-attribution of ingredients.** No
source found the combination of conditional centering, endogenous tilt,
hard-cell self-consistency, zero binned nuisance information, and eventual
absence of margin-certified empirical stable states. The efficient-score
normal equation and the monotone-covariance equality case are classical and
must be cited as such.

### `DS-STABLE-BASINS-LCM-CLASSIFICATION`

**Verdict: claim-level prior art is present for structural conclusion (1),
but the full four-part node remains unmatched.** Tarpey & Flury (1996)
directly proves an LCM self-consistency-to-eigenspace theorem, and Tarpey,
Li & Flury (1995) proves the leading-subspace theorem for principal points.
No source found the reduced-rule nuisance-rank collapse, exact profiled value
identity, sign-split nonemptiness family, or noncompilability conclusion.

Registry action should be one of:

- split the structural conclusion into a literature/bridge node and retain
  `search_gap` on the project-specific remainder; or
- if the compound node remains, set `literature_search_status` to
  `prior_art_found` and state exactly which conclusion has prior art.

Leaving the compound node at an unqualified `search_gap` understates the
published LCM/self-consistency theorem.

### `DS-STABLE-BASINS-FIXED-POINT-GATE`

**Verdict: `search_gap`.** Lloyd/self-consistency is classical, but no source
found the decomposition into a Lloyd-stationary branch for
(T_\beta=S_\psi-\beta S_\lambda) plus the endogenous root
(E[h(T_\beta)S_\lambda]=0), nor the necessity-only empirical gate.

### `DS-STABLE-BASINS-GATE-SCANS`

**Verdict: `search_gap` for a direct methodological precedent; status remains
measured, never theorem authority.** Mixture-quantizer continuation and Lloyd
branch computation are adjacent numerical traditions, but no paper found
matches the profiled endogenous-root scans. The negative finite scan itself
cannot support novelty or the theorem.

## 8. Re-attribution risks before publication

1. Calling the tilt-residual orthogonality itself novel would under-credit
   classical efficient-score / least-favourable-direction theory.
2. Calling the covariance sign or equality step a DS17 theorem would
   under-credit Chebyshev/Jakubowski; calling it FKG would overstate the
   machinery.
3. Calling Tarpey–Li–Flury a theorem about all self-consistent points in the
   *leading* eigenspace conflates global principal points with arbitrary
   self-consistent supports.
4. Calling Flury (1990) an existence or (k>2) principal-subspace theorem is
   incorrect; those statements are not proved there.
5. Calling Tarpey–Flury the origin of the term self-consistency omits
   Hastie–Stuetzle.
6. Calling Serinko–Babu's singular Hessian the same phenomenon as DS17's
   nuisance-rank collapse is an analogy presented as identity.
7. The 2015 generalized principal-subspace paper must be discussed before any
   beyond-elliptical structural novelty language.
8. `search_gap` is the strongest justified negative-search verdict. This
   targeted round is not citation saturation and proves no novelty.

## 9. Final search conclusion

The exact DS17 obstruction and endogenous fixed-point gate were not found in
published work. The mathematical combination may remain project-level, but
its proof is built from two classical ingredients that require explicit
attribution, and its LCM structural conclusion overlaps a published
self-consistency-to-eigenspace theorem closely enough that the compound LCM
claim cannot remain described simply as an unqualified search gap.
