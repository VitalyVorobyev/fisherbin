# Manuscripts — lagging integration target

**Role.** These are frozen publication-shaped snapshots of the research
program. The live scientific memory (`claims/`, `KNOWN_RESULTS/`,
`COUNTEREXAMPLES/`) is **ahead** of the manuscripts: results are audited,
assumptions hardened, and counterexamples added here first, and harvested into
a manuscript revision only when a publication decision is taken (see
`research-plan-proposal.md` — the paper is a by-product of the ledger, not a
driver). Never treat a manuscript statement as more current than the registry.

**Prefer the crosswalk below plus the registry over the article bodies.** The
v9 article is ~165 KB of Markdown source / ~195 KB rendered — greppable and
section-readable, but still an order of magnitude more than a claim lookup, so
open it only in a dedicated manuscript-revision task. Its Appendix H maps every
`NOVELTY_LEDGER.md` row to the section or appendix that carries it, and
Appendix G resolves every counterexample fixture id.

**Rendering.** The `.html` sibling is generated, never hand-edited:

```bash
uv run agenticresearch/py/render_manuscript.py agenticresearch/manuscripts/score_space_quantization_article_v9.md
```

The script (python-markdown declared inline, so `uv run` fetches it on demand)
carries the v8 stylesheet verbatim, loads MathJax 3 from its CDN, links `[n]`
citations to the `ref-n` anchors, renders `[novelty: …; ledger …]` tags as superscript provenance marks that stay
hidden until the sidebar's "Show provenance" button is pressed, and builds the
sidebar contents from the `##` headings (appendices under their own divider). Source conventions: `\(…\)` and
`\[…\]` math, section-local equation tags `(7.2)`, result boxes as
`<div class="theorem" markdown="1">`.

**Figures live in `figures/`, never inlined.** The six assets were base64
`data:` URIs until 29 Aug 2026, which made the article a 407 KB blob with
single lines over 100 KB: undiffable by git, unsearchable by grep, unloadable
by an agent. `py/registry.py validate` now fails on any `data:image/` payload
in the workspace, so this cannot regress. The `.html` needs its sibling
`figures/` directory to render — it is no longer a self-contained single file.

## Files

| File | What it is | State |
|---|---|---|
| `score_space_quantization_article_v9.md` / `.html` | Main research article, v9, 3 Sep 2026 (M12 session S5): "Information-optimal hard quantization of multivariate score space"; main text §1–§10 plus Appendices A–H | Current; drafted from `NOVELTY_LEDGER.md`, restructured the same day into main text + appendices after the owner rejected the flat first draft; Appendix H places every ledger row |
| `score_space_quantization_article_v8.md` / `.html` | Main research article, v8, 26 Aug 2026 | Superseded by v9; kept for the crosswalk and as the S2 reconciliation input |
| `NOVELTY_LEDGER.md` | Novelty ledger, 3 Sep 2026 (M12 session S2): one row per central v8 statement and per finding proved since v8, with novelty label, attribution and registry pointer | Current; the v9 draft (S5) is written from it |
| `../archive/doptimal_event_categorization_hep.html` | Shorter HEP-facing companion: D-optimal event categorization for multi-parameter inference | Archived 3 Sep 2026 (M12 consolidation); not a revision input |
| `../archive/scorequant_research_landscape_en.html` | Literature/landscape survey (history, key authors, software: MadMiner, INFERNO, ThickBrick, GATO, BOBR, OptBinning) | Archived 3 Sep 2026; superseded by `LITERATURE/` |

## Numbering crosswalk (manuscript v9 ↔ v8 ↔ registry)

Four numbering systems have circulated: manuscript v9 environments, manuscript
v8 environments, the older v5 research-notes numbering, and the registry claim
ids. The registry ids are canonical; the ledger row resolves each v9 result to
its claim ids and attribution. v9 has a main text (§1–§10, twelve numbered
results in one counter) and Appendices A–H (lettered results); the "first
draft" column is the rejected 3 September 2026 single-counter draft, kept only
because the S5 packet and the placement notes were written against it.

| Manuscript v9 | v8 | v9 first draft | v9 location | Novelty; ledger row |
|---|---|---|---|---|
| Proposition 1 (affine form of a common-metric stationary partition) | Proposition 1 | Proposition 1 | §3.2 | adaptation; V8-08 |
| Lemma B.1 (leverage bound) | Lemma 2 | Lemma 2 | Appendix B.2 | known; V8-10 |
| Theorem 2 (finite D exchange stability forces self-consistent Voronoi geometry) | Theorem 3 | Theorem 3 | §4.2 | apparently new; V8-11 |
| Proposition 3 (approximate finite efficient-Voronoi geometry) | Proposition 4 | Proposition 4 | §5.1 | unresolved; V8-24 |
| Lemma 4 (variational form of the generalized profiled information (classical)) | — | Lemma 5 | §5.2 | known; DS11-1 |
| Proposition C.1 (refinement monotonicity, neutral splits, and the exact domination gap) | — | Proposition 6 | Appendix C.3 | direct corollary; DS11-2 |
| Theorem 5 (population stationarity is efficient-Voronoi geometry) | — | Theorem 7 | §5.3 | adaptation; DS12-1 |
| Proposition 6 (exact profiled leverage bound at exchange-stable states) | — | Proposition 8 | §5.4 | apparently new; DS13-1 |
| Theorem 7 (conditional finite-to-population bridge under (M1)–(M5)) | — | Theorem 9 | §5.5 | adaptation; DS14-1 |
| Theorem 8 (margins dichotomy at global finite D_s optima (d_\psi=d_\lambda=1)) | — | Theorem 10 | §5.6 | apparently new; DS15-1 |
| Proposition C.2 (exact empirical sandwich and bracket limits) | — | Proposition 11 | Appendix C.7 | direct corollary; DS15-3 |
| Proposition C.3 (achievability by swap steering) | — | Proposition 12 | Appendix C.7 | unresolved; DS15-2 |
| Theorem 9 (margin price, value funnel, and floor) | — | Theorem 13 | §5.7 | apparently new; DS16-1 |
| Lemma C.4 (tilt-residual identity and the fixed-point gate) | — | Lemma 14 | Appendix C.9 | direct corollary; DS17-3 |
| Theorem 10 (conditional centering empties the margin-certified branch) | — | Theorem 15 | §5.8 | apparently new; DS17-1 |
| Proposition C.5 (merged branch on linear-conditional-mean laws) | — | Proposition 16 | Appendix C.9 | known; DS17-2 |
| Theorem 11 (exact off-class global basin and empirical transfer through global optima) | — | Theorem 17 | §5.9 | adaptation; DS18-1 |
| Theorem 12 (valid two-sided brackets and exact saddle closure) | — | Theorem 18 | §6.1 | adaptation; DS19-1 |
| Proposition D.1 (\Delta-consistency of the \beta=0 interval programme on the off-class law of Theorem 11) | — | Proposition 19 | Appendix D.3 | direct corollary; DS19-3 |
| Proposition D.2 (what is polynomial) | — | Proposition 20 | Appendix D.4 | direct corollary; DS19-5 |
| Proposition E.1 (exact A move oracle and finite termination) | — | Proposition 21 | Appendix E.3 | direct corollary; A1-1 |
| Proposition E.2 (tangent screening for A) | — | Proposition 22 | Appendix E.3 | direct corollary; A3-1 |
| Proposition F.1 (restricted-class empirical consistency) | Proposition 5 | Proposition 23 | Appendix F.5 | adaptation; V8-40 |

Equations are numbered per section or appendix in v9 and only when referenced;
appendices restate what they need under their own tag. The first-draft v8→v9
equation map in `docs/programme/S05-manuscript-v9-draft.md` is historical.
Fixtures are cited in the main text as "fixture G\(n\)" and resolved by
Appendix G; Appendix H places every ledger row.

### v8 crosswalk (historical)

| Manuscript v8 | Registry claims | Notes |
|---|---|---|
| Proposition 1 (common-metric stationary partition is affine / Mahalanobis Voronoi) | GENERAL-FIRST-VARIATION, D-POP-VORONOI | population level |
| Lemma 2 (leverage bound) | D-LEVERAGE | |
| Theorem 3 (finite D exchange stability ⇒ self-consistent Voronoi) | D-EXCHANGE-IMPLIES-VORONOI, D-EXCHANGE-VIOLATION-LOWER-BOUND, D-FINITE-INDUCTIVE-CLOSURE | audited 26 Aug 2026 (`AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md`); registry statement adds merged-atom, exact-K, and zero-tolerance hypotheses plus boundary counterexample `CE-D-UNMERGED-DUPLICATES-001` — the manuscript does **not** yet carry these |
| Proposition 4 (approximate finite efficient-Voronoi bound for \(D_s\)) | DS-OKN-BOUND | called "Prop. 17" in the old v5 numbering |
| Proposition 5 (restricted-class empirical consistency) | CONSISTENCY-RESTRICTED-AFFINE | |
| *(absent)* | DS-PROFILED-VARIATIONAL (DS11), OPEN-DS-POP-COMMON-METRIC (DS12), DS-EXCHANGE-LEVERAGE-BOUND (DS13), OPEN-DS-FINITE-POP-BRIDGE (DS14) | audited 28 Aug 2026 (`AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md`); no manuscript counterpart yet |

## Known staleness

### v9 (3 September 2026)

- The main text was cut hard in the restructure (about 21,000 words of flat text
  became a main text under 9,000 words plus appendices). No independent human
  read-through has happened yet; the owner's reading of the rendered main text is
  the acceptance step recorded in `docs/programme/S05-manuscript-v9-draft.md`.
- Haynsworth 1968 is cited for the Schur-complement inertia lineage (DS15-4)
  without a ledger attribution key; the Jakubowski 2021 volume details are
  unverified. Both are bibliographic, not mathematical.
- Every item in the v8 list below is addressed in v9 (Appendix H names the
  location for each ledger row; the four required corrections — Theorem 2
  hypotheses, the fig-02 caption, the §8 profiled \(D_s\) implementation row,
  the §9 open problem — are recorded in the S5 packet). New staleness goes
  here, one bullet per item, by the session that produces the result.

### v8 (historical; fixed in v9)

- A figure caption in §5.2 refers to "Theorem 6"; the result is Theorem 3
  (leftover from renumbering).
- Theorem 3's hypotheses lack the audited merged-duplicate-atom and
  tolerance caveats now recorded in the registry (see crosswalk row).
- The manuscript has no A-optimality material and predates the
  information-efficiency output section (I1–I3) and the guarantee hierarchy of
  `KNOWN_RESULTS/`.
- `CE-DS-GLOBAL-GEOMETRY-001` cites this manuscript as its source; the second
  independent witness (`-002`) postdates it.

### Added 28 August 2026 (the DS-bridge sessions)

- **The whole DS11–DS14 chain is absent.** The manuscript's \(D_s\) material
  predates the variational form, the population stationary geometry, the exact
  profiled leverage bound, and the conditional finite\(\to\)population bridge
  (`KNOWN_RESULTS/05b-ds-bridge.md`).
- **DS11's core identity is not ours.** The audit re-attributed it to classical
  prior art (Krein 1947 / Anderson 1971 / Li–Mathias 2000, Thm 2.2) and set
  `literature_search_status: prior_art_found`. Any draft claiming it as novel
  must be corrected before submission — this is the highest-risk item here.
- **Two new counterexamples** postdate the manuscript:
  `CE-DS-DEGENERATE-GLOBAL-TIE-001` and `CE-DS-POP-WASTED-CELLS-001`.
- **DS14 is conditional**, on margins that are explicitly *not* automatic at
  finite optima (OP28). Nothing in the manuscript states that qualification.
- **Assumption labels changed.** DS14's margins are `(M1)`–`(M5)`; they were
  `(A1)`–`(A5)` until the labels were found to collide with the A-optimality
  results A1–A4.

### Added 29 August 2026 (the DS-margins session)

- **DS15 is absent and reframes the \(D_s\) story.** For conditionally
  centered laws (\(E[S_\lambda\mid\hat s]=0\); Gaussian/elliptical) at
  \(d_\psi=1\), global finite \(D_s\) optima converge in value to the
  *unrestricted* population supremum, attained only by the nuisance-degenerate
  efficient-score interval quantizer: (M2) is automatic, (M3) provably fails,
  and the compile target for profiled criteria is the projected
  efficient-score rule, not a margin-certified in-bin quantizer
  (`KNOWN_RESULTS/05b-ds-bridge.md` DS15). Any manuscript treatment of DS14
  must carry this qualification, and the "singleton cells persist" reading of
  the \(N\le18\) evidence is now known to be pre-asymptotic
  (N-DS-SCALAR-MASS).
- **New prior-art constellation.** Kieffer-1983 / Graf-Luschgy-2000 /
  Levrard-2015 / Silvey-1978 / Wang-Yang-Stufken-2019 enter the bibliography;
  the distortion-vs-determinant "two camps" frame (topics/01, topics/04) is
  the natural related-work skeleton for the margins discussion.

### Added 30 August 2026 (the DS15 audit session)

- **DS15's scope narrowed by its audit.** The independent audit
  (`AUDITS/AUDIT-DS-MARGINS-AT-OPTIMA-001.md`) refuted the registered
  \(d_\lambda\)-generality: at \(K=d_\lambda+1\) every feasible labeling has
  profiled value exactly zero (rank ceiling;
  `CE-DS-MARGINS-RANK-VACUITY-001`), so DS15 is a
  \(d_\psi=d_\lambda=1\) theorem with \(K\ge3=d_\lambda+2\), and the
  \(d_\lambda\ge2\) branch is open (OP29). Any manuscript statement of DS15
  must carry the scalar-nuisance scope and must not cite the original
  \(O(N^{-3/4})\) achievability rate as almost-sure (the audited rate carries
  a \(\sqrt{\log\log N}\)); the achievability proposition is now a proof, not
  a sketch, with audit-supplied ingredients that a paper would need to spell
  out.

### Added 30 August 2026 (the stable-margins session)

- **DS16 is absent.** The margin price and value-funnel theorem at arbitrary
  labelings, the exchange-stable-state census, the seed-independent nuisance
  collapse at library scale, and the certificate-gated compile verdict for
  profiled criteria (`KNOWN_RESULTS/05b-ds-bridge.md` DS16, packet
  `WORK/completed/DS-STABLE-MARGINS-COMPILE.md`) have no manuscript
  counterpart, and the deployability story in any future revision must route
  profiled compilation through the projected efficient-score rule with the
  margin-certified path priced, not assumed.
- The two new fixtures (`CE-DS-STABLE-MARGIN-RETAINING-001`,
  `CE-DS-INTERVAL-SEED-UNSTABLE-001`) and the census/library measured rows
  (N-DS-STABLE-*) postdate v8.

### Added 30 August 2026 (the DS16 audit session)

- **DS16 needs the audited uniform-law proof, not the original pointwise
  SLLN wording.** The codebook in Lemma DS16.1 is data-dependent; the valid
  bridge is a uniform strong law over compact tilt--codebook sets. The
  near-minimizer codebook-rigidity ingredient must be attributed to
  Rakhlin--Caponnetto (2006), while the arbitrary-grouping and signed-nuisance
  steps remain specific to DS16.
- **The compile language was too strong.** The projected rule is the only
  *currently established* unconditional route in the registry, not a theorem
  excluding all future compilers. DS14 is a theorem for exchange-stable
  sequences satisfying all eventual margins and law assumptions; one finite
  fit passing a measured triple supplies diagnostics, not population
  stationarity. Certificate-branch inhabitation and a constrained solver stay
  open in OP30/OP7.
- **The constrained values and prices must not be conflated.** The strict
  nuisance-block value \(v^{*+}(\kappa)\) differs from the closed
  full-eigenvalue value \(v^*(\kappa)\); neither attainment nor one-sided
  continuity is proved. Report the observable finite
  \(\hat v_K-\hat\Phi_s\), not a numerical \(\delta(\kappa)\), which is only
  existential.
- **Two measured summaries were corrected.** The exact stable-count range is
  5--944, not 18--944. The 0.004--0.046 researcher library gap is an aggregate
  summary, not a run-wise bound; an independent N=100 random-seed run reached
  0.075 while preserving the qualitative centered-law funnel.

### Added 31 August 2026 (the stable-basins session; audit-hardened)

- **DS17 proves the margin-certified stable branch almost surely eventually
  empty on its declared conditionally centered population class (L).** The
  conditional-centering obstruction — the extended numerator/root identity
  chained through the conditional Chebyshev association inequality under
  (L), then the pathwise DS14′ lemma — shows that on every atomless (L)-law
  with (M1)+(M4) (Gaussian/elliptical laws included) no one-point
  exchange-stable labeling carries (M2)+(M3)+(M5) at any fixed margins for
  all large \(N\) (`KNOWN_RESULTS/05b-ds-bridge.md` DS17). Any manuscript
  passage presenting the DS14 companion path as a live conditional
  deployment route on class (L) is now stale; it is a finite diagnostic
  only, not a population certificate. The audit distinguishes that numerator
  equation, which remains meaningful at a singular nuisance block, from the
  quotient identity \(B_q^*=\beta\), which requires
  \(I_{\lambda\lambda}(q)>0\). Conditional centering is a property of the
  population law; it is never permission to sample-center scores.
- **The merged (M5)-free branch is classified, and it does not compile.**
  Dropping the separation margin, margin-compatible stationary
  configurations on class (L) survive only as wasted-cell structures: the
  projected centroids coincide, and the compilable merged reduction has
  \(\lambda_{\min}=0\). The Gaussian sign-split family has value \(v_2\), but
  that numerical identity is not a general LCM theorem. The eight-atom
  fixture remains the structured construction; the audit adds the absolute
  support-minimal three-atom boundary and records why neither atomic law
  satisfies the theorem's atomless/margin hypotheses.
- **Off the class the gate is a necessary diagnostic, not a certificate.**
  A full declared-window independent multistart found one mix3
  self-consistent root carrying \(\lambda_{\min}=1.7364\) and near-zero
  measured price. It did not prove uniqueness, gate sufficiency, branch
  completeness, or empirical transfer. Manuscript language asserting “free
  certification” or finite-scan completeness is stale.
- **The ingredients require classical attribution.** Efficient-score
  orthogonality, conditional Chebyshev equality, and principal-point/Lloyd
  self-consistency have established antecedents. The audit found no direct
  source for DS17's compound eventual-nonexistence theorem, so that absence is
  a `search_gap`, not novelty; the LCM/self-consistency component is marked
  `prior_art_found`.
- **New claims and a rescoped open problem.**
  `DS-STABLE-BASINS-CENTERED-OBSTRUCTION`, `DS-STABLE-BASINS-LCM-CLASSIFICATION`,
  `DS-STABLE-BASINS-FIXED-POINT-GATE`, and `DS-STABLE-BASINS-GATE-SCANS` enter
  the registry; `OPEN-DS-STABLE-BASINS`/OP30 is rerouted from "do
  margin-compatible stable sequences exist" to the merged-branch,
  attainment, and constrained-design remainders left open by DS17.

### Added 31 August 2026 (the exact non-centered basin session; audit complete)

- **DS18 supplies one exact off-(L) positive theorem, but only through global
  selection.** For independent uniform \(X,Z\), scores
  \((S_\psi,S_\lambda)=(X,3X^2-1+Z)\), and \(K=3\), the cuts \(\pm1/3\)
  give \(I_q=\operatorname{diag}(8/27,32/81)\), \(\beta=0\), and
  \(D_s\)-efficiency \(8/9\). The rule is the unique strict population
  optimum up to labels, and every sequence of finite global regular
  \(D_s\) optimizers transfers to it almost surely and is exactly ordinary
  one-point exchange-stable. Manuscript language saying that no off-(L)
  transfer theorem exists is stale.
- **Do not turn the result into a local-algorithm or raw-cut claim.** The
  theorem is existential through global finite optimizers. The serialized
  support-minimal \(N=4\) boundary fixture has a strict improving move from
  the raw population-cut labels, so those labels need not be stable at finite
  \(N\); generic exchange ascent selection remains open.
- **No deployment consequence exists.** The DS18 claim passed its fresh
  independent adversarial audit on 31 August 2026
  (`AUDITS/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001.md`, **verified with
  hardened assumptions**), and the verdict deliberately changes nothing for
  deployment: no `src/`, API, or compile-path language may rely on it, and the
  audit proves neither practical basin selection nor robustness under
  perturbations of the law.
- **Two DS18 statements the manuscript must not reproduce as written.**
  (i) Any text attributing the scalar three-level uniqueness to a
  strict-log-concavity result is stale: \(\operatorname{Unif}[-1,1]\) is
  log-concave but not strictly so, and the correct antecedents are
  Kieffer (1983) and Mease & Nair (2006). (ii) Any text citing DS15's Lemma 3
  or Proposition 5 inside the DS18 proof is stale: those are registered for
  class (L) with exactly centered empirical scores, both of which DS18 negates;
  the audited proof is self-contained.
- **The DS18 finite exchange-stability claim now names its convention.** The
  in-bin (DS9) feasibility convention is load-bearing — under a DS11
  pseudo-inverse comparison domain a global optimum over regular labelings need
  not be exchange-stable at all
  (`CE-DS-NONCENTERED-SINGULAR-DESTINATION-001`, \(N=4\), gain \(1/96\)).
  Manuscript language saying "global optimum implies exchange stable" without
  the convention is stale.

### Added 1 September 2026 (the practical certified-solver session)

- **DS19 closes P1 by reduction, not by universal strong duality.** For
  \(d_\psi=1\), the tilt-DP construction gives valid generalized and regular
  two-sided brackets and an observable saddle closure test. Fixed-tilt exact
  evaluation, polynomial certified-accuracy minimization, and exact
  fixed-\((K,d_\lambda)\) computation are established; exact polynomial bit
  complexity with variable \((K,d_\lambda)\) remains OP31. The manuscript must
  not describe the bracket as generically exact: `CE-DS-TILT-DUAL-GAP-001`
  has an exact order-one gap greater than 0.68.
- **The DS18 interval-DP primal is value-consistent, and only value-consistent.**
  On the named DS18 law the raw \(X\)-interval DP has
  \(\Delta_N\to0\) almost surely and inherits the audited disagreement bound.
  This does not imply exchange stability, local-ascent basin selection,
  perturbation robustness, or permission to compile a profiled terminal.
- **The vector tilt outer problem is not quasiconvex in general.**
  `DS-MATRIX-TILT-NONQUASICONVEX` disproves Tier B's convex/quasiconvex route
  by an exact \(d_\psi=d_\lambda=2\) witness. Weak matrix-tilt duality remains
  valid; no approximation or library surface follows.
- **Deployment remains audit-gated.** A regular closed saddle certifies finite
  globality; a nonclosed bracket reports an interval; the projected
  efficient-score rule remains the established unconditional route for its
  distinct formulation; a DS14 companion still requires all audited sequence
  assumptions; otherwise compilation is refused. DS19 is internal until a
  fresh independent audit.

### Added 2 September 2026 (the DS19 audit session)

- **DS19 is audited and hardened; the manuscript must carry the hardened
  wording.** The tilt-DP bracket, the saddle gate, the certified bracket,
  \(\Delta\)-consistency and the Tier B witness survived an independent
  adversarial audit (`AUDITS/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001.md`).
  Five hardenings apply: the tie lemma (ties do not cost tie-order
  enumeration); the closure gate is set-valued and a reported open bracket is
  not a gap certificate (`CE-DS-TILT-DUAL-TIE-MASK-001`); the bit model of the
  certified bracket is explicit; support minimality of the gap witness is for
  \(K=3\) only — the overall minimum is \(N=3,K=2\)
  (`CE-DS-TILT-DUAL-GAP-002`, gap \(1/6\)); zero-weight rows are excluded.
- **Do not describe exact computation as fixed-\((K,d_\lambda)\) only.** At
  \(d_\lambda=1\) the exact dual minimiser is bit-polynomial for every
  \(K\) (audit §7.5); for fixed \(d_\lambda\ge2\) it is
  arithmetic-polynomial by Toledo (1993). The fixed-tilt DP is \(O(KN)\)
  after sorting (Grønlund et al. 2017), not only \(O(KN^2)\). Both are
  attribution facts that must reach any submission.
- **Deployment remains audit-gated by the compile table, not by this audit.**
  Verification authorizes no compile surface.

### Added 3 September 2026 (the M12 reconciliation session)

- **`NOVELTY_LEDGER.md` now supersedes the item list above as the v9 input.**
  Every item in this staleness list is carried in a ledger row's Notes column,
  with a novelty label and attribution; the list stays as the historical
  record and gets no further entries. Of 103 rows, 20 are `known`, 34 `direct
  corollary`, 10 `adaptation`, 8 `apparently new` (each on a `search_gap`
  only, pending the P8 adversarial literature review), and 31 `unresolved`
  (open claims, audit records, and results with no recorded literature
  search). The ledger's `unresolved` rows are the P8 worklist.
- **v8 statements with no registry counterpart** (three-level framing;
  the §8.2 "no differentiability theorem" absence; the §2.2 det W vs det B
  remark; the §5.2/§5.3/§11 numerical rows) are listed in the ledger's
  "Gaps" subsection; they are framing or measured evidence, not claims.

**Who maintains this list.** The session that produces the result, as
completion item 7 of `protocols/theorem.md` and the closing duty of
`protocols/audit.md`. It had no updater before workspace v4.0, which is why the
items above accumulated unnoticed.
