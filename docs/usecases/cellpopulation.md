# Learning information-aware cell gates: a complete FlowCyt study

Flow cytometry produces a cloud of cells, not a row of population fractions.
Each cell carries twelve marker measurements. The practical result, however, is
often only six numbers: the proportions of T cells, B cells, monocytes, mast
cells, hematopoietic stem/progenitor cells (HSPCs), and everything else.

This study asks a deliberately hard compression question:

> Can we replace 200,000 held-out twelve-dimensional test events with a few
> integer bin counts and still recover the population fractions?

The answer on the frozen FlowCyt experiment is yes. Eight learned hard bins
retain 94.4% of the held-out Fisher information and estimate the five target
fractions with a macro RMSE of 0.00226. A marker-space k-means partition with
the same eight outputs reaches 0.0289 RMSE and 13.8% Fisher efficiency.

Those numbers are not fixture results. They come from all 30 FlowCyt patients,
with 20 reference patients and ten untouched test patients. The reproducible
bounded study contains 600,000 real cells sampled from 21,254,866 upstream
events.

![Complete cell-population workflow](assets/cell_population_workflow.png)

The important boundary is visible in the figure. The classifier is not
FisherBin. Neither is the downstream mixture likelihood. FisherBin receives
score vectors and returns a frozen hard partition. This makes the example useful
for cytometry users and for developers adapting the same API to another domain.

## Result at a glance

The predeclared acceptance gate required learned score partitions to beat the
median random score partition in held-out D-efficiency for at least five of six
bin counts, and to be no worse than marker k-means in population RMSE for at
least four. The result was 6/6 for both tests.

| Bins | Soft Voronoi RMSE | Score k-means RMSE | Marker k-means RMSE | Random RMSE median | Soft D-efficiency | Random D-efficiency median |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 0.00429 | 0.00440 | 0.04186 | 0.03338 | 0.427 | 0.016 |
| 8 | 0.00226 | 0.00237 | 0.02889 | 0.02404 | 0.944 | 0.153 |
| 10 | 0.00228 | 0.00236 | 0.04758 | 0.01644 | 0.957 | 0.243 |
| 15 | 0.00231 | 0.00228 | 0.03332 | 0.01057 | 0.977 | 0.319 |
| 20 | **0.00223** | 0.00230 | 0.03220 | 0.00746 | 0.986 | 0.455 |
| 30 | 0.00249 | 0.00253 | 0.04990 | 0.00629 | **0.993** | 0.472 |

Eight bins are the useful knee in this experiment. Moving to 20 bins gives the
lowest observed RMSE, but the gain is only \(3.3\times10^{-5}\), while the
held-out minimum occupancy falls from 25 cells to zero. Thirty bins preserve
more local information but do not improve the downstream estimate. More bins
are not automatically better.

![Full FlowCyt held-out results](assets/cell_population.png)

The lower-left panel shows each estimated target fraction against the expert
fraction for the ten test patients. The lower-right panel is a two-dimensional
view of a five-dimensional learned partition; the colors are hard bin labels,
not cell labels.

The complete numeric record is committed as
[`cell_population.json`](assets/cell_population.json). It includes every
method/bin result, per-patient estimates, calibration and shift diagnostics,
uncertainty arrays, run settings, timings, source provenance, and acceptance
decisions.

## The real data behind the experiment

FlowCyt contains 30 bone-marrow samples and five expert-annotated target
populations. We retain the remaining cells as a sixth `other` component. This
matters: removing `other` using the expert labels would leak the answer before
inference starts.

The public corpus stores every patient/population pair in a separate FCS file.
Downloading and unpacking the complete archive is unnecessary for this bounded
study. The acquisition command reads FCS metadata first, allocates exactly
20,000 cells per patient in proportion to the upstream component totals, and
then range-reads 16 deterministic strata within every nonempty component.
Largest-remainder allocation keeps every sampled population fraction within
\(3.4\times10^{-5}\) of its full-file fraction.

This is component-stratified acquisition, not label-blind acquisition. The
expert component totals determine how many rows are read so that rare classes
are not lost to coarse network sampling. Once the 600,000-row dataset is
assembled, test labels are absent from classifier fitting, score calibration,
partition learning, template estimation, and mixture inference. They return
only for the final comparison with expert fractions.

![Patient composition and calibration diagnostics](assets/cell_population_diagnostics.png)

The shaded bars are the ten test patients. The target composition varies
substantially: T cells range from roughly 2.7% to 17.3% across the cohort, while
mast cells are often below 0.02%. This is one reason an ordinary random row split
would be misleading. The split must happen by patient.

The exact frozen patient split is:

- reference: 1, 2, 3, 4, 7, 10, 12, 13, 14, 16, 17, 18, 19, 21, 22, 24, 25, 26, 27, 29;
- test: 5, 6, 8, 9, 11, 15, 20, 23, 28, 30.

Within the reference cohort, five four-patient folds produce out-of-fold score
predictions. Disjoint deterministic row roles are then used for partition
fitting, validation diagnostics, and bin-template estimation. Validation rows
never affect gradients, stopping, or checkpoint selection.

## From class probabilities to mixture scores

Let \(p_k(x)\) be the marker density of population \(k\). A patient is modelled
as

\[
p(x\mid\theta)=\sum_{k=1}^{6}\theta_k p_k(x),
\qquad \theta_k\geq 0,
\qquad \sum_k\theta_k=1.
\]

Only five fractions are independent. Taking `other` as the reference component
gives five score directions at the reference composition \(\theta_0\):

\[
s_a(x)=
\frac{p_a(x)-p_6(x)}
     {\sum_k\theta_{0k}p_k(x)},
\qquad a=1,\ldots,5.
\]

The component densities are not known analytically. We estimate their ratios
with a patient-cross-fitted `HistGradientBoostingClassifier`. If \(q_k(x)\) is
a class posterior learned with training prior \(\pi_k\), then

\[
\frac{p_k(x)}{p_{\text{train}}(x)}=\frac{q_k(x)}{\pi_k}.
\]

The common event density cancels in the score formula. This is the key bridge:
we can build the five statistical score coordinates without fitting a general
twelve-dimensional density model.

Every classifier fold is trained without the patient it predicts. One
multiclass temperature is fitted from the out-of-fold probabilities using equal
patient/class influence. The fitted temperature is 2.219, balanced accuracy is
0.941, balanced log loss is 0.211, and expected calibration error is 0.029.
The reliability plot still shows miscalibration in sparse intermediate-confidence
bins. Fisher information does not make an upstream score estimator correct.

## The FisherBin API boundary

This use case starts from externally estimated scores, so `fit_scores` is the
right entry point:

```python
partition = fb.fit_scores(
    reference_scores[partition_rows],
    weights=integration_weights,
    validation_scores=reference_scores[validation_rows],
    validation_weights=validation_weights,
    n_bins=8,
    config=fb.SoftVoronoiConfig(
        seed=2026,
        n_init=4,
        max_steps=160,
    ),
)

test_bins = partition.predict(test_scores)
held_out_report = partition.evaluate(test_scores)
print(held_out_report.geometric_mean_retention)
```

There are five practical API rules hidden in this short block:

1. Pass raw statistical scores. Do not center them; the origin has statistical
   meaning.
2. Use nonnegative measure weights to define the reference integration measure.
   Here they give every patient equal influence within a class and reproduce
   \(\theta_0\) across classes.
3. Treat validation as a diagnostic. FisherBin deliberately does not use it to
   choose centers.
4. Freeze the result and call `predict` on scores in the same parameter order.
5. Inspect both information and occupancy. A high D-efficiency does not prevent
   a held-out bin from becoming empty.

If an application already has evaluated linear components, use
`fit_components`; if it owns callable component functions on physical variables,
use `fit`. This example should not produce a cytometry-specific public API. A
future library change is welcome when it represents a generic statistical
contract rather than FlowCyt preprocessing or classifier choices.

## Turning hard labels into fractions

After the partition is frozen, an independent labelled reference subset
estimates the template matrix

\[
A_{jk}=P(B_j\mid k).
\]

Templates are averaged per patient so that a large sample cannot dominate the
cohort. A Jeffreys pseudocount of \(1/2\) prevents an unseen class/bin pair from
making the likelihood exactly zero. For test-patient bin counts \(n_j\), the
downstream likelihood is

\[
\log L(\theta)=
\sum_j n_j\log\left(\sum_k A_{jk}\theta_k\right).
\]

The example solves this concave simplex problem with deterministic EM. Local
covariance is computed in the five free directions and lifted back to all six
fractions. Singular directions are projected with a pseudoinverse; no ridge is
allowed to invent information. Every reported patient likelihood converged; the
slowest learned-partition fit required 1,198 iterations at five bins.

This likelihood is application code under `examples/cell_population/`. It
consumes the generic hard labels but is not part of FisherBin's public API.

## What was compared

Every hard method receives the same number of outputs and feeds the same
downstream likelihood:

| Representation | Question it answers |
| --- | --- |
| Score k-means | How strong is weighted clustering after Fisher whitening? |
| Soft Voronoi | Does direct differentiable D-optimal fitting help? |
| Marker k-means | Is ordinary clustering in twelve-marker space sufficient? |
| One leading score direction | How much is lost by a one-dimensional gate variable? |
| Two marker-PCA coordinates on a grid | How does naive axis-aligned gating behave? |
| Random score Voronoi, 20 repeats | Is score space alone enough without learning centers? |
| Unbinned score likelihood | What happens when the calibrated density ratios are trusted directly? |

The near equality of score k-means and soft Voronoi is a useful result. The
Fisher transform already supplies a strong geometry, and weighted k-means is a
competitive default here. The study supports score-aware partitioning; it does
not establish universal superiority of one optimizer.

The unbinned likelihood reaches 0.0135 macro RMSE, worse than every learned hard
partition. This does not mean that discarding data creates information. The
unbinned fit trusts the classifier density ratios directly, while the binned
pipeline re-estimates \(P(B_j\mid k)\) from independent labelled reference rows.
Hard bins therefore act as a low-dimensional recalibration and regularizer for
an imperfect score model. Fisher retention measures local compression loss for
the supplied scores; downstream bias can still move differently.

## Per-population behavior

At the eight-bin operating point, the held-out RMSE values are:

| Population | RMSE |
| --- | ---: |
| T cells | 0.00393 |
| B cells | 0.00118 |
| Monocytes | 0.00272 |
| Mast cells | 0.00021 |
| HSPCs | 0.00328 |
| Other | 0.00757 |

The small absolute mast-cell RMSE needs care. The true mast fraction is usually
only a few events in a 20,000-cell patient sample, and some patients have none
after proportional rounding. Absolute RMSE therefore looks small even when the
relative error is poor. This is a general warning for rare mixture components:
one summary number cannot replace the per-class table.

## Uncertainty: where the local calculation works and fails

For the 30-bin partition, we compare the likelihood's local Fisher standard
errors with 200 multinomial bootstrap refits of the frozen bin-count pipeline.

![Fisher and bootstrap uncertainty](assets/cell_population_uncertainty.png)

The median predicted/bootstrap ratios are 1.012 for T cells, 1.141 for B cells,
1.066 for monocytes, 1.253 for HSPCs, and 0.976 for `other`. This is good local
agreement for a deterministic count likelihood.

Mast cells fail visibly. Their fitted fraction often sits exactly at zero, so
the nonparametric bootstrap also collapses at the simplex boundary. The interior
quadratic Fisher approximation remains nonzero and its median ratio becomes
meaningless. The correct conclusion is not to patch the denominator. Boundary
intervals or a constrained likelihood-ratio construction are needed for that
population.

## Patient shift and empty bins

The test cohort is measurably shifted even though it comes from the same
benchmark. After the frozen reference transform, the median absolute marker
shift is 0.123 robust-scale units, the maximum channel shift is 0.225, and the
mean score shift has Euclidean norm 0.448.

At 20 and 30 bins, at least one learned bin is empty on the held-out cohort even
though D-efficiency remains above 0.985. That combination is possible because
the remaining occupied bins preserve the five informative score directions.
Operationally, however, empty bins are a warning about transport and template
stability. This is another reason to prefer eight bins for this dataset.

## Reproduce the research

Install the complete development environment:

```bash
uv sync --all-extras --all-groups --locked
```

For the fast CI-scale integration workflow, use the committed 34,554-cell
fixture:

```bash
JAX_ENABLE_X64=1 MPLBACKEND=Agg \
  uv run python -m examples.cell_population \
  --fixture examples/data/flowcyt_fixture.npz \
  --quick
```

For the complete all-patient study, first build the ignored 600,000-cell sample
directly from the public FCS files:

```bash
uv run python -m examples.cell_population \
  --download-sample flowcyt-results/flowcyt_sample_20000.npz \
  --max-per-patient 20000 \
  --sample-blocks 16 \
  --download-workers 12
```

Then run the frozen research settings:

```bash
JAX_ENABLE_X64=1 MPLBACKEND=Agg \
  uv run python -m examples.cell_population \
  --fixture flowcyt-results/flowcyt_sample_20000.npz \
  --full \
  --bins 5 8 10 15 20 30 \
  --output-dir docs/usecases/assets
```

The generated sample SHA-256 is
`a08e9bf183fe32b913e155d413eeacfdb65c7f99017a42e69c4b91bdde20d987`.
On an Apple M4 Pro, the numerical study took 58.2 seconds and reached 1.40 GiB
peak resident memory. The score model and score construction consumed 26.3
seconds; all six partition/baseline stages consumed another 31.5 seconds. These
timings exclude network acquisition and documentation rendering.

The [FlowCyt paper](https://proceedings.mlr.press/v248/bini24a.html) describes
the benchmark and expert populations. The data and derived samples are licensed
under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/),
separately from FisherBin's MIT-licensed code. The generated manifest records
the source URLs, file totals, sampling settings, and digest.

## Developer map

- `data.py` freezes patient identities, schema, robust preprocessing, and local
  loaders.
- `fixture.py` parses FCS metadata and performs deterministic remote range
  sampling.
- `scores.py` owns cross-fitting, temperature calibration, density-ratio
  conversion, simplex scores, and integration weights.
- `experiment.py` freezes row roles, fits partitions and baselines, runs the
  held-out likelihoods, and records evidence.
- `likelihood.py` estimates bin templates and solves binned/unbinned mixture
  fits.
- `figures.py` renders all committed illustrations from the machine-readable
  result.
- `tests/test_cell_population.py` covers schema, sampling, score identities,
  cross-fitting, likelihood recovery, chunked prediction, and the standard
  integration path.

All of this remains example code because its data model and evaluation protocol
are specific to the study. The reusable object is the score-space hard partition
and its information report.

## What this study establishes

On this frozen all-patient sample, a handful of score-aware hard gates preserve
the parameter information that ordinary marker-space partitions miss. Eight
bins are already enough for a practical result. The study also shows the limits
clearly: score calibration matters, high information retention does not prevent
empty transported bins, and local Fisher errors fail for fractions on the
simplex boundary.

That combination is the useful result. FisherBin is not a classifier and not a
mixture fitter. It is the compression layer between them, and this case shows
how to build, test, diagnose, and reproduce that layer on real data.
