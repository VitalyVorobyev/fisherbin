# AUDIT-DS-MARGINS-AT-OPTIMA — publication-grade adversarial audit of DS15

**Programme:** P1 · **Opened:** 30 August 2026 · **Closed:** 30 August 2026 · **Status:** completed

## Goal

Independently verify, refute, or reduce `OPEN-DS-MARGINS-AT-OPTIMA` (DS15):
the margins dichotomy at exact global finite \(D_s\) optima for conditionally
centered laws. The auditor did not produce the proof; the session followed
`protocols/audit.md` with its own counterexample search and its own prior-art
search.

## Outcome

**Verified with hardened assumptions** — and the registered generality
partially refuted. Report: `AUDITS/AUDIT-DS-MARGINS-AT-OPTIMA-001.md`.

- **Refuted:** the \(d_\lambda\)-generality under bare \(K\ge3\). At
  \(K=d_\lambda+1\) exact centering forces every feasible labeling's profiled
  value to exactly zero (rank ceiling + Schur rank additivity) while
  \(v_K>0\): conclusion (i) is false for \(d_\lambda\ge2\), \(K=d_\lambda+1\).
  Minimized exact witness `CE-DS-MARGINS-RANK-VACUITY-001` (\(N=4\)), pinned
  in CI. The correct cardinality condition is \(K\ge d_\lambda+2\); at
  \(d_\lambda=1\) that is exactly the recorded \(K\ge3\).
- **Hardened and verified (\(d_\psi=d_\lambda=1\)):** Proposition 6
  (achievability by steering) closed from a labeled sketch to a proof —
  boundary/mass consistency from (S)-uniqueness, a VC/LIL availability count
  for the swap slabs, drift accounting, two-direction controllability, honest
  \(\tilde O(N^{-3/4})\) rate. Conclusion (3)'s "audit §8" Glivenko–Cantelli
  import was a misattribution (that step is (M4)/(M5)-powered in the source);
  replaced by a self-contained lemma over the fixed half-plane VC class
  needing only (S)-atomlessness. Proposition 5's uniform Lipschitz-in-tilt
  bound was derived. Lemmas 1–3 and conclusions (1),(4),(5) re-derived and
  stand.
- **Independent numerics (no shared code, pure-stdlib exact rationals):**
  20 exhaustively certified global optima at \(N=12\)–\(16\) (up to
  \(7{,}141{,}686\) canonical partitions per instance, ≈42.6M exact
  evaluations): sandwich/tax identity 20/20, zero exact full-lattice ties,
  class boundary (centered vs non-centered nuisance block) reproduced. The
  researcher's float top-64 screen, re-implemented with its \(10^{-9}\)
  guard, ranks the true optimum first with zero casualties 20/20 — the
  screen mechanism is validated at the \(N\ge14\) range where the original
  trend instances are screen-selected (those instances themselves remain
  uncertified; both trend ledger rows now say so). The float-only scalar
  (M2) sweep gained an exact-rational DP anchor at \(N=1000\) (library DP
  agrees to \(10^{-9}\); min mass exactly \(49/200\)).
- **Registry repairs:** missing dependency edges (DS7, DS8, DS9 rank node)
  added; the circular `OPEN-DS-DOMINATION-EQUALITY` dependency removed
  (arrow now runs via `implies`); stale "OP28 open" text fixed in 05a DS10
  and 05b DS11(a); sibling nodes and OP29 rescoped; manuscripts staleness
  list extended.

## Artifacts

- `AUDITS/AUDIT-DS-MARGINS-AT-OPTIMA-001.md` — 16-item report.
- `py/audit_ds_margins_at_optima.py` — independent exact suite
  (identities / vacuity / exhaustive+screen / scalar).
- `AUDITS/artifacts/AUDIT-DS-MARGINS-AT-OPTIMA-001/*.json` — committed run
  records (seeds, revision, script hash, environment).
- `COUNTEREXAMPLES/CE-DS-MARGINS-RANK-VACUITY-001.json` + two CI pins in
  `tests/test_research_claims.py`.
- `LITERATURE/audits/AUDIT-DS-MARGINS-AT-OPTIMA-30-August-2026.md` —
  independent triangulation with recorded query log.
- Ledger rows N-DS-AUDIT15-{IDENTITIES,VACUITY,EXHAUSTIVE,SCALAR-ANCHOR}.

## Next dependency-blocking question

OP29's deployment-relevant half, sharpened by this audit
(`OPEN-DS-MARGINS-NONCENTERED`): do one-point exchange-stable non-global
\(D_s\) labelings — what the library's optimizer actually returns — retain
the DS14 margins on conditionally centered laws, and at what information
cost relative to \(v_K\)? Behind it, same node: the \(d_\lambda\ge2\),
\(K\ge d_\lambda+2\) dichotomy via a vector-(R) steering construction.
