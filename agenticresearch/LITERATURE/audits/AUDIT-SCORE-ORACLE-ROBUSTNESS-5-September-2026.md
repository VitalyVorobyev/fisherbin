# Independent prior-art triangulation: the O6 audit

**Key:** Bhattacharya-Ghosh-1978, Hall-1992, Donner-Koval-1980

Run 5 September 2026 for `AUDIT-SCORE-ORACLE-ROBUSTNESS`, the independent
audit of `RETENTION-PLUGIN-CLT-FROZEN-SCALAR` (O6), following the
per-theorem minimum of `protocols/literature.md`. This is a **fresh**
theorem-targeted pass by the auditing session; the researcher's
`LITERATURE/audits/RETENTION-PLUGIN-CLT-FROZEN-SCALAR-5-September-2026.md`
was read only afterwards as comparison material. Retrieval (theorem and
section numbers) was delegated to a subordinate web-verification agent;
every triangulation judgment is the auditor's. Verification labels:
**primary text** when the statement was read in the book/paper text (a
scan, the author's own notes with identical numbering, or the abstract);
**primary record** when a publisher, library or journal table of contents
was checked; **secondary record** when only a citing source was checked. It
is not a citation-saturation round. The claim-level conclusion is
`prior_art_found` for the method; the exact statement is a search gap,
which is never a novelty assertion.

## What O6 actually consumes

1. The multivariate CLT for iid vectors with finite second moments (the
   fourth moment of \(S\) is the largest entry of \(\operatorname{Cov}T\)).
2. The delta method for a map differentiable at the limit point, applied to
   the everywhere-defined estimator functional \(\phi\) (audit report §8).
3. The plug-in variance principle: \(\sigma^2=E[\psi^2]\) with \(\psi\) the
   influence function, and its consistency for a polynomial of sample
   moments.
4. Context only: second-order (Edgeworth) theory for studentized smooth
   functions of moments, which explains the measured \(O(1/n)\) bias and the
   positive skew of the plug-in studentized statistic (O6.7).

## Verification of the four keys recorded on 5 September

- **van der Vaart (1998), `vanderVaart-1998`.** Chapter 3 "Delta Method",
  §3.1 "Basic Result" (p. 25) — *primary text* (scanned contents,
  ETH library). "3.1 Theorem" is the delta method with the exact hypotheses
  O6 uses (map defined on a subset of \(\mathbb R^k\), differentiable at
  \(\theta\), \(T_n\) with values in the domain) — *primary text* in the
  author's lecture notes with identical numbering (Kleijn/UvA host), the
  1998 book itself corroborated (*secondary*). The sample variance under
  \(EX^4<\infty\) is **Example 3.2**, not an unnumbered example — *primary
  text*. Chapter 20 "Functional Delta Method" (§20.1 von Mises calculus,
  §20.2 Hadamard differentiability) — *primary text* (contents). Theorem
  5.23 (M-estimator asymptotic normality) sits in §5.3 "Asymptotic
  Normality" (pp. 51–60) — section *primary text*, number *secondary*.
  **Corrected: Example 3.2 named; Chapter 20 added.**
- **Cramér (1946), `Cramer-1946`.** Chapter 28 "Asymptotic properties of
  sampling distributions" (p. 363), **§28.4 "Functions of moments"** —
  *primary text* (archive.org scan of the contents). Companion finite-sample
  algebra: §27.4 "The variance", §27.7 "Functions of moments".
  **Confirmed; the "cited from memory" caveat is lifted.**
- **Serfling (1980), `Serfling-1980`.** Chapter 3 "Transformations of Given
  Statistics" (p. 117), Chapter 2 "The Basic Sample Statistics" (p. 55) —
  *primary record* (Google Books). The labels "Theorem A" / "Theorem B" in
  §3.3, and which of the two needs only differentiability at the point —
  **unresolved** (no readable text reachable: Wiley and the e-book front
  matter refuse, the archive copy has no OCR). The researcher's "Thm B
  corroborated by two secondary citations" stands as *secondary*; the
  auditor adds no confirmation.
- **Hampel, Ronchetti, Rousseeuw & Stahel (1986),
  `Hampel-Ronchetti-Rousseeuw-Stahel-1986`.** Chapter 2 "One-Dimensional
  Estimators" begins p. 78 — *primary record*; \(V(T,F)=\int\mathrm{IF}^2dF\)
  is cited to p. 85, inside §2.1 — *secondary*. Sub-section letter and
  equation numbers — **unresolved**.
- **Wishart (1932), `Wishart-1932`.** Biometrika 24(3/4):441–456 — *primary
  record* (journal TOC). Normal-theory content — *secondary*.
- **Kendall & Stuart, Vol. 2 *Inference and Relationship* (3rd ed.).**
  Chapter 26 "Statistical Relationship: Linear Regression and Correlation",
  Chapter 27 "Partial and Multiple Correlation" — *primary text* (front
  matter of the archive scan). The section treating the correlation ratio's
  standard error, and whether a non-normal moment-based variance is given —
  **unresolved** (body text not retrievable). Not registered; the gap stays
  in `gaps.md`.

## Triangulation (six fields per source)

- **Bhattacharya & Ghosh (1978), *On the validity of the formal Edgeworth
  expansion*, Ann. Statist. 6(2):434–451 (`Bhattacharya-Ghosh-1978`;
  primary text, abstract).** **Exact problem:** Edgeworth expansion of
  \(W_n=\sqrt n[H(\bar Z)-H(\mu)]\) for smooth \(H\) of a sample-mean vector.
  **Exact result:** validity of the formal expansion under moment and
  Cramér-type conditions; the class covers all smooth functions of sample
  moments. **Objective:** none. **Feasible set:** iid vectors with enough
  moments. **Transfers:** O6.2 is exactly a smooth function of a sample-mean
  vector, so the second-order picture (an \(O(1/n)\) bias and a skew term)
  is the generic one; this is the theoretical backdrop of O6.7.
  **Does not:** no partition, no influence function, no Wald coverage
  statement; O6 uses only the first-order term.
- **Hall (1992), *The Bootstrap and Edgeworth Expansion*, Springer
  (`Hall-1992`; secondary record — Google Books record; the studentized
  skewness discussion is cited to p. 76, section number unresolved).**
  **Exact problem:** Edgeworth expansions for the "smooth function model"
  (statistics that are smooth functions of sample means), studentized and
  not. **Exact result:** the studentized statistic's expansion has a skew
  coefficient of opposite sign and different size from the non-studentized
  one, which is why plug-in Wald intervals under-cover at small \(n\).
  **Objective:** none. **Feasible set:** iid, smooth function model with
  moments. **Transfers:** the measured sign flip (population-studentized
  skew \(-0.30\), plug-in-studentized \(+0.86\) at \(n=100\)) is the textbook
  phenomenon; a bootstrap-\(t\) correction would be the standard remedy.
  **Does not:** O6's packet excludes bootstrap comparisons; nothing here is
  used in the proof.
- **Donner & Koval (1980), *The large sample variance of an intraclass
  correlation*, Biometrika 67(3):719–722 (`Donner-Koval-1980`; primary
  record — PubMed/journal record; the companion Biometrics 36:19–25 paper
  is the estimation one).** **Exact problem:** large-sample variance of the
  ANOVA estimator of the intraclass correlation. **Exact result:** a
  delta-method variance under the one-way random-effects model.
  **Objective:** none. **Feasible set:** balanced/unbalanced family data
  under a normal random-effects law. **Transfers:** the nearest "delta
  method for a between-over-total ratio" in the applied literature; the
  same algebraic shape (ratio of two quadratic forms). **Does not:** the
  grouping is random and the law normal; O6's partition is a fixed
  measurable map of an oracle score and the law is arbitrary with four
  moments; the uncentred ratio and \(0/0:=0\) do not appear.
- **Renaud & Victoria-Feser (2010), *A robust coefficient of determination
  for regression*, J. Statist. Plann. Inference 140(7):1852–1862 (record
  confirmed, primary record; not registered).** **Exact problem:** a robust
  \(R^2\). **Transfers:** the influence-function viewpoint on an \(R^2\)-type
  ratio. **Does not:** regression with random regressors; a robust
  estimator rather than the plug-in; no fixed partition.
- **Koerts & Abrahamse (1969); Ohtani & Hasegawa (1993); Kelley (2007);
  Bishara & Hittner (2012, 2015).** Screened and rejected as transfers:
  exact normal-theory \(R^2\) distributions, small-sample \(R^2\) moments
  under multivariate-\(t\) errors, noncentral-\(F\) effect-size intervals, and
  simulation studies of Pearson's \(r\) under non-normality respectively.
  None contains a fixed-partition uncentred ratio with an explicit
  influence function. Ohtani & Hasegawa is *not* a delta-method paper (the
  auditor's initial guess; corrected here).

## Search verdict

The method of O6.2–O6.4 is prior art (van der Vaart Thm 3.1 / Cramér §28.4
for the limit, Hampel et al. p. 85 for \(\sigma^2=E\psi^2\)); no located
source states the uncentred correlation ratio on a fixed partition with
\(0/0:=0\), the RSS identity, the closed-form influence function
\(\psi=((1-\eta)S^2-(S-c_Z)^2)/v\) or the root-set characterisation of
\(\sigma^2=0\). That statement is recorded as a **search gap** on the claim's
warning; the registry field stays `prior_art_found` because the method is.
No re-attribution. Before any publication use, the two unresolved items
(Serfling §3.3 labels; Kendall & Stuart's correlation-ratio section) must be
read in primary text.
