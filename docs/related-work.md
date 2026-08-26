# Related work

Choosing a quantizer so that it preserves Fisher information is not a new idea. It sits at the
intersection of four research traditions that developed largely independently, and most of the
ingredients ScoreQuant uses are established results in one of them. This page maps that territory,
states plainly which claims are already known, and places the comparable software.

The purpose is calibration, not marketing. ScoreQuant did not invent Fisher-optimal binning, and a
reader deciding whether to use it deserves to know precisely which part is new.

## Four traditions

**Optimal experimental design.** This is where "maximize the determinant of an information matrix"
became a standard objective. Kiefer and Wolfowitz established the equivalence between D- and
G-optimality, which turns the log-determinant objective into a local sensitivity condition and
explains why \(I^{-1}\) appears as the natural metric ([Kiefer and Wolfowitz,
1960](https://doi.org/10.4153/CJM-1960-030-4)). Whittle generalized the equivalence to concave
design criteria ([Whittle, 1973](https://doi.org/10.1111/j.2517-6161.1973.tb00944.x)), and Näther
and Reinsch developed the \(D_s\) case for parameters of interest in the presence of nuisance
parameters ([Näther and Reinsch,
1981](https://doi.org/10.1080/02331888108801591)). The optimization variable in this literature is
a design measure, not a hard quantizer, but the language and the matrix criteria come from here.

**Quantization for estimation.** This line asks how to transmit a finite number of bits while
losing as little parameter information as possible. Venkitasubramaniam, Tong and Swami stated the
problem directly for distributed estimation and introduced score-function quantizers as the optimal
or benchmark structure ([CISS 2006](https://doi.org/10.1109/CISS.2006.286494)) — this is direct
prior art for the idea of quantizing the score to preserve Fisher information. Farias and Brossier
developed the scalar high-resolution theory, deriving the asymptotic information loss, the optimal
interval density, and adaptive schemes ([arXiv:1310.6945](https://arxiv.org/abs/1310.6945)). Barnes,
Han and Özgür gave a geometric characterization of Fisher information after quantization in terms
of conditional score means, solving the one-bit Gaussian location problem exactly
([Allerton 2018](https://doi.org/10.1109/ALLERTON.2018.8635899), extended in
[arXiv:1902.02890](https://arxiv.org/abs/1902.02890)); this is the closest theoretical predecessor
of the score-space formulation. Dülek proved that for exponential families a deterministic
\(K\)-level quantizer depending only on sufficient statistics exists, with a convex-polytope optimal
partition for the trace criterion ([IEEE TPAMI
2023](https://doi.org/10.1109/TPAMI.2022.3172282)) — which means polyhedral quantizer geometry is
already known and cannot be claimed as new. The classical distortion-quantization background is
[Lloyd (1982)](https://doi.org/10.1109/TIT.1982.1056489) and
[Max (1960)](https://doi.org/10.1109/TIT.1960.1057548); the detection-side analogue, sufficiency of
likelihood-ratio space for quantizer design, is [Tsitsiklis
(1993)](https://doi.org/10.1109/26.223779).

**Determinant clustering.** Determinant criteria on partitions have a long history in cluster
analysis: Friedman and Rubin's invariant grouping criteria
([1967](https://doi.org/10.1080/01621459.1967.10500923)), Marriott's practical study
([1971](https://doi.org/10.2307/2528592)), and Scott and Symons' likelihood-ratio clustering
([1971](https://doi.org/10.2307/2529003)). These typically minimize within-cluster scatter or
maximize a likelihood ratio rather than optimizing a between-cell Fisher matrix of a quantized
score, but any novelty claim about "determinant clustering" has to be narrow. The relocation-based
solver family is Hartigan's method, analyzed against Lloyd's by Telgarsky and Vattani (AISTATS,
PMLR 9, 820–827, 2010); the centroidal-Voronoi machinery is [Du, Faber and Gunzburger
(1999)](https://doi.org/10.1137/S0036144599352836), and consistency of k-means is [Pollard
(1981)](https://doi.org/10.1214/aos/1176345339).

**Inference-aware categorization.** A recent line, mostly from particle physics, optimizes
summaries or bins directly for the sensitivity of the downstream statistical analysis rather than
for a proxy loss. INFERNO trains a neural summary against a differentiable approximation of the
uncertainty of a binned likelihood ([de Castro and Dorigo,
2019](https://arxiv.org/abs/1806.04743)). ThickBrick optimizes event selection and categorization
for signal significance with an explicitly Lloyd-like iteration ([Matchev and Shyamsundar,
2021](https://arxiv.org/abs/1911.12299)). GATO and BOBR optimize multidimensional bin boundaries of
classifier discriminants by gradient descent and by Bayesian optimization respectively ([Erdmann,
Kasaraguppe and Mausolf, 2026](https://arxiv.org/abs/2601.07756)). The neighboring
simulation-based-inference literature supplies the scores themselves: the local score as a learned
summary is SALLY/SALLINO ([Brehmer, Louppe, Pavez and Cranmer,
2020](https://arxiv.org/abs/1805.12244)), building on calibrated classifier likelihood ratios
([Cranmer, Pavez and Louppe, 2015](https://arxiv.org/abs/1506.02169)). The classifier is not the
only route to the ratios: direct density-ratio estimation fits them without an intermediate
classification problem — KLIEP by Kullback-Leibler importance estimation ([Sugiyama et al.,
2008](https://doi.org/10.1007/s10463-008-0197-x)), uLSIF by unconstrained least squares
([Kanamori, Hido and Sugiyama, 2009](https://jmlr.org/papers/v10/kanamori09a.html)) — and
calibrated neural ratio estimators extend the same estimand to simulator-driven models. ScoreQuant
couples to the estimand, a ratio callback with declared provenance, never to a particular
estimation algorithm.

## Known versus new

| Statement | Status | Where it comes from |
| --- | --- | --- |
| A quantizer can be chosen to maximize Fisher information | Established | Venkitasubramaniam–Tong–Swami (2006) and the distributed-estimation line |
| The score, or a sufficient statistic, is the natural space for the quantizer | Established | Venkitasubramaniam–Tong–Swami (2006); Barnes–Han–Özgür (2018); Dülek (2023) |
| A trace-optimal multivariate quantizer can have polyhedral geometry | Established | Dülek (2023), convex-polytope optimum for exponential families |
| Normalized trace after Fisher whitening equals weighted k-means distortion | Corollary | Follows from the conditional-mean loss identity; not presented here as a theorem |
| Learned, inference-aware bins and categories | Established | INFERNO; ThickBrick; GATO/BOBR |
| Randomized rules reduce to deterministic ones for an atomless score law | Classical | [Dvoretzky, Wald and Wolfowitz (1951)](https://doi.org/10.1214/aoms/1177729689) purification |
| Optimal one-dimensional grouping chosen to minimize information loss | Established | [Cox (1957)](https://doi.org/10.1080/01621459.1957.10501411); Ogawa (1951) on optimal spacings of order statistics |
| Full-matrix \(\log\det I_B\) for hard score quantization with exact finite relocation algebra | No direct match found | The targeted search found no ready-made treatment; the most promising narrow gap |
| 1-exchange stability \(\Rightarrow\) strict self-consistent \(I_B^{-1}\)-Voronoi for the D objective | Strongest specific claim | Still awaiting a dedicated adversarial prior-art review |
| The same implication fails for profiled \(D_s\) | Boundary result | Exact rational counterexamples in the regression suite |

The defensible formulation is therefore not "we invented optimal Fisher binning". It is: ScoreQuant
studies the exact finite-sample and population geometry of **full-matrix D-optimal hard
quantization** of multivariate score space, and implements a solver that exploits that D-specific
structure — the exact rank-two relocation and its closed-form log-determinant gain, monotone
exchange with a stability certificate at termination, the exchange-stability bridge that licenses
compiling a finite partition into a reusable Mahalanobis rule, certified efficient-score upper
bounds for profiled \(D_s\), and bounded branch-and-bound global certificates on small instances.
The library packaging is part of that: the two tasks and the three input regimes stay visible in
the API instead of collapsing into a single opaque `fit`.

## Where the theory is still open

Several questions remain genuinely unresolved and are stated here rather than papered over:
complete prior-art closure for the D case, the computational complexity of the global problem for
variable dimension and cell count, population consistency of empirical D-optimal quantizers,
tightness of the deterministic relaxation for score laws with atoms, the finite geometry of the
profiled \(D_s\) case, E-optimality, how classifier miscalibration and finite training data
propagate into the retained information, and how a rule transfers across reference points or under
covariate shift.

## Software comparison

No package matches this formulation end to end. It is more useful to see where each one sits in the
pipeline "obtain a score \(\rightarrow\) build summaries or categories \(\rightarrow\) do
inference".

| Package | Pipeline stage | Objective | Relationship |
| --- | --- | --- | --- |
| MadMiner ([Brehmer et al.](https://arxiv.org/abs/1805.12244)) | Score estimation | Likelihood-ratio and score estimation for particle physics | A supplier of scores, not a bin optimizer. It can feed Door 1 or Door 3 |
| INFERNO ([de Castro and Dorigo](https://arxiv.org/abs/1806.04743)) | Summary construction | Differentiable approximation to the uncertainty of a binned likelihood | The conceptual precedent for optimizing the downstream inference objective; a neural summary rather than an exact hard quantizer |
| ThickBrick ([Matchev and Shyamsundar](https://arxiv.org/abs/1911.12299)) | Categorization | Signal-discovery significance | Algorithmically the closest classical relative — Lloyd-like iteration on hard categories — with a different criterion |
| GATO ([Erdmann et al.](https://arxiv.org/abs/2601.07756)) | Bin-boundary optimization | Binned-likelihood signal significance, differentiable GMM/sigmoid bin model | The closest modern comparator for multidimensional bin-shape optimization |
| BOBR ([Erdmann et al.](https://arxiv.org/abs/2601.07756)) | Bin-boundary optimization | Same significance objective, black-box Bayesian optimization | Same niche as GATO without a differentiability requirement |
| [OptBinning](https://github.com/guillermo-navas-palencia/optbinning) | Supervised discretization | Mathematical programming against a binary, continuous, or multiclass target | Mature production binning infrastructure; the objective is not Fisher information |
| [scikit-learn](https://scikit-learn.org/) `KBinsDiscretizer`, `KMeans` | Baseline discretization and clustering | Uniform/quantile bins, or Euclidean distortion | The natural baseline for the normalized-trace criterion after whitening, and a good initializer for the D objective, but not an optimizer of it |
| **ScoreQuant** | Categorization from scores | Full-matrix \(\log\det I_B\), profiled \(D_s\), normalized trace | Exact exchange gains, optional global certificates, an explicit split between sample partition and reusable quantizer, and a score supplied as data, a model, or a classifier |

The practical differentiation is the level of abstraction. ScoreQuant lives at the score-oracle
boundary rather than inside a domain-specific analysis workflow, so the same optimizer serves an
analytic likelihood, a linear component model, simulation-derived scores, and classifier-derived
surrogates.

## Reading path

A short sequence for holding the field in your head:

1. [Kiefer and Wolfowitz (1960)](https://doi.org/10.4153/CJM-1960-030-4) — where D-optimality comes
   from, and why \(I^{-1}\) appears in local optimality conditions.
2. [Friedman and Rubin (1967)](https://doi.org/10.1080/01621459.1967.10500923) — how old
   determinant-based partition criteria are.
3. [Venkitasubramaniam, Tong and Swami (2006)](https://doi.org/10.1109/CISS.2006.286494) — direct
   prior art on score-function quantization.
4. [Farias and Brossier (2013)](https://arxiv.org/abs/1310.6945) — how far the scalar theory can be
   pushed.
5. [Barnes, Han and Özgür (2018)](https://doi.org/10.1109/ALLERTON.2018.8635899) — the geometric
   bridge to a vector parameter.
6. [de Castro and Dorigo (2019)](https://arxiv.org/abs/1806.04743) — inference-aware optimization as
   a paradigm.
7. [Dülek (2023)](https://doi.org/10.1109/TPAMI.2022.3172282) — the prior-art boundary on quantizer
   geometry.
8. [Erdmann, Kasaraguppe and Mausolf (2026)](https://arxiv.org/abs/2601.07756) — the current
   comparator for multidimensional bin optimization.

The [bibliography](bibliography.md) lists the sources behind the statistical machinery ScoreQuant
uses directly; this page is the wider map.
