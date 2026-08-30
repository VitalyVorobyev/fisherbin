# Manuscripts — lagging integration target

**Role.** These are frozen publication-shaped snapshots of the research
program. The live scientific memory (`claims/`, `KNOWN_RESULTS/`,
`COUNTEREXAMPLES/`) is **ahead** of the manuscripts: results are audited,
assumptions hardened, and counterexamples added here first, and harvested into
a manuscript revision only when a publication decision is taken (see
`research-plan-proposal.md` — the paper is a by-product of the ledger, not a
driver). Never treat a manuscript statement as more current than the registry.

**Prefer the crosswalk below plus the registry over the article bodies.** The
v8 article is ~58 KB of prose (`.md`) / ~68 KB (`.html`) — greppable and
section-readable, but still an order of magnitude more than a claim lookup, so
open it only in a dedicated manuscript-revision task.

**Figures live in `figures/`, never inlined.** The six assets were base64
`data:` URIs until 29 Aug 2026, which made the article a 407 KB blob with
single lines over 100 KB: undiffable by git, unsearchable by grep, unloadable
by an agent. `py/registry.py validate` now fails on any `data:image/` payload
in the workspace, so this cannot regress. The `.html` needs its sibling
`figures/` directory to render — it is no longer a self-contained single file.

## Files

| File | What it is | State |
|---|---|---|
| `score_space_quantization_article_v8.md` / `.html` | Main research article, v8, 26 Aug 2026: "Information-optimal hard quantization of multivariate score space" | Structurally complete draft; proofs compressed; behind the registry (see staleness) |
| `doptimal_event_categorization_hep.html` | Shorter HEP-facing companion: D-optimal event categorization for multi-parameter inference | Draft |
| `scorequant_research_landscape_en.html` | Literature/landscape survey (history, key authors, software: MadMiner, INFERNO, ThickBrick, GATO, BOBR, OptBinning) | Superseded by `LITERATURE/` for research use |

## Numbering crosswalk (manuscript v8 ↔ registry)

Three numbering systems have circulated: manuscript v8 environments, the older
v5 research-notes numbering, and the registry claim ids. The registry ids are
canonical.

| Manuscript v8 | Registry claims | Notes |
|---|---|---|
| Proposition 1 (common-metric stationary partition is affine / Mahalanobis Voronoi) | GENERAL-FIRST-VARIATION, D-POP-VORONOI | population level |
| Lemma 2 (leverage bound) | D-LEVERAGE | |
| Theorem 3 (finite D exchange stability ⇒ self-consistent Voronoi) | D-EXCHANGE-IMPLIES-VORONOI, D-EXCHANGE-VIOLATION-LOWER-BOUND, D-FINITE-INDUCTIVE-CLOSURE | audited 26 Aug 2026 (`AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md`); registry statement adds merged-atom, exact-K, and zero-tolerance hypotheses plus boundary counterexample `CE-D-UNMERGED-DUPLICATES-001` — the manuscript does **not** yet carry these |
| Proposition 4 (approximate finite efficient-Voronoi bound for \(D_s\)) | DS-OKN-BOUND | called "Prop. 17" in the old v5 numbering |
| Proposition 5 (restricted-class empirical consistency) | CONSISTENCY-RESTRICTED-AFFINE | |
| *(absent)* | DS-PROFILED-VARIATIONAL (DS11), OPEN-DS-POP-COMMON-METRIC (DS12), DS-EXCHANGE-LEVERAGE-BOUND (DS13), OPEN-DS-FINITE-POP-BRIDGE (DS14) | audited 28 Aug 2026 (`AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md`); no manuscript counterpart yet |

## Known staleness in v8 (fix at next manuscript revision)

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

**Who maintains this list.** The session that produces the result, as
completion item 7 of `protocols/theorem.md` and the closing duty of
`protocols/audit.md`. It had no updater before workspace v4.0, which is why the
items above accumulated unnoticed.
