# Manuscripts — lagging integration target

**Role.** These are frozen publication-shaped snapshots of the research
program. The live scientific memory (`CLAIMS.json`, `KNOWN_RESULTS.md`,
`COUNTEREXAMPLES/`) is **ahead** of the manuscripts: results are audited,
assumptions hardened, and counterexamples added here first, and harvested into
a manuscript revision only when a publication decision is taken (see
`research-plan-proposal.md` — the paper is a by-product of the ledger, not a
driver). Never treat a manuscript statement as more current than the registry.

**Do not load the `.html`/`.md` article bodies into an agent context.** They
are ~400 KB each, mostly base64-inlined figures. Use the crosswalk below plus
the registry instead; open a manuscript only in a dedicated
manuscript-revision task.

## Files

| File | What it is | State |
|---|---|---|
| `score_space_quantization_article_v8.md` / `.html` | Main research article, v8, 26 Aug 2026: "Information-optimal hard quantization of multivariate score space" | Structurally complete draft; proofs compressed; behind the registry (see staleness) |
| `doptimal_event_categorization_hep.html` | Shorter HEP-facing companion: D-optimal event categorization for multi-parameter inference | Draft |
| `scorequant_research_landscape_en.html` | Literature/landscape survey (history, key authors, software: MadMiner, INFERNO, ThickBrick, GATO, BOBR, OptBinning) | Superseded by `LITERATURE.md` for research use |

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

## Known staleness in v8 (fix at next manuscript revision)

- A figure caption in §5.2 refers to "Theorem 6"; the result is Theorem 3
  (leftover from renumbering).
- Theorem 3's hypotheses lack the audited merged-duplicate-atom and
  tolerance caveats now recorded in the registry (see crosswalk row).
- The manuscript has no A-optimality material and predates the
  information-efficiency output section (I1–I3) and the guarantee hierarchy of
  `KNOWN_RESULTS.md`.
- `CE-DS-GLOBAL-GEOMETRY-001` cites this manuscript as its source; the second
  independent witness (`-002`) postdates it.
