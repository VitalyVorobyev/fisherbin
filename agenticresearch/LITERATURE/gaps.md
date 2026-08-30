# Coverage gaps

Communities, venues, or periods suspected under-covered by the current graph.

- Old monographs and proceedings with incomplete citation indexing (Späth books, Fedorov).
- Non-English determinant-clustering literature.
- Very recent preprints (forward-citation lag).
- Paywalled/unreachable primary texts behind load-bearing DS15 citations
  (30 Aug 2026 audit): Graf–Luschgy 2000 ch. 4–5 (the "Thm 4.1" numbering for
  positive cell mass is unverified; 4.2/4.12/5.1 confirmed via Liu–Pagès),
  Silvey 1978 (theorem itself unread, secondary only), Pukelsheim's
  singular-design chapters. A library pass is needed before any submission.
- Constrained/penalized quantization where a feasibility margin interacts
  with the optimum (DS15's novelty axis): only practice-side evidence exists
  (INFERNO remark; Erdmann et al. 2026 penalties; Wunsch et al. 2021 "optimum
  not known"); no theory community identified yet — watch
  Blanchard–Jaffe–Zhivotovskiy (arXiv:2507.06226) and its citers.

## After snowballing round 3 — 30 August 2026

- **Book citation graphs remain incomplete.** Pukelsheim (1993/2006) and
  Späth (1985) are bibliographically resolved, but neither had a stable
  canonical OpenAlex work record. Fedorov (1972) was forward-heavy and had no
  indexed reference list. Their primary bibliographies still need manual
  backward traversal.
- **Recent HEP forward coverage remains immature.** *Learning to bin*
  (arXiv:2601.07756) was manually screened from the local PDF because OpenAlex
  had no canonical record during the snapshot; reliable forward citations are
  not yet available.
- **Determinant-clustering consistency remains under-covered at theorem
  level.** Bryant (1991) is a plausible adjacent source, but inaccessible
  primary text prevented verification of its exact objective and assumptions.
- **Non-English and pre-digital clustering literature remains a gap,**
  especially work between the 1967 Friedman–Rubin paper and Späth's 1977
  exchange study.
- **Citation-index reproducibility is imperfect.** OpenAlex exhausted its
  request budget during the corrected global-union pass; Semantic Scholar was
  used as a fallback for missing edges. Per-source counts and limitations are
  retained in `graph.json`; they should not be presented as a saturation
  claim.
