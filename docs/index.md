# ScoreQuant: from events to informative hard labels

ScoreQuant optimizes hard labels in statistical score space. It exposes two explicit tasks:

```text
fixed score rows -> optimized finite assignment
score law        -> reusable score-space quantizer
```

The distinction matters. Labels for one table do not usually determine labels for future events.

## Choose the task first

<!-- TODO(phase2): illustrative fragment (scores/weights defined in prose); slated for docs rewrite. -->
<!-- snippet: skip -->
```python
import scorequant as sq

partition = sq.optimize_partition(
    scores,
    weights=weights,
    n_bins=8,
    criterion=sq.DOptimality(),
    config=sq.DExchangeConfig(seed=3),
)
```

`partition.labels` belongs to the fixed table. It has no `predict` method. A verified stable D
partition can be compiled explicitly.

<!-- TODO(phase2): illustrative fragment (scores defined in prose); slated for docs rewrite. -->
<!-- snippet: skip -->
```python
quantizer = sq.fit_quantizer(
    sq.ScoreSample(scores, weights),
    n_bins=8,
    criterion=sq.NormalizedTrace(),
    config=sq.KMeansConfig(seed=3),
)
new_bins = quantizer.predict_scores(new_scores)
```

If you start from observations, pair their measure with a score provider. The source and provider
remain visible, as does the observation-to-score step at prediction.

## Learn and apply

- The [book](book/index.md) develops the complete theory independently of code.
- The [workflow guide](user-workflow.md) maps each user situation to a concrete call.
- The [API guide](api.md) defines current contracts and errors.
- The [migration guide](migration.md) gives atomic replacements for the removed fitting API.
- The [FlowCyt capstone](usecases/cellpopulation.md) separates classifier error, compression loss,
  identifiability, shift, and downstream inference.
