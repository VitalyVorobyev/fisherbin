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

**Round-3 resolution (30 August 2026):** FIP\(_3\) is direct prior art for the
scalar \(d=1\) retained-information ratio and Valassi's sensitivity is the
scalar score-space reduction. It is not prior art for the multivariate
determinant normalization in `INFO-D-EFFICIENCY`, and the paper gives no
optimal-cell theorem. Keep the current claim statuses; describe the scalar
restriction explicitly in publication prose.

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
## Snowballing round 3 — 30 August 2026 (bidirectional)

This was the first bidirectional citation round. All resolvable anchors in
`seeds.md` were traversed one hop backward and forward. OpenAlex supplied the
primary graph and metadata; Semantic Scholar was used only to repair missing
or rate-limited edges. Counts and source limitations are recorded in
`graph.json`.

### Fisher-information quantization and score access

- **Venkitasubramaniam, Tong & Swami (2007),** *Quantization for Maximin ARE
  in Distributed Estimation* (`Venkitasubramaniam-Tong-Swami-2007`), extends
  scalar score-function quantization to a worst-parameter ARE criterion and an
  iterative threshold design. It informs `TRACE-WHITENED-KMEANS`,
  `OPEN-D-HIGH-RATE`, and `OPEN-PARAMETER-MISMATCH`, but supplies no
  multivariate D or \(D_s\) result.
- **Barnes, Han & Özgür (2020),** *Lower Bounds for Learning Distributions
  under Communication Constraints via Fisher Information*
  (`Barnes-Han-Ozgur-2020`), carries quantized-Fisher geometry into minimax
  lower bounds, not a deterministic partition solver. It informs
  `FI-QUANT-IDENTITY` and `TRACE-WHITENED-KMEANS`.
- **Lam & Reibman (1993),** *Design of Quantizers for Decentralized
  Estimation Systems*, and **Gubner (1993),** *Distributed Estimation and
  Quantization*, are earlier scalar/distributed estimation ancestors. They
  optimize estimator performance under restricted communication models; they
  do not establish the hard multivariate conditional-score determinant
  objective. Both inform `FI-QUANT-IDENTITY` and `TRACE-WHITENED-KMEANS`.
- **Cranmer, Pavez & Louppe (2015),**
  *Approximating Likelihood Ratios with Calibrated Discriminative
  Classifiers* (`Cranmer-Pavez-Louppe-2015`), directly supports
  `CLASSIFIER-RATIO-ORACLE`. It does not propagate calibration error into
  Fisher or D/\(D_s\) loss.
- **Zhang, Blum, Kaplan & Lu (2018),** *A Fundamental Limitation on Maximum
  Parameter Dimension for Accurate Estimation With Quantized Data*
  (`Zhang-Blum-Kaplan-Lu-2018`), is direct distributed-estimation precedent
  for the alphabet/parameter-dimension rank obstruction in
  `FI-RANK-CEILING`.

### Optimal design and determinant exchange

- **Silvey & Titterington (1973),** *A Geometric Approach to Optimal Design
  Theory* (`Silvey-Titterington-1973`), proves D and \(D_s\) equivalence in
  approximate design and a convergent monotone D construction. It directly
  strengthens the attribution of `DS-CLASSICAL-DESIGN-THEORY`.
- **Silvey, Titterington & Torsney (1978),** *An Algorithm for Optimal Designs
  on a Design Space* (`Silvey-Titterington-Torsney-1978`), gives monotone
  finite-design-space algorithms. It is algorithmic precedent for
  `D-EXCHANGE-TERMINATES`, but its free design weights do not transfer to
  coupled hard-cell masses and conditional means.

### High-rate and vector quantization

- **Rakhlin & Caponnetto (2006),** *Stability of K-Means Clustering*
  (`Rakhlin-Caponnetto-2006`), is direct prior art for the
  compact-codebook/almost-minimizer rigidity used in DS16.1. Its bounded-law,
  nearest-center theorem does not cover arbitrary groupings, signed nuisance
  moments, or the profiled-information price.
- **Telgarsky & Vattani (2010),** *Hartigan's Method: k-means Clustering
  without Voronoi* (`Telgarsky-Vattani-2010`), supplies the nearest finite
  one-point-terminal geometry. It also reinforces that exchange stability is
  not a Voronoi certificate; it has no population or nuisance conclusion.
- **Zador (1982), Gersho (1979), and Bucklew & Wise (1982)** provide the
  classical high-rate scaling, cell-shape, and rigorous multidimensional
  additive-distortion templates now cited by `OPEN-D-HIGH-RATE`.
- **Gupta & Hero (2003),** *High-Rate Vector Quantization for Detection*, is
  the nearest task-aware bridge: an inference loss for binary detection admits
  high-rate point-density calculus. It still does not derive the logdet
  retained-Fisher or profiled-Schur expansion required by
  `OPEN-D-HIGH-RATE`.
- **Gray, Linder & Li (2002)** and **Lookabaugh & Gray (1989)** sharpen the
  entropy-constrained and geometric high-rate background, respectively. They
  remain additive-distortion results and are linked only to
  `OPEN-D-HIGH-RATE` in the discovery graph.

### Efficient-score compression and HEP categorization

- **Alsing & Wandelt (2019),** *Nuisance Hardened Data Compression for Fast
  Likelihood-Free Inference* (`Alsing-Wandelt-2019`), is the closest published
  representation-level antecedent to the efficient score used by
  `DS-EFFICIENT-SCORE-DOMINATION`. It preserves marginalized Fisher
  information locally/asymptotically for a continuous summary; it does not
  prove all-quantizer Loewner domination or a hard \(D_s\) upper bound.
- **Charnock, Lavaux & Wandelt (2018)** (IMNN) and **Alsing, Wandelt & Feeney
  (2018)** (DELFI+MOPED) learn or use continuous Fisher-aware summaries. They
  inform `REPRESENTATION-QUANTIZATION-LOSS` and
  `OPEN-REPRESENTATION-LOSS-ESTIMATION`, not hard-cell geometry.
- **Brehmer et al. (2020)** (MadMiner) is a practical learned-ratio/score
  pipeline informing `PROXY-TRUE-RETAINED-FI` and
  `OPEN-HEP-NUISANCE-SCALING`.
- **Wunsch et al. (2021)** and **Simpson & Heinrich (2023)** (neos) optimize
  differentiable binned/profiled inference objectives with nuisances. They
  are direct applied precedents for `DS-SCHUR` and
  `OPEN-HEP-NUISANCE-SCALING`, but rely on KDE/soft or end-to-end relaxations
  rather than exact hard score-space partitions.

## Proposed status changes — not applied

None. The round adds prior-art links and sharpens boundaries, but it does not
justify changing any claim's `status` or `literature_search_status`.
`OPEN-D-HIGH-RATE` remains open; `DS-EFFICIENT-SCORE-DOMINATION` remains an
internal project result; and Valassi (2020) precedes only the scalar
restriction of `INFO-D-EFFICIENCY`.
