# Targeted prior-art audit: AUDIT-DS-MARGINS-AT-OPTIMA (DS15, independent)

Run 30 Aug 2026 by the independent DS15 audit session (`protocols/audit.md`
item 5), on the **frozen hardened statement** (\(d_\psi=d_\lambda=1\),
(L)+(S)+(R), \(K\ge3\)) — separate from and after the researcher-side
29 Aug OP28 triangulation, which this audit does not modify. Verification
labels: *verbatim* (statement read in the source or a full-text copy),
*secondary* (peer-reviewed source quoting/restating it, named), *abstract*
(abstract/citation-level only), *snippet* (search-result snippet,
unconfirmed). Six search axes, 40+ recorded query strings; per-axis
candidate/relevant counts below. Delegated web-search session; every claim
here was screened against the returned evidence, and the two
registry-impacting corrections were re-checked against `registry.json`
directly.

## Query log (auditability)

- **A. Quantizer consistency & uniqueness verification** — 10 queries,
  ≈95 results screened / 25 relevant. Retrieved full texts: Pollard 1981
  (Yale scan), Liu–Pagès 2020 (JMLR), Roychowdhury arXiv:1703.06518,
  Mease–Nair 2006. Blocked: Graf–Luschgy book (403/500 on all open copies).
- **B. Margin conditions in quantization** — 3 queries, ≈30/9. Retrieved:
  Levrard AOS 2015 full text.
- **C. Singular information at \(D_s\)-optimal designs** — 5 queries,
  ≈45/15. Retrieved: St. John–Draper 1975 (CMU scan). Blocked: Silvey 1978
  (JSTOR), Pukelsheim chapters.
- **D. The novelty axis (margins failure at optima of profiled criteria)** —
  13 queries, ≈120/15. Retrieved: Erdmann et al. arXiv:2601.07756 (HTML).
- **E. 1-D contiguity** — 3 queries, ≈30/12. Retrieved: W. D. Fisher 1958
  (Brown scan, pp. 789–792).
- **F. Swap-steering under side constraints** — 3 queries, ≈30/10.
  Retrieved: arXiv:2507.06226 abstract.

## Triangulation (per `protocols/literature.md`: six fields per source)

- **Pollard (1981), "Strong Consistency of K-Means Clustering", AoS
  9(1):135–140, doi:10.1214/aos/1176345339.** *(verbatim)*
  **Exact problem:** empirical optimal \(k\)-point centroid sets \(A_n\) for
  i.i.d. data under a distortion \(\phi(\|x-a\|)\) with
  \(\phi(2r)\le\lambda\phi(r)\). **Exact result:** if
  \(\int\phi(\|x\|)dP<\infty\) and the optimal set is unique *for every*
  \(j\le k\), then \(A_n\to\bar A(k)\) a.s. (Hausdorff) and
  \(\Phi(A_n,P_n)\to m_k(P)\) a.s. **Objective:** expected distortion.
  **Feasible set:** all \(k\)-point center sets, unconstrained.
  **Transfers:** the value/centroid consistency engine for DS15's
  Proposition 5 and conclusions (2)–(3) (via (S)-uniqueness); the
  every-\(j\) uniqueness hypothesis is satisfied for log-concave laws.
  **Does not:** scalar distortion only; no matrix criterion, no nuisance
  block, no constraints.
- **Graf & Luschgy (2000), *Foundations of Quantization for Probability
  Distributions*, LNM 1730, doi:10.1007/BFb0103945.** *(secondary — book
  unreachable; via Liu–Pagès 2020 (JMLR 21(86)) and Roychowdhury
  (arXiv:1703.06518, Prop 1.1))* **Exact problem:** optimal \(n\)-point
  quantization of \(P\) under \(L^r\) distortion. **Exact results used:**
  every cell of an optimal quantizer has positive mass and null boundary
  (content confirmed; numbering: null boundaries = Thm 4.2, existence =
  Thm 4.12 per Liu–Pagès; **the "Thm 4.1" numbering for positive mass is
  unverified** — the 29 Aug audit's "Thm 4.1/4.2" label was too confident);
  Thm 5.1 = uniqueness of the scalar log-concave \(K\)-quantizer
  (**numbering and content confirmed twice**: Liu–Pagès Lemma 10's proof
  pointer, plus an independent restatement). **Objective:** distortion.
  **Feasible set:** unconstrained codebooks. **Transfers:** \(w^*_b>0\)
  (DS15 conclusion (2) target), \(W_{K-1}>W_K\) deletion mechanism (Lemma
  3), (S)-uniqueness anchor. **Does not:** distortion side only.
- **Kieffer (1983), IEEE IT 29(1):42–47, doi:10.1109/TIT.1983.1056622.**
  *(abstract; uniqueness content corroborated verbatim via Mease–Nair 2006
  and secondary via Liu–Pagès/Kazıklı et al.)* **Exact problem:** scalar
  \(N\)-level quantizer, log-concave density, convex strictly increasing
  \(C^1\) error weight. **Exact result:** unique locally (hence globally)
  optimal quantizer; Lloyd's Method I converges to it. **Objective:**
  weighted error. **Feasible set:** scalar quantizers. **Transfers:**
  (S)-uniqueness for Gaussian efficient scores. **Does not:** nothing on
  empirical optima or constraints. *Boundary found (Mease & Nair 2006,
  Statistica Sinica 16:1299–1312, verbatim): Eubank-type weakenings of
  log-concavity are refuted by an explicit three-stationary-point
  counterexample — (S) must stay pinned to log-concavity of the density.*
- **Levrard (2015), AoS 43(2):592–619, doi:10.1214/14-AOS1293, arXiv
  1405.6672 (the registry's 1310.7138 was the 2013 precursor — corrected).**
  *(verbatim)* **Exact problem:** ERM quantization rates in Hilbert space.
  **Exact result:** Definition 2.1 margin condition
  \(p(t)\le(Bp_{\min}/128M^2)\,t\) on the mass near optimal-cell boundaries
  ⟹ finitely many optimal codebooks, quadratic growth, \(1/n\) rates;
  Gaussian mixtures satisfy it. **Objective:** distortion risk.
  **Feasible set:** unconstrained codebooks. **Transfers:** the margin
  *vocabulary* and the structural contrast: Levrard's margin is a
  hypothesis on the law at population optima, **never proven at optima** —
  DS15 inverts this by proving a (differently defined) conditioning margin
  *fails* at optima. **Does not:** no analogue of nuisance blocks or
  feasibility margins; fast-rate mechanics rest on a squared-distortion
  Pythagorean identity with no Schur analogue.
- **Silvey (1978), Biometrika 65(3):553–559.** *(secondary — abstract-level
  restatements in López-Fidalgo & Rodríguez-Díaz and the design literature;
  the theorem itself was not read)* **Exact problem:** optimal design
  measures whose information matrix is singular. **Exact result (as
  restated):** an equivalence theorem for singular \(M\) via generalized
  inverses, with the usable-inverse characterization left open; the
  singular-\(D_s\) phenomenon predates it (Kiefer; Karlin–Studden, per
  St. John–Draper 1975, verbatim). **Objective:** \(D_s\)/c-optimality
  over design measures. **Feasible set:** the convex set of design
  measures. **Transfers:** the design-side precedent that subset-criteria
  tolerate singular information at optima — DS15's (M3)-failure is the
  partition-side sharpening from "permitted" to "inevitable".
  **Does not:** design measures, not partitions; no inevitability theorem;
  no empirical layer. *(Registry cross-check: the neighbouring key
  `Sibson-Kenny-1975` resolves to a real JRSS-B 37:288–292 paper by DOI —
  the delegated search's "not located" was a query-phrasing miss, not a
  registry defect.)*
- **W. D. Fisher (1958), JASA 53(284):789–798,
  doi:10.1080/01621459.1958.10501479.** *(verbatim)* **Exact problem:**
  partition \(K\) weighted scalar values into \(G\) groups minimizing
  weighted SSE. **Exact result:** optimal partitions are contiguous in the
  sorted order (appendix proof); search space
  \(\binom{K-1}{G-1}\). **Objective:** weighted SSE. **Feasible set:** all
  set partitions. **Transfers:** the 1-D contiguity step of DS8/DS15
  Proposition 4, now with its classical citation. **Does not:** everything
  else.

## The novelty axis (D): outcome

Thirteen queries (≈120 screened) across "profiled Fisher information
binning", "Schur complement optimal partition", HEP systematics-aware
binning (INFERNO, Wunsch et al., Erdmann et al.), constrained-clustering
degeneracy, and information-preserving discretization found **no statement
or proof that free optima of a profiled/Schur-complement information
criterion drive the nuisance/feasibility block to degeneracy**, nor any
equivalent of the DS15 dichotomy. Closest non-precedents: (a) singular
\(D_s\) designs (permitted, not inevitable); (b) Gaussian-mixture ML
degeneracy repaired by eigenvalue constraints (Hathaway 1985;
García-Escudero et al. 2018) — same *shape*, different criterion and
mechanism; (c) INFERNO's unproven remark that its optimum "tends towards"
nuisance-independence; (d) Erdmann et al. (arXiv:2601.07756) adding ad-hoc
penalties against degenerate bins — the DS15 phenomenon observed in
practice, untheorized; (e) Wunsch et al. (2021, CSBS 5:4) stating the
optimal reduction under systematics "is not known". Recorded as a
**search gap** (`literature_search_status: search_gap` on both the claim
and the audit node) — evidence of absence in the searched space, never a
novelty claim.

## Axis F (swap-steering) outcome

No published theorem provides "steer a near-optimal clustering by
single-point swaps to satisfy a side constraint at asymptotically
negligible cost". Ingredients exist separately: Kanungo et al. 2004
(bounded-cost swap analysis), Bradley–Bennett–Demiriz 2000 (flow-based
constrained assignment), and — closest, new — Blanchard, Jaffe &
Zhivotovskiy (arXiv:2507.06226): balance constraints restore k-means
consistency at no asymptotic cost. Proposition 6's construction therefore
required its own proof (supplied by the audit), and Blanchard et al. is the
reference to engage before publication.

## Registry consequences

- `Levrard-2015` bibliography entry corrected (arXiv 1405.6672; margin
  condition stated precisely; "hypothesis on the law, never proven at
  optima" recorded).
- `Graf-Luschgy-2000` note softened: "Thm 4.1" numbering flagged
  unverified; Thm 4.2/4.12/5.1 numberings confirmed via Liu–Pagès.
- New keys: `Fisher-1958` (verbatim), `Mease-Nair-2006` (verbatim; the
  (S)-boundary), `Blanchard-Jaffe-Zhivotovskiy-2025` (abstract; the
  Proposition-6 neighbour). Annotations in `topics/04`.
- `literature_search_status` stays `search_gap` on
  `OPEN-DS-MARGINS-AT-OPTIMA`; the audit node records the same.
- Remaining verbatim gaps for a library pass before any submission:
  Graf–Luschgy ch. 4–5 (the "4.1" number), Silvey 1978 (the theorem
  itself), Pukelsheim's singular-design chapters (`gaps.md` updated).
