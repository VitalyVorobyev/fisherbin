# Reviewed papers

Deep-reviewed papers with outcomes; every entry names the claim ids it informs. Populated by the LITERATURE-GRAPH work packets.

## Valassi (2020) — screened 29 August 2026

Bibliography key `Valassi-2020`; the anchoring annotation is in
`topics/05-hep-inference-aware.md`.

**Outcome: open attribution question, deliberately not settled.** The paper states, in the
single-parameter case, both the retained-information identity behind `FI-QUANT-IDENTITY`
(\(I_\theta=\sum_k s_k\phi_k^2\), cell-mean sensitivity \(\phi_k\)) and an efficiency ratio
FIP\(_3=I_\theta/I_\theta^{(\rm ideal)}\) that coincides with `INFO-D-EFFICIENCY` at \(s=1\). Both
claims now cite it. Neither claim's `status` or `publication_status` was changed and no
`literature_search_status` was set, because that determination belongs to a literature session
running the `protocols/literature.md` checklist, not to a wiring commit.

**The two questions that session must answer:**

1. Does FIP\(_3\) constitute prior art for `INFO-D-EFFICIENCY`, or only for its \(s=1\) restriction?
   The registry statement is the determinant ratio \((\det I_q/\det I_{\rm full})^{1/d}\); the two
   agree only at \(d=1\), where the determinant is not doing any work.
2. Is the argument "bin by \(\gamma_i\)" a *result* or a framing? Valassi asserts the optimal
   partitioning variable is the sensitivity and does not characterise the optimal cells. If it is a
   result, it is the scalar ancestor of the score-space reduction in `PROBLEM.md` and belongs in
   `KNOWN_RESULTS/01-universal.md` as a `[LIT]` attribution.

This is the same failure mode the DS11 audit caught (`AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md`):
a result believed novel that a neighbouring community had stated first in a special case. Resolve
it before any manuscript revision.

## CMS Collaboration (2025) — screened 29 August 2026

Bibliography key `CMS-2025`; the anchoring annotation is in
`topics/05-hep-inference-aware.md`.

**Outcome: motivation, not prior art. No claim cites it, deliberately.** SANNT minimises
\(\Delta r_s=\sqrt{(F^{-1})_{r_sr_s}}\) over one parameter of interest and up to 224 nuisance
parameters — the profiled objective of `DS-SCHUR` at \(s=1\), reached independently and run at
production scale. It never studies the geometry of the resulting partition, so it precedes no
registry theorem.

**What it does supply** is an unusually direct statement of the gap the \(D_s\) programme fills: the
paper records that a Fisher-based loss "introduces an ambiguous choice of binning" and that the
binned likelihood "is not differentiable at its bin edges", and reaches for INFERNO's softmax
histogram or a KDE surrogate. That is the softening `KNOWN_RESULTS/08-soft.md` exists to make
unnecessary. Worth citing in the motivation of any \(D_s\) manuscript.


## Pollard (1981) — read verbatim 30 August 2026 (DS15 audit)

Bibliography key `Pollard-1981`; annotation in `topics/04-vector-quantization.md`.

**Outcome: statement and hypotheses fully verified from the Yale scan.** The
consistency theorem assumes uniqueness of the optimal center set for *every*
\(j\le k\) (not just \(j=k\)) plus a \(\phi\)-moment; value convergence needs
no uniqueness. Informs `OPEN-DS-MARGINS-AT-OPTIMA` (Proposition 5 and
conclusions (2)–(3)) and `AUDIT-DS-MARGINS-AT-OPTIMA`. The every-\(j\)
hypothesis is discharged for log-concave efficient-score laws by the
uniqueness cluster (Kieffer/Graf–Luschgy 5.1/Mease–Nair).

## Fisher (1958) — read verbatim 30 August 2026 (DS15 audit)

Bibliography key `Fisher-1958`; annotation in `topics/04-vector-quantization.md`.

**Outcome: contiguity of optimal 1-D weighted SSE partitions confirmed with
its appendix proof** (pp. 789–792 read). Anchors `DS-SCALAR-EFFICIENT-DP` and
the interval-optimum leg of DS15's Proposition 4.

## Mease & Nair (2006) — read verbatim 30 August 2026 (DS15 audit)

Bibliography key `Mease-Nair-2006`; annotation in `topics/04-vector-quantization.md`.

**Outcome: (S)-boundary found.** Log-concavity of the density suffices for
scalar-quantizer uniqueness (likelihood-ratio ordering); Eubank (1988)'s
weaker condition is refuted by an explicit three-stationary-point
counterexample. DS15's assumption (S) must not be weakened toward
Eubank-type conditions. Informs `OPEN-DS-MARGINS-AT-OPTIMA`.

## Levrard (2015) — read verbatim 30 August 2026 (DS15 audit)

Bibliography key `Levrard-2015`; annotation in `topics/04-vector-quantization.md`.

**Outcome: the margin condition (Definition 2.1) is a hypothesis on the law
at population optima and is never proven to hold at empirical optima** —
confirming the structural contrast with DS15, which proves a margin *fails*
at optima. Registry arXiv id corrected (1405.6672; 1310.7138 is the 2013
precursor "Margin conditions for vector quantization").
