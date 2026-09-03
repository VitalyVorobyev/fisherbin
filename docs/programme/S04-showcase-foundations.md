# S04 — Showcase foundations (Michelson phase, NumPy example, HEP data spike)

**Workstream:** W4 · **Needs:** S3 · **Parallel with:** S6 · **Status:** done

## Goal

Close two of the four gaps in W4's per-input-route showcase gate and de-risk the third. Today the
analytic `ScoreFunction` route and the NumPy backend have no example at all, and
`CentralLogRatioScore` is documented but never executed in the docs. This session builds one
example that covers both the `ScoreFunction` route and the NumPy backend at once
(Michelson fringe phase against a fringe-frequency nuisance, D vs profiled D_s), adds one
executed
`CentralLogRatioScore` fence to `docs/three-doors.md`, and spikes whether a HEP dataset is usable
for S7 (HiggsML Uncertainty Challenge first, then ATLAS Open Data, then MadMiner tutorial
outputs). Done means the new example runs in fast mode in both test tiers and the S7 dataset
question has a recorded answer, not an open one.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S03-library-internals-refactor.md`: S3 closing report; this session must build
  against the post-refactor API, not the pre-refactor one.
- `examples/gaussian_location.py`: closest existing example for statistical-design pattern.
- `examples/nuisance_profiled_ds.py`: existing profiled D_s pattern to reuse for the nuisance.
- `docs/examples/index.md`: current example index; the new page joins this list.
- `docs/three-doors.md`: holds the `CentralLogRatioScore` fence this session must make executable.
- `tests/test_evidence_suite.py`: pins evidence JSON; the new example's numbers register here.
- `docs/adr/0018-explicit-multi-backend-execution.md`: NumPy backend contract this example must
  demonstrate via `ExecutionConfig(backend="numpy")`.
- `mkdocs.yml`: nav entry for the new example page.
- `docs/roadmap.md`: M12 W4 gate block; this session's closing report is where the roadmap names
  the S7 dataset choice.

## Deliverables

- `examples/michelson_phase.py`: analytic `ScoreFunction` example, D vs profiled D_s with an
  explicit nuisance parameter, run on `ExecutionConfig(backend="numpy")`.
- `docs/examples/michelson-phase.md`: doc page for the example, added to the mkdocs nav.
- A notebook for the example (paired with the doc page, matching the existing example pattern).
- Evidence JSON for the new example pinned in `tests/test_evidence_suite.py`.
- One executed `CentralLogRatioScore` code fence added to `docs/three-doors.md`.
- HEP data spike: for each candidate dataset (HiggsML Uncertainty Challenge, ATLAS Open Data,
  MadMiner tutorial outputs, in that priority order), record URL, licence, size, and nuisance
  parameters, verified by actually fetching the data, not by reading its landing page. This record
  lives only in the S04 closing report, not in a separate repo file.

## Done criteria

- `examples/michelson_phase.py` and its doc page exist and the doc page is present in
  `mkdocs.yml` nav.
- The example executes in `SCOREQUANT_EXAMPLE_FAST` mode under both `tests/test_notebooks.py` and
  the docs-execution tier.
- The `CentralLogRatioScore` fence in `docs/three-doors.md` executes under
  `tests/test_docs_snippets.py`.
- `tests/test_evidence_suite.py` includes and pins the new example's evidence JSON.
- The S04 closing report names a usable HEP dataset (or states plainly that none of the three
  candidates is usable, with the reason for each).
- Full handoff gate green (see Verification).
- roadmap M12 table shows S04 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Design the Michelson statistical example (nuisance structure, D vs profiled D_s comparison) | orchestrator inline (never `fable`) | written spec appended to this packet before code starts |
| Implement the example script, notebook, doc page, and evidence pinning | sonnet | source and doc diff |
| Make the `CentralLogRatioScore` fence in `docs/three-doors.md` executable | sonnet | doc diff |
| Fetch and verify each HEP dataset candidate (URL, licence, size, nuisance parameters) | haiku | fetch log and verdict per dataset |
| Run gates, add nav entry, report failures verbatim | haiku | gate output |

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

- **Resolved 3 September 2026: what the `CentralLogRatioScore` criterion was actually asking
  for.** The done criterion reads "the fence executes under `tests/test_docs_snippets.py`", and
  that was already true before the session: the fence was unmarked and valid Python. What it did
  *not* do was reach a fit — it called `central_score.score(...)` and bound the raw array, so
  alone among the doors on the page it produced no result object. That is the gap the criterion
  was written for, and it is what was closed: the fence now fits a quantizer through the paired
  classifier and reports `information_kind == "supplied_score_surrogate"`, which makes the
  provenance point the page argues in prose visible in a returned value. Read the criterion as
  "produces a result object", the way `tests/test_portal_snippets.py` already asserts.

- **Resolved 3 September 2026: the example's name.** The plan called it "Gaussian/Michelson", a
  placeholder from before the model existed. The model that shipped has no Gaussian component —
  it is the fringe-shape law of an interferometer — so the files are `examples/michelson_phase.py`
  and `docs/examples/michelson-phase.md`, and the roadmap and later packets say "Michelson phase".


- Which HEP dataset S7 uses, if any: the plan sets the fetch priority (HiggsML, then ATLAS Open
  Data, then MadMiner tutorial outputs) but the final pick depends on what this session's spike
  finds usable. If none is usable, S7 falls back to the FlowCyt three-interface benchmark by
  default.
- Notebook format and location: the plan requires a notebook but does not name its path; follow
  the existing `examples/notebooks/` convention used by other examples.

## Design decisions (written 3 September 2026, before any code)

Verified interactively against the frozen API before being written down; every number below was
produced by the calls it describes, on `ExecutionConfig(backend="numpy", precision="float64",
device="cpu")`.

### The statistical model

A Michelson interferometer counts photons along the fringe coordinate. Write the fringe phase
\(u = k x\) and record, for each detected photon, which of \(K\) detector segments it landed in.
Conditioned on the photon count, the arrival law over \(m\) whole fringes is the fringe shape

$$p(u \mid \varphi, \epsilon) \;\propto\; 1 + V\cos\!\big((1+\epsilon)u + \varphi\big),
\qquad u \in [0, 2\pi m),$$

with \(V\) the fringe visibility (known, fixed at 0.6), \(\varphi\) the **phase — the parameter of
interest**, and \(\epsilon\) a **fractional fringe-frequency error — the nuisance**. An unknown
\(\epsilon\) is the canonical nuisance of interferometric metrology: over a short baseline a phase
offset and a slightly wrong wavenumber are nearly the same signal, which is exactly what makes
this a profiled problem rather than a decorative one.

Two parameters, one measurement coordinate. The example therefore demonstrates the point
`docs/motivation.md` makes in prose — that binning one discriminant is the near miss — on a model
where the answer is exactly computable.

### The exact conditional score

Over whole fringes the normalizer \(Z=\int(1+V\cos(u+\varphi))\,du\) equals the interval length at
\(\epsilon_0=0\), so \(\partial_\varphi \log Z = 0\), while \(\partial_\epsilon \log Z =
V\cos\varphi_0\) does not vanish. At \((\varphi_0,\epsilon_0)=(0,0)\) the conditional score is
therefore closed-form:

$$s_\varphi(u) = \frac{-V\sin u}{1+V\cos u},
\qquad s_\epsilon(u) = u\,s_\varphi(u) - V .$$

The \(-V\) is the normalizer derivative, not a centering convenience. It is what makes
\(E[s_\epsilon]=0\) hold exactly: \(E[u\,s_\varphi]=V\) independently of \(m\), so dropping the
term would leave a score with mean \(+V\) and a wrong information matrix. This example is
consequently the cleanest available demonstration of the project's "never center scores" invariant
— the origin is fixed by the model, and getting it right is arithmetic, not preference.

Both components are bounded because \(1+V\cos u \ge 1-V > 0\), so the `ScoreFunction` finiteness
contract holds by construction rather than by clipping.

### Closed forms, which is what makes this a verification asset

$$I_{\varphi\varphi} = 1-\sqrt{1-V^2},\qquad
I_{\varphi\epsilon} = I_{\varphi\varphi}\cdot\frac{u_{\max}}{2},\qquad
E[s_\varphi]=E[s_\epsilon]=0 .$$

At \(V=0.6\) the first is exactly \(0.2\). Both were reproduced by `fisher_information` to
5e-15 on 8,000 midpoint quadrature nodes. The example asserts them, so it is a check on the
library and not only an illustration of it. \(I_{\epsilon\epsilon}\) has no comparably tidy form
and is pinned numerically (41.5392 at the stated settings).

The unbinned correlation is \(+0.872\), and profiling the phase against the frequency costs
**76.0%** of the phase information before any binning: \(0.2 \to 0.047938\). Every retention
figure the example reports for the phase is stated against that profiled ceiling, never against
\(I_{\varphi\varphi}\), because the latter is not available to an analyst who does not know
\(\epsilon\).

### Settings

`V0 = 0.6`, `PHI0 = 0.0`, `FRINGES = 4` (\(u_{\max}=8\pi\)); deterministic midpoint quadrature,
8,000 nodes in full mode and 2,000 under `SCOREQUANT_EXAMPLE_FAST` (`efficient_score_bound`
refuses above `max_rows=20000` distinct atoms, so the full setting stays well inside it);
bin-budget sweep \(K\in\{4,6,8,10\}\) with \(K=6\) the headline; `seed=4` throughout.

### What the example computes, and the numbers it must reproduce

1. **Both routes to the score.** `sq.ScoreFunction(michelson_score, provenance=ScoreProvenance(
   kind="exact", ...), schema=sq.ScoreSchema(("phase", "fringe_frequency")))` paired with
   `sq.IntegrationSource([[0.0, u_max]], density=fringe_density, quadrature=
   sq.GaussLegendreConfig(order=256))`. This is the one input route with no example today: an
   analytic score against a bounded quadrature reference measure. The schema's names let
   `ProfiledDOptimality(interest=("phase",))` declare interest by name; `efficient_score_bound`
   takes indices only, so it gets `interest=(0,)`.
2. **The closed-form assertions** above.
3. **Three partitions per \(K\)**, all through `optimize_partition` on `provider.score(X)` so the
   observation-to-score step stays visible: equal-width detector segments (the naive rule),
   `DOptimality` + `DExchangeConfig`, and `ProfiledDOptimality(interest=(0,))` +
   `DExchangeConfig` seeded from `efficient_score_bound(...).labels`.
4. **The headline table**, profiled phase information retained against the unbinned profiled
   ceiling:

   | \(K\) | equal-width segments | D-optimal | profiled-\(D_s\)-optimal | bound gap |
   |---|---|---|---|---|
   | 4 | **0.0000** | 0.7227 | 0.8629 | 5.0e-03 |
   | 6 | 0.2054 | 0.7995 | 0.9483 | 2.5e-05 |
   | 8 | 0.7247 | 0.8806 | 0.9714 | 6.5e-05 |
   | 10 | 0.5653 | 0.9267 | 0.9817 | 1.2e-04 |

   Three things in that table are the example's reason to exist, and each has an exact
   explanation the page must give rather than merely display.

   - **Equal-width segments retain exactly nothing at \(K=4\).** Four equal segments over four
     fringes make each segment one whole period, so by periodicity every cell mean is identical,
     the between-cell matrix is rank-deficient, and the profiled phase information is zero. This
     is aliasing between the segmentation and the fringe period, and it is a real hazard, not a
     contrived one.
   - **Adding segments can make the naive rule worse** (0.7247 at \(K=8\) down to 0.5653 at
     \(K=10\)): eight segments over four fringes is a clean two per fringe, ten is 2.5 per fringe
     and aliases again. Refining a partition can only help — but only when it *refines*, and an
     equal-width rule at a new \(K\) is not a refinement of the old one.
   - **D-optimality is not the phase criterion.** At \(K=4\) the D-optimal partition keeps 0.7227
     of the profiled phase information where the profiled-optimal keeps 0.8629, and the two
     criteria return different labels at every \(K\). The gap to the certified efficient-score
     ceiling stays at or below 5e-03, so the profiled solver is provably close to the best any
     \(K\)-cell rule can do.
5. **The compile bridge and the refusal.** The D-optimal partition is exchange-stable, so
   `compile_quantizer()` succeeds and the compiled rule remembers
   `ExecutionConfig(backend="numpy", ...)` — the concrete form of ADR 0018's fit-here-predict-there
   claim. The profiled partition refuses: `RefusalError: finite profiled-D labels have no canonical
   inductive compilation; fit an explicit quantizer instead [CE-DS-GLOBAL-GEOMETRY-001]`. Both are
   asserted.
6. **The reusable rule on the missing route.** `fit_quantizer(source, provider=provider, ...)`
   twice: `DOptimality` + `DExchangeConfig`, and `ProfiledDOptimality(interest=("phase",))` +
   `SoftVoronoiConfig`, the latter being the only route to a reusable profiled rule.

   Each rule reports two numbers, and the distinction is the point. `criterion_efficiency` is what
   a rule scores on the criterion it optimized — `train_report` for the plain rule,
   `train_profiled_report` for the profiled one — and the two are on different denominators, so
   they must never be compared. `profiled_retention` puts both rules' own labels through the
   sweep's profiled ceiling, and is the column that compares. At `K=6`, 8,000 nodes and
   `max_steps=300`: the plain rule scores 0.8345 on its own criterion but retains **0.7987** of the
   profiled phase information; the profiled rule scores 0.8532 and retains **0.8518**. Reading only
   the own-criterion column would have made the gap look like 0.019 when it is 0.053.

   The soft fit's own-criterion number rises with the step budget (0.8353 at 80 steps, 0.8412 at
   120, 0.8532 at 300, 0.8805 at 600) while its plain D retention falls over the same range (0.8081
   to 0.6465). That is the profiled criterion working, not drifting: it buys phase information by
   spending information in the nuisance direction. The hardening gap stays near 1e-4 throughout, so
   it reports that the surrogate committed — not that the answer is good. `initializer_restarts`
   changed nothing at any budget tried (3 and 8 were bit-identical), which is worth a look in a
   later session but is not this example's subject.
7. **The comb.** Predicting the compiled six-bin rule on a 4,001-node grid of \(u\) yields 24
   contiguous runs, not 6 — one tooth per bin per fringe. A linear grid counts 25 because
   \(u=0\) and \(u=u_{\max}\) are the same fringe phase and the wrap-around tooth is split in
   two; `comb_runs` rejoins them, which is why the assertion reads `n_bins * 4`. Because the score depends on \(u\) only through the fringe phase, a
   score-space cell pulls back to one interval per fringe: the information-optimal detector
   segmentation is a comb, and no contiguous segmentation of the aperture can imitate it. This is
   the figure's whole point and the example's most transferable lesson.

### Figure

Two panels, generated through `examples/run.py`'s `run_and_save` conventions. Left: the score
trajectory in \((s_\varphi, s_\epsilon)\) — a single curve, since \(u\) is one-dimensional —
coloured by fitted bin, with the compiled Mahalanobis-Voronoi boundaries. Right: the same labels
drawn back onto \(u\) over the four fringes, above the equal-width segmentation for contrast, so
the comb and the aliasing are visible in one look.

### Deliberately not in this example

No downstream likelihood fit. `examples/nuisance_profiled_ds.py` already carries that arc, and the
value here is the exactness of the model, not a second Poisson fit. No `ScalarDPConfig` run: the
score space is rank 2, so the interval dynamic program does not apply, and saying so is more useful
than demonstrating a refusal a reader did not ask about.

## HEP data spike record (3 September 2026)

Verified by fetching, not by reading landing pages. A delegated pass returned "none of the three
is usable"; two of its negative claims were checked directly and the decisive one was wrong, so
the verdict below supersedes it. The correction is recorded because it changes S7's path from the
fallback back to the HEP route the plan preferred.

### 1. FAIR Universe — HiggsML Uncertainty Challenge — **USABLE**

The delegated pass reported "data not publicly accessible without authentication" and "no public
Zenodo mirror or alternative archive exists", inferred from a login redirect on the Codabench
competition listing. Both are false. A public release exists:

- **DOI** `10.5281/zenodo.15131565`, "FAIR Universe - HiggsML Uncertainty Challenge Public
  Dataset". **Licence CC-BY-4.0**, which permits redistributing a derived subset inside this
  MIT-licensed repository with attribution and a DOI citation.
- **Reachable without credentials.** A ranged request on the file endpoint returns HTTP 206 with
  real bytes (`PK\x03\x04`), and the archive's members are
  `FAIR_Universe_HiggsML_data.parquet` and `FAIR_Universe_HiggsML_data_metadata.json` —
  **Parquet, not ROOT**. No `uproot`, and no new runtime dependency at all, because the fixture is
  committed as `.npz` the way `examples/data/flowcyt_fixture.npz` already is; Parquet is read once,
  offline, at fixture-build time (`uv run --with pyarrow` suffices and touches neither the project
  environment nor `uv.lock`).
- **A committed sample already exists at fixture scale.**
  `FAIR-Universe/HEP-Challenge` holds `input_data/FAIR_Universe_HiggsML_data.parquet` at
  **0.13 MB** (1,000 rows x 31 columns), so the 15.1 GB full archive need not be downloaded to
  build a 5 MB fixture. Columns: `weights`, `labels`, `detailed_labels`, sixteen `PRI_*` primary
  observables and thirteen `DER_*` derived ones. Composition by weight: `ztautau` 634 rows,
  `htautau` (signal) 336, `ttbar` 26, `diboson` 4; summed weights 1.05e6 for 10 fb^-1.
- **Nuisance parameters are explicit and parametric**, which is what makes this dataset the right
  one rather than merely an available one. `ingestion_program/systematics.py` implements
  `systematics(data, tes=1.0, jes=1.0, soft_met=0.0, ttbar_scale=..., diboson_scale=...,
  bkg_scale=...)`: tau energy scale, jet energy scale, soft MET, and three background
  normalizations. `tes` — the nuisance the S7 packet named — is a factor applied to `PRI_had_pt`,
  so the nuisance is a transformation of the features that the model can be differentiated with
  respect to, rather than a set of pre-baked variation samples. That is exactly the shape a
  profiled \(D_s\) example needs.

**One real limit on the sample.** With 26 `ttbar` and 4 `diboson` rows, the two
background-normalization nuisances are not usable at sample scale. `tes` is, because it acts on
every event. So S7 can take either path:

- **(a) recommended:** the 0.13 MB sample plus the `tes` nuisance. No large download, and it is the
  nuisance the packet asked for.
- **(b)** a larger fixture cut from the Zenodo release, if the background-normalization nuisances
  are wanted too. Costs a 15.1 GB download once.

Provenance note for S7: `FAIR-Universe/HEP-Challenge` carries **no licence file**, so derive the
fixture's licence claim from the Zenodo record (CC-BY-4.0), cite the DOI, and record the hash — do
not cite the GitHub path as the licence source.

### 2. ATLAS Open Data — **usable, but worse for this purpose**

Reachable (CERN Open Data API HTTP 200; record 15006, DOI
`10.7483/OPENDATA.ATLAS.B5BJ.3SGS`) and **CC0-1.0**, so redistribution is unrestricted. Against
it: ROOT format, which would need `uproot` at fixture-build time; ~2.5 GB with per-file sizes of
77-687 MB; and the education-tier Gamma-Gamma sample has **no documented systematic
uncertainties**, which is the decisive criterion. Not chosen. The delegated pass's further claim
that ROOT files are unreachable over HTTP was not confirmed and is not load-bearing here.

### 3. MadMiner tutorial outputs — **not usable**

Not a data release. The tutorials are instructions for *generating* events with MadGraph, Pythia
and Delphes; no static dataset is archived, and the toolchain would add Fortran and C++ build
requirements. Confirmed: the repository serves notebooks, no data.

### Verdict

**S7 builds the HEP route on the FAIR Universe HiggsML public dataset, path (a).** The FlowCyt
three-interface fallback is not needed and should not be built. Recorded facts S7 relies on: DOI
`10.5281/zenodo.15131565`, CC-BY-4.0, Parquet, 0.13 MB sample at 1,000 rows x 31 columns, and the
`tes` tau-energy-scale nuisance from `ingestion_program/systematics.py`.

## Closing report

Session S4 ran on 3 September 2026 on branch `consolidation-s4-showcase-foundations` (one Claude
Code session; the statistical design and the HEP verdict done inline by the orchestrator, two
sonnet implementation agents and one haiku fetch agent). The session also carried a programme
re-scope the owner asked for, described at the end of this report.

**Delivered.** `examples/michelson_phase.py` measures an interferometer phase against a
fringe-frequency nuisance, entirely on `ExecutionConfig(backend="numpy", precision="float64",
device="cpu")`. It closes the one input route that had no example: an analytic `ScoreFunction`
against a bounded `IntegrationSource`, with `ScoreSchema(("phase", "fringe_frequency"))` so
`ProfiledDOptimality(interest=("phase",))` declares interest by name. Alongside it:
`examples/notebooks/michelson_phase.ipynb`, `docs/examples/michelson-phase.md` (in the nav, with
every fence executed), the two-panel figure and its evidence JSON under `docs/examples/assets/`,
four pinned tests in `tests/test_evidence_suite.py`, and updated counts on
`docs/examples/index.md` and `docs/index.md` (ten pages became eleven). The
`CentralLogRatioScore` fence in `docs/three-doors.md` now fits a quantizer and reports
`information_kind == "supplied_score_surrogate"`.

The design spec above was written and verified before any code, and the example reproduces it. The
numbers that matter: equal-width detector segments retain **exactly zero** profiled phase
information at `K=4`, because four segments over four fringes make every cell mean identical and
the between-cell matrix rank-deficient — aliasing between the segmentation and the fringe period.
The same rule gets *worse* from `K=8` to `K=10` (0.7247 to 0.5653) for the same reason. D-optimality
is not the phase criterion: 0.7227 against the profiled-optimal 0.8629 at `K=4`, with different
labels at every budget and a gap to the certified efficient-score ceiling of at most 5e-03. Two
closed forms, \(I_{\varphi\varphi}=1-\sqrt{1-V^2}\) and \(I_{\varphi\epsilon}=I_{\varphi\varphi}
u_{\max}/2\), are asserted to 1e-12, so the page checks the library rather than only illustrating
it. The compiled six-bin rule predicts a **comb** — 24 teeth, one per bin per fringe — which no
contiguous segmentation of the aperture can express.

**Verified.** Full handoff gate green on the branch: `ruff check`, `ruff format --check`,
`ty check src`, the whole suite under X64 (**500 passed**), the float32 leg (4 passed), `uv build`
(wheel and sdist), and `mkdocs build --strict`.

**Corrected during the session, and worth knowing.**

- *The HEP verdict was wrong the first time.* The delegated spike reported all three datasets
  unusable, concluding from a login redirect on a competition listing page that no public archive
  existed. One direct query found the FAIR Universe HiggsML public dataset on Zenodo under
  CC-BY-4.0, in Parquet, with a 0.13 MB sample already committed upstream and six explicit
  parametric nuisances including the `tes` tau energy scale S7 had named. Every link was then
  checked directly (HTTP 206 with real bytes, HTTP 200 on the sample, the file loads to
  1,000 x 31). The full record is in the "HEP data spike record" section above; S7 builds the HEP
  route and its FlowCyt fallback is cut. `docs/programme/README.md` gained a standing rule from
  this: when a delegated negative would change what the programme builds, the orchestrator
  re-checks the decisive claim itself.
- *The reusable-rule table compared two different quantities.* As first implemented, `RuleRow`
  filled one `efficiency` field from `train_report` for the plain rule and from
  `train_profiled_report` for the profiled one — different denominators in one column, in a JSON
  file S8 is required to read its numbers from. The row now carries both `profiled_retention` (both
  rules' own labels through the sweep's ceiling, so the column compares) and
  `criterion_efficiency` (each rule on its own criterion, documented as not comparable). The
  correction matters: read the own-criterion column alone and the gap looks like 0.8345 against
  0.8532; the real gap is 0.7987 against 0.8518.
- *The spec's own soft-Voronoi numbers were from a different configuration* and a different report,
  which the implementing agent flagged honestly rather than fabricating a match. The spec above now
  records the measured behaviour instead: the profiled criterion's own score rises with the step
  budget while plain D retention falls, which is the criterion working, and the hardening gap stays
  near 1e-4 throughout — so a small gap says the surrogate committed, not that the answer is good.
- *The comb count is 24, not the 25 the spec first stated.* A linear grid splits the wrap-around
  tooth in two because \(u=0\) and \(u=u_{\max}\) are the same fringe phase; `comb_runs` rejoins
  them.

**Cut or left open.** Nothing in the packet was cut. Two things are left for later and neither
blocks a session: `initializer_restarts` made no difference to `SoftVoronoiConfig` at any budget
tried (3 and 8 were bit-identical), which deserves a look but is not this example's subject; and
`docs/examples/michelson-phase.md` links `motivation.md`, which S6 retires — S6 fixes the inbound
link when it does.

**Programme re-scope (owner-directed, same session).** The owner asked that the remainder of M12
be reweighted towards a presentable user-facing state, with the portal explaining rather than
selling. Four decisions were taken and are recorded in the packets and the M12 block: the portal is
promoted to the site root with MkDocs narrowed to `/reference/` behind a committed redirect
manifest; walkthroughs live in the portal as MDX and MkDocs becomes reference-only; four
walkthroughs, one per input route, two on real data; and the front door is written last so it
quotes real numbers. S6 and S8 were re-scoped, S10 is new, S9 re-pointed, S4 and S7 unchanged. The
execution order is **S4 -> (S6 || S7) -> S8 -> S10 -> S9**. Two stale facts were corrected on the
way: v0.1.0 shipped to PyPI on 30 August 2026, while `CHANGELOG.md` said `unreleased` and the
roadmap said nothing was published.

**The one thing the next session must know.** S6 and S7 are both unblocked and independent, and
they are the two that can run in parallel. S6 is the structural session and everything after it
depends on the route and topology it lands, so it goes first if only one runs; its riskiest
deliverable is the redirect manifest, and the pre-cut sitemap listed 52 URLs of which 51 need
stubs — the site root is deliberately not one of them, because after the promotion the root is the
portal home, which is the entire point.
