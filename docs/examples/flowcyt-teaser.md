# FlowCyt: real cells, not a synthetic problem

Every other page in this section solves **space quantization** or **sample partitioning**
on a synthetic model, so the true answer is available for comparison. This page is a
pointer to the one case study that runs the same library on real, messy, real-instrument
data with no synthetic ground truth: the
[complete FlowCyt cell-population study](../usecases/flowcyt/index.md). There is no
notebook here — the study page is already the full story, with its own committed figures,
committed JSON evidence, and its own regression tests.

## What the study is

Flow cytometry measures twelve markers per cell and produces a cloud of hundreds of
thousands of cells per patient. The practical deliverable is usually a handful of
population fractions — here, the proportions of T cells, B cells, monocytes, mast cells,
hematopoietic stem/progenitor cells, and everything else. The study asks whether that
handful of numbers can be recovered from a few learned hard bins instead of the full
cell cloud, on the public [FlowCyt benchmark](https://proceedings.mlr.press/v248/bini24a.html):
30 bone-marrow patients, split by patient into 20 reference and 10 frozen held-out test
patients, with a reproducible 600,000-cell fixture sampled from the complete 21-million-row
corpus.

**Task and door.** The study fits a reusable rule — `fit_quantizer` on an explicit
`ScoreSample` — so it is space quantization through the `ScoreSample` boundary. The
scores themselves are not observations: they come from [Door
3](door3-classifier.md), a patient-cross-fitted classifier's posteriors converted to
mixture-fraction score coordinates through `MixturePosteriorTransform`. Classifier
training, calibration, and the downstream mixture likelihood are all application code
outside ScoreQuant's public surface; the library receives score vectors and returns a
frozen quantizer, exactly the boundary [Chapter 4](../book/ch04-scores-and-doors.md)
draws between a score provider and the library.

## Headline result

Eight learned hard bins reach 0.00193 macro RMSE on the ten held-out patients, retaining
98.5% of the supplied-score surrogate information — the useful knee in a bin-count scan
from 5 to 30. Five bins are a genuine negative result rather than an optimizer failure:
a fixed-total six-class mixture has only five independent fractions, so five bins cannot
identify them. The numbers below are read directly from the study's committed evidence,
not retyped from its prose.

```python
import json
from pathlib import Path

metrics = json.loads(Path("docs/usecases/assets/cell_population.json").read_text())
transport = json.loads(Path("docs/usecases/assets/flowcyt_transport_audit.json").read_text())

assert metrics["source"]["sample_rows"] == 600_000
assert transport["full_corpus"]["rows"] == 21_254_866

eight_bins = metrics["soft_voronoi:8"]
assert round(eight_bins["target_macro_rmse"], 5) == 0.00193
assert round(eight_bins["held_out_d_efficiency"], 3) == 0.985

five_bins = metrics["scientific_closure"]["fixed_total_information"]["soft_voronoi:5"]
assert five_bins["d_efficiency"] == 0.0  # non-identifiable fixed-total likelihood

assert round(transport["maximum_absolute_class_fraction_error"], 6) == round(3.4e-05, 6)
assert round(transport["maximum_absolute_standardized_feature_mean_error"], 3) == 0.030
```

The transport audit — comparing the bounded 600,000-cell sample against every one of the
21,254,866 upstream events — found a maximum absolute patient/class fraction error of
\(3.4\times10^{-5}\) and a maximum absolute standardized marker-mean error of 0.030,
which the study reports as evidence the bounded sample is a faithful approximation for
class composition and low-order marker moments, not a proof that every score-space
boundary transports equally well.

## Where it connects

The study exercises the same door and criterion pairing that
[door3-classifier](door3-classifier.md) demonstrates on a synthetic problem — the
retention-versus-classifier-quality caveat there is the same caveat the FlowCyt
classifier is held to. Its finite-D exchange step and compile-bridge check are the same
mechanics [door1-score-events](door1-score-events.md) walks through end to end, and its
soft Voronoi fit is the same solver [soft-purification](soft-purification.md) studies in
isolation. [Chapter 13](../book/ch13-estimated-scores.md) is the theory behind the
estimated-score caveat this study takes seriously throughout, and [Chapter
14](../book/ch14-choosing-a-method.md) is the diagnostic checklist — rank, occupancy,
train/validation gap, score provenance — the study runs in full on real data.

Read the complete study for the [classifier calibration
audit](../usecases/flowcyt/scores.md), the [five-bin non-identifiability
proof](../usecases/flowcyt/quantization.md#why-five-bins-fail), the
uncertainty-coverage check at the simplex boundary, and the [full-corpus transport
audit](../usecases/flowcyt/data.md#the-full-corpus-transport-audit). The
[profiled-\(D_s\) extension](../usecases/flowcyt/profiled.md) then asks what changes when
the measurement is a single population fraction with the rest of the composition
floating — and answers, with a certificate, that on this dataset the answer is
"almost nothing". The [solver comparison](../usecases/flowcyt/solvers.md) runs every
applicable solver and the three canonical baselines on the same rows this study uses, and
shows where the synthetic shootout's near-ties do and do not survive real data.
