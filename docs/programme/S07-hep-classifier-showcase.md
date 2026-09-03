# S07 — HEP classifier showcase

**Workstream:** W4 · **Needs:** S4 · **Parallel with:** S6 · **Status:** queued

## Goal

Close the last W4 gap: HEP has no example at all today. **S4's spike settled the dataset question
in favour of the HEP route, so the FlowCyt fallback this packet used to describe is cut and must
not be built.** Read the "HEP data spike record" section of
`docs/programme/S04-showcase-foundations.md` for the verified facts; the short version is the FAIR
Universe HiggsML Uncertainty Challenge public dataset, DOI `10.5281/zenodo.15131565`, CC-BY-4.0,
Parquet, with a 0.13 MB sample of 1,000 rows x 31 columns already committed upstream and an
explicit `tes` tau-energy-scale nuisance. **That record describes `tes` as "a factor applied
to `PRI_had_pt`"; it is the upstream docstring's summary and it is incomplete — see D3 below,
which reads the source and corrects it. Follow D3, not the Goal paragraph or the spike record.**

This session builds `examples/hep_classifier/`: a Door 3 route (classifier to ratios to scores)
through profiled \(D_s\) with the tau-energy-scale nuisance, on a committed fixture no larger than
5 MB with its hash and licence recorded. Done means the roadmap W4 gate names the provenance of
every number the example reports, not just that the example runs.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S04-showcase-foundations.md`: the "HEP data spike record" section carries the
  verified dataset facts — DOI, licence, format, sample size and shape, the nuisance list, and the
  provenance warning that the upstream GitHub repository has no licence file so the CC-BY-4.0
  claim must cite the Zenodo record. Also the Michelson example, whose analytic-nuisance arc this
  session should not duplicate.
- `examples/cell_population/`: the module shape to mirror — the only existing example built around
  a real, externally licensed dataset.
- `examples/data/README.md`: the provenance pattern a committed third-party fixture follows.
- `examples/door3_classifier.py`: the existing Door 3 (classifier to ratios to scores) pattern.
- `docs/examples/flowcyt-teaser.md`: existing FlowCyt doc page, precedent for the new doc page.
- `docs/three-doors.md`: Door 3 contract this example must match.
- `tests/test_evidence_suite.py`: pins evidence JSON; the new example's numbers register here.
- `docs/roadmap.md`: M12 W4 gate block; this session updates it to name the provenance of every
  reported number.

## Deliverables

- `examples/hep_classifier/`: Door 3 to profiled \(D_s\) with the tau-energy-scale nuisance,
  following the module shape of `examples/cell_population/` (a `data.py` contract layer, a
  `scores.py` classifier-to-score bridge, an `experiment.py`, a `figures.py`).
- A committed fixture, 5 MB or smaller, with its hash and the CC-BY-4.0 licence and Zenodo DOI
  recorded alongside it, following `examples/data/README.md`'s existing provenance pattern.
- `docs/usecases/hep/`: doc page for the example.
- A notebook (`examples/notebooks/hep_classifier.ipynb`, matching the existing convention).
- Evidence JSON pinned in `tests/test_evidence_suite.py`.
- `docs/roadmap.md` W4 gate text names the provenance (dataset, licence, fixture hash) of every
  number the example reports.

**Cut:** the FlowCyt three-interface fallback (`examples/cell_population/integration.py`). S4
confirmed a usable HEP dataset, so building the fallback would add a second FlowCyt example that
no gate asks for.

## Done criteria

- `examples/hep_classifier/` exists, is present in the mkdocs nav, and executes in fast mode under
  both test tiers.
- The committed fixture is 5 MB or smaller and its hash, licence (CC-BY-4.0) and Zenodo DOI are
  recorded in the example's doc page or a sibling file, citing the Zenodo record and not the
  unlicensed upstream GitHub path.
- Evidence JSON for the example is pinned in `tests/test_evidence_suite.py`.
- `docs/roadmap.md` W4 gate names the provenance of every number in the example's output.
- Full handoff gate green (see Verification).
- roadmap M12 table shows S07 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Design the statistical arc (which parameters are of interest, how `tes` enters the score, what the naive baseline is) | orchestrator inline (never `fable`) | written spec appended to this packet before code starts |
| Implement the example script, notebook, doc page, and evidence pinning | sonnet | source and doc diff |
| Verify fixture size, hash, and licence; cite the Zenodo DOI not the GitHub path | haiku | verification log |
| Update `docs/roadmap.md` W4 gate text with provenance | haiku | roadmap diff |
| Run gates, add nav entry, report failures verbatim | haiku | gate output |

## Design decisions — the statistical arc

Written inline before implementation, per the delegation table. Everything below is a decision
the implementation must follow, not a suggestion; where a number is left open it says what
measurement settles it.

### D1 — The measurement, and why the backgrounds are collapsed

The model is an extended linear intensity over the fixture's events,

$$\lambda(x;\mu,\nu,\alpha)=\mu\,s(x;\alpha)+\nu\,b(x;\alpha),$$

with reference point \(\theta_0=(1,1,1)\) and three parameters:

| Parameter | Meaning | Role |
|---|---|---|
| \(\mu\) | `htautau` signal rate | **of interest** |
| \(\nu\) | combined background rate | nuisance (normalization) |
| \(\alpha\) | `tes`, the tau energy scale | nuisance (shape) |

`ztautau`, `ttbar` and `diboson` are collapsed into one background component. This is forced, not
chosen: S4's spike record measured 26 `ttbar` and 4 `diboson` rows in the committed sample, which
cannot support separate normalizations. The doc page must say so and cite the row counts, because
a reader who knows the challenge will expect the three background normalizations the upstream
`systematics.py` exposes.

### D2 — The score has three columns, and they come through two different ratio doors

This is the decision the packet asked for, and the two halves are deliberately not built the same
way.

**Columns 0 and 1 — the rates — are closed form given the ratio.** A calibrated two-class
classifier separating `htautau` from the combined background gives posteriors \(\eta\) under
training priors \(\pi\); the ratios are \(r_k=\eta_k/\pi_k\), and
`IntensityParameterization(coefficients=[1.0, 1.0])` maps them to \(r_k/\sum_j\theta_j r_j\),
keeping all \(K\) columns including the overall-normalization direction. Built with
`DensityRatioScore.from_classifier`. A rate parameter's score is *available analytically* once the
ratio is known, so it must **not** be finite-differenced — doing so would inject classifier noise
into the one direction that does not need it.

**Column 2 — `tes` — has no closed form, and is what the central-difference door exists for.**
Because `tes` is a deterministic transformation of the features rather than a set of pre-baked
variation samples, the \(\alpha=1\mp\delta\) samples are *constructed* from the same fixture rows
by applying the transformation. A calibrated binary classifier separating the minus sample from the
plus sample estimates \(\log(p_+/p_-)\), and `CentralLogRatioScore` applies the prior correction
and divides by \(2\delta\). This is the library's least-exercised provider and it has no example
today; S4 made its `three-doors.md` fence executable, and this session gives it a real dataset.

**Composition.** `ScoreProvider` is an open protocol — its own docstring shows a caller-defined
implementation and says the built-in providers are "not a closed list of what is allowed" — so the
example defines a small provider that delegates to both and concatenates their columns. It carries
`ScoreSchema(("mu_htautau", "nu_background", "tes"))`, so the criterion can be written
`ProfiledDOptimality(interest=("mu_htautau",))` and reads as the measurement it is. Its provenance
is `kind="estimated_ratio"`, which is the only honest value: both halves are classifiers, and
neither may claim exact Fisher semantics.

### D3 — What `tes` actually does, verified against upstream, and three corrections

I read `ingestion_program/systematics.py` in `FAIR-Universe/HEP-Challenge` directly rather than
trusting the summary. **S4's spike record — and this packet's own Goal paragraph — describe `tes` as
"a factor applied to `PRI_had_pt`". That is the upstream docstring's summary and it is incomplete.**
Three corrections follow, and each one would have produced a plausible-looking artifact if missed.

**C1 — `tes` moves three primary columns, not one.** `mom4_manipulate` scales `PRI_had_pt` by `tes`
and then *recoils the missing transverse momentum against it*: the tau four-vector is rescaled at
fixed mass by \((1-\text{tes})/\text{tes}\), added to the MET vector, and `PRI_met` and
`PRI_met_phi` are recomputed from the result. Shifting `PRI_had_pt` alone leaves MET inconsistent
with the event, and the minus/plus classifier would learn that inconsistency — a column 2 with a
credible magnitude and no physical meaning.

**C2 — `postprocess` drops events, so the shifted samples are not row-aligned.** After the shift
upstream applies `PRI_had_pt > 26` and drops the rows that fail. Under `tes = 1 - delta` some events
fall below the threshold and disappear; under `1 + delta` they survive. That is an *acceptance*
change, the density ratio \(p_+/p_-\) diverges at the threshold, and a central difference over
1,000 events cannot resolve it. **The example therefore runs the transformation with
`dopostprocess=False`**, so `tes` is a pure deformation of the features at fixed selection and the
estimand is well defined. The doc page states this as a modelling choice with its reason: the
example measures the *shape* sensitivity to the tau energy scale, not the acceptance sensitivity.

**C3 — every variant must go through the same code path, including the nominal one.**
`mom4_manipulate` rounds all primary columns to three decimals unconditionally, at the end, whether
or not a shift was requested. A nominal matrix taken straight from the Parquet file would be
unrounded while the shifted ones were rounded, and a classifier can learn a rounding lattice. The
nominal variant is produced by calling `systematics(..., tes=1.0)` like every other.

**C4 — the derived columns are recomputed upstream, so keep all 28 features.** I first wrote this
section requiring `PRI_*` columns only, reasoning that stale `DER_*` values would reintroduce C1.
Running the code showed the opposite: `systematics()` ends by returning `DER_data(data_syst)`, which
recomputes every derived quantity from the shifted primaries. Dropping them would have thrown away
the most `tes`-sensitive discriminants in the dataset for no reason. **Take whatever
`systematics()` returns, in full.**

**Measured, not assumed.** Running the pipeline on the 1,000-row sample at
`tes` in `{0.90, 0.95, 1.00, 1.05, 1.10}` with `dopostprocess=False`:

| Fact | Measured |
|---|---|
| Rows in every variant | 1,000 — row-aligned, so the pairs match |
| Feature columns responding to `tes` | **10 of 28** |
| Largest responses (median relative change, 0.90 to 1.10) | `PRI_met` 0.31, `DER_mass_transverse_met_lep` 0.30, `PRI_had_pt` 0.22, `PRI_met_phi` 0.18, `DER_pt_ratio_lep_had` 0.18, `DER_mass_vis` 0.11, `DER_sum_pt` 0.10, `DER_met_phi_centrality` 0.03 |
| Rows `postprocess` would have dropped at `tes = 0.90` | **169 of 1,000** — C2's acceptance effect is a 17% change, not a rounding detail |
| Sample composition | `ztautau` 634, `htautau` 336, `ttbar` 26, `diboson` 4; weights all strictly positive, sum 1.0514e6 |
| Upstream commit used | `31816a0d8c8dda03d4b28d9e824674821756962b` (2025-05-15) |

Two consequences worth stating for the implementer. The deformation is **large** — a 10-30% median
change in the responsive columns — so the minus/plus classifier will not be starved of signal, and
my earlier worry that this column would be noise-limited at fixture scale was wrong. And because it
is that large, **bias, not variance, is the binding constraint on \(\delta\)**, which is what D4 now
reflects.

**Consequence for the fixture: the variants are precomputed offline and committed.** The build
script fetches upstream `systematics.py` at a recorded commit, applies it at each `tes` value in a
throwaway environment (`uv run --with pandas --with pyarrow`), and commits the resulting feature
matrices. Nothing is vendored — the repository carries no licence file, so its code is used, not
copied — and the example needs neither the upstream code nor a reimplementation of the four-vector
algebra at runtime. Reimplementing `V4.scaleFixedM` and the MET recoil in this repository was the
alternative and it is rejected: it is thirty lines whose correctness could only be checked against
the upstream output we can simply use directly.

Commit seven matrices, at the `tes` values D4 lists. At 1,000 rows and 28 feature columns each is
~224 KB, so all seven sit far inside the 5 MB ceiling.

**Provenance, stated precisely rather than tidily.** The bytes come from
`input_data/FAIR_Universe_HiggsML_data.parquet` in `FAIR-Universe/HEP-Challenge`, at a recorded
commit. That repository has no licence file. The licence claim therefore rests on the Zenodo record
for the dataset the sample is drawn from — DOI `10.5281/zenodo.15131565`, CC-BY-4.0 — and the
provenance file must say all three things: where the bytes came from, that the code repository is
unlicensed, and which record the licence is claimed under. Do not compress this into "CC-BY-4.0"
and a DOI.

### D4 — \(\delta\), and the stability check that has to accompany it

A central difference trades bias against classifier noise, and at 1,000 rows the noise is real: the
minus and plus samples are the same events under a small deformation, so they are nearly
identical distributions. Requirements:

- Report \(\delta\), the weighted out-of-fold AUC of the minus/plus classifier, and the fraction of
  events whose calibrated posterior is within 0.01 of 0.5.
- Run the score at \(\delta\) and \(\delta/2\) and report the agreement. **A disagreement is a
  result to report, not a parameter to tune away**: if the two do not agree, the doc page says the
  `tes` column is noise-limited at fixture scale and the walkthrough inherits that caveat.
- **Headline \(\delta = 0.05\)**, with the score recomputed at \(0.025\) and \(0.10\) so the
  evidence carries a three-point convergence study rather than a single unfalsifiable number. The
  fixture therefore commits seven variants, `tes` in
  `{0.90, 0.95, 0.975, 1.00, 1.025, 1.05, 1.10}` — about 1.6 MB in total, well inside the ceiling.
- **State plainly that \(\delta\) is a numerical differentiation step, not the physical
  tau-energy-scale uncertainty** — which is nearer 1-3%. The score is the derivative at
  \(\alpha=1\) whatever prior width \(\alpha\) carries, and a HEP reader who sees these numbers
  without that sentence will read them as a physics claim.
- The variants are row-aligned by C2, so all 1,000 events appear in both classes: 2,000 training
  rows, matched pair by pair.

### D9 — Two failure modes the spike found, both of which produce plausible wrong numbers

I ran the whole arc end to end on the built fixture before delegating. Both of these were bugs in
my own first attempt, neither raises an error, and both yield a number a reader would accept.

**F1 — the minus/plus folds must be grouped by event, or the classifier inverts.** The two variants
are the *same* 1,000 events transformed, and eighteen of the twenty-eight columns do not respond to
`tes` at all. Under an ordinary stratified split, event \(i\)'s minus copy and plus copy land in
different folds, so the model memorizes the event from its static columns and returns the label of
the copy it was trained on — the opposite one. Measured out-of-fold AUC with a plain
`StratifiedKFold`: **0.3424**, below chance. With one fold id per *event*, reused by both copies:
**0.5733**. An implementer who sees 0.34 and "fixes" it by flipping a sign gets a beautifully
inverted score column.

**F2 — training on raw MC weights makes the signal invisible.** The weighted signal fraction is
\(f = 0.00099\): background events carry weights near 1582 and signal near 3. A classifier trained
with those weights sees essentially no signal. Train instead with **per-class normalized weights**
and declare training priors \((0.5, 0.5)\), so \(r_k=\eta_k/\pi_k\) still recovers the ratio of the
weighted class densities; the physical rate ratio enters through
`IntensityParameterization(coefficients=[1-f, f])`, not through the priors. This is also what the
library's own doctrine requires — importance ratios are source weights, never provider inputs. The
MC weights are carried on the `ScoreSample`, where they belong. Measured signal AUC after the fix:
**0.8316** (weighted).

**Reference numbers from the spike**, for the implementer to land near — they are a target, not a
value to reproduce exactly, since the final example fixes seeds and budgets of its own:

| Quantity | Spike value |
|---|---|
| Weighted signal AUC (out of fold) | 0.8316 |
| Weighted signal fraction \(f\) | 0.00099 |
| `tes` minus/plus AUC, grouped folds, \(\delta=0.05\) | 0.5733 |
| \(\sum_k \theta_k s_k\) over the rate columns | identically 1 (std 0.0) — the exact linear dependence the intensity map implies, and a useful self-check |
| Effective rank at 6 bins | 3 |
| Profiled \(D_s\) geometric-mean retention, 6 bins, `DExchangeConfig(seed=11)` | 0.529 |

The fixture is already built and committed at `examples/data/hep_higgsml_fixture.npz` (0.59 MB) by
`examples/hep_classifier/fixture.py`, with provenance in the sibling `.json`. **Do not rebuild it**;
it needs the network and two packages the project does not depend on.

### D5 — The naive baselines are what a physicist actually does

Two, both scored on the *same* criteria as the ScoreQuant labels so the columns compare:

1. **Classifier-quantile bins** — equal-frequency bins of the signal posterior \(\eta_s\) at the
   same bin budget. This is the standard "bin the network output" analysis.
2. **A single threshold cut** — the two-bin signal-region/control-region split at the \(\eta_s\)
   quantile maximizing \(S/\sqrt{B}\), the most recognizable baseline there is.

### D6 — The claim under test, stated as a prediction

Binning on \(\eta_s\) alone should lose profiled information, because \(\eta_s\) is built to
separate signal from background and knows nothing about \(\alpha\); the region where the signal
concentrates is also where the tau energy scale moves events most, so profiling over \(\alpha\)
eats what those bins carry. ScoreQuant optimizes in the three-dimensional score space where the
\(\alpha\) direction is explicit.

**This is a prediction, not a result.** If the measured gap is small, or the wrong way round, the
example reports that. The programme has precedent — `/showcase` and the blog both carry negative
results — and a walkthrough that quotes a number the run did not produce is worth nothing.

### D7 — What every labeling is scored on

Each labeling is reported **twice**: full-D retention and profiled \(D_s\) retention. The whole
point is that the two criteria disagree, and one column cannot show that. `efficient_score_bound`
supplies the certified ceiling alongside, as `examples/nuisance_profiled_ds.py` already does.

Solvers follow the generated compatibility matrix: `DExchangeConfig` with `ProfiledDOptimality` for
`optimize_partition`, and `SoftVoronoiConfig` for `fit_quantizer` — profiled \(D_s\) has no compile
bridge, so the reusable rule is the soft fit.

### D8 — Mechanics that are not negotiable

- **No new runtime dependency.** Parquet is read once, offline, at fixture-build time
  (`uv run --with pyarrow`, touching neither the project environment nor `uv.lock`); the committed
  artifact is `.npz`, exactly as `examples/data/flowcyt_fixture.npz` is.
- **The classifier is trained inside the example** — resolving the packet's open decision. At 1,000
  rows it is cheap, and committing posteriors alongside the fixture would hide the step the example
  is teaching.
- **Out-of-fold posteriors with a deterministic fold assignment**, so no event's score comes from a
  model that saw it, plus the temperature calibration `examples/cell_population/scores.py` already
  uses. Both classifiers, not just the signal one.
- **Weights are the MC event weights.** They must be nonnegative and finite with at least one
  positive; the fixture builder asserts this and records how many rows, if any, were dropped.
- Deterministic seeds throughout. Fast mode shrinks the classifier and solver budgets and the bin
  sweep — never the fixture, whose hash is pinned.

## Verification

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
```

## Open decisions

- **Resolved by S4:** HEP is built and the FlowCyt fallback is cut.
- The exact event/feature subset that keeps the fixture at or under 5 MB, and whether the upstream
  0.13 MB sample is enough. It carries all four processes but only 26 `ttbar` and 4 `diboson` rows,
  so it supports the `tes` nuisance (which acts on every event) and not the background-normalization
  nuisances. If a larger fixture is wanted, S4's record notes the cost: one 15.1 GB download from
  the Zenodo release.
- Whether the classifier is trained inside the example or its calibrated posteriors are committed
  alongside the fixture. `examples/cell_population/scores.py` trains a
  `HistGradientBoostingClassifier` at run time; at 1,000 rows that is cheap, so training in-example
  is probably right, but the fast-mode budget decides.

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
