# FisherBin: from events to informative counts

FisherBin learns a finite hard partition of continuous or high-dimensional events while preserving information about parameters of a linear intensity model.

[Start learning](learn/estimation-problem.md){ .md-button .md-button--primary }
[Run the first tutorial](tutorials/first-partition.md){ .md-button }

<div class="grid cards" markdown>

-   **Explicit statistical workflow**

    Keep physical variables, component values, scores, and hard bins visible as separate representations.

-   **A small statistical boundary**

    Bring scores from an analytic model, linear components, automatic differentiation, a simulator, or a classifier.

-   **Evidence, not optimizer claims**

    Inspect held-out Fisher retention, occupancies, center motion, and final hardened partitions.

</div>

## What problem does it solve?

Suppose every observation is a point in a large space, but the final analysis
estimates only a few parameters. You may still need a small number of hard bins
for a count likelihood, a template fit, storage, or an interpretable selection.
Ordinary geometric binning preserves proximity in the measured variables.
FisherBin instead preserves similarity in how observations respond to the
parameters.

That response is represented by the **score**, the gradient of the log
likelihood. The Learn section introduces likelihood, score, Fisher information,
and the exact information loss from binning from first principles. No prior
knowledge of score compression is assumed.

## The library boundary

```text
physical variables X
    -- component model --> component values Phi
    -- reference theta0 --> scores Phi / (Phi @ theta0)
    -- FisherBin --> hard bin labels
```

Start directly from evaluated components when that is what your simulation or template pipeline already produces:

```python
import fisherbin as fb

result = fb.fit_components(
    Phi,
    coefficients=theta0,
    weights=mc_weights,
    n_bins=16,
    config=fb.SoftVoronoiConfig(seed=7),
)

print(result.report())
data_bins = result.predict(Phi_data)
```

Components need not be normalized probability densities. FisherBin requires a finite, strictly positive reference intensity and finite nonnegative integration weights.

FisherBin produces a frozen partition and information diagnostics. It does not
fit the downstream scientific parameters and it does not train a classifier.

## Evidence and applications

The committed [synthetic evidence gallery](gallery/index.md) exercises analytic identities, nonlinear score mappings, importance weights, independent validation and test samples, and competing baselines.

[![Spatial-source optimization and diagnostics](gallery/spatial_sources.png)](gallery/index.md)

## A realistic application

The [FlowCyt cell-population use case](usecases/cellpopulation.md) learns a few
hard multidimensional gates from labelled reference patients, keeps the labels
of ten test patients out of inference, and estimates six population fractions
from bin counts.
The study also explains why an unbinned likelihood built from approximate
classifier ratios can have worse RMSE than a binned, independently calibrated
pipeline. This is model bias, not an exception to the information inequality.

[![FlowCyt population quantification](usecases/assets/cell_population.png)](usecases/cellpopulation.md)

Continue with [the estimation problem](learn/estimation-problem.md), or jump to
the [workflow guide](user-workflow.md) if you already have score vectors.
