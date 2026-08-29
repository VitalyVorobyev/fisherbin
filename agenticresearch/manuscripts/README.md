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

**Who maintains this list.** The session that produces the result, as
completion item 7 of `protocols/theorem.md` and the closing duty of
`protocols/audit.md`. It had no updater before workspace v4.0, which is why the
items above accumulated unnoticed.
