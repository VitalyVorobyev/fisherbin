"""The single source of truth for the ``/get-started`` portal page.

This is a genuine, standalone Python program: run it top to bottom with
``uv run python website/scripts/get_started_program.py`` and it prints, in
order, every number the ``/get-started`` page shows. Nothing on that page is
retyped from a notebook or hand-copied from a terminal -- the page's prose
quotes this file's own stdout.

``website/scripts/generate_snippets.py`` is the other reader of this file. It
splits the source on the ``# %% cell: <id>`` markers below, executes each cell
in one shared namespace (so later cells see earlier cells' variables, exactly
as running this file straight through would), and captures each cell's stdout
into ``website/src/generated/snippet-outputs.json``. The portal's ``Snippet``
component then renders one cell's code alongside its captured output.

Every cell that prints a number does so through an explicit format spec
(``f"{x:.4f}"``, never a bare ``repr`` of a float or array) and runs on the
NumPy backend at float64, so the output is bit-reproducible across runs and
across machines.
"""

# %% cell: setup
import tempfile
from pathlib import Path

import numpy as np

import scorequant as sq

rng = np.random.default_rng(21)
execution = sq.ExecutionConfig(backend="numpy", precision="float64", device="cpu")

# N(mu, I_2) at mu0 = 0 has score s(x) = x: these raw observations already
# are the score vectors every later cell works with.
scores = rng.normal(size=(1_200, 2))
weights = np.ones(scores.shape[0])

# %% cell: first-fit
partition = sq.optimize_partition(
    scores,
    weights=weights,
    n_bins=5,
    criterion=sq.DOptimality(),
    config=sq.DExchangeConfig(seed=21),
    execution=execution,
)

print(f"D-efficiency         {partition.train_report.geometric_mean_retention:.4f}")
print(f"effective rank       {partition.train_report.effective_rank}")
print(f"exchange stable      {bool(partition.exchange_stable)}")
print(f"best remaining gain  {partition.best_remaining_gain:.3e}")

# %% cell: reading-the-numbers
report = partition.train_report
eigenvalues = ", ".join(f"{value:.4f}" for value in report.retained_eigenvalues)
bin_weights = ", ".join(f"{value:.1f}" for value in report.bin_weights)
effective_sizes = ", ".join(f"{value:.1f}" for value in report.bin_effective_sample_sizes)

print(f"retained eigenvalues   [{eigenvalues}]")
print(f"bin weights            [{bin_weights}]")
print(f"bin effective sizes    [{effective_sizes}]")

# %% cell: stability-check
stability = sq.exchange_stability_report(scores, partition.labels, weights=weights)

print(f"stable          {stability.stable}")
print(f"best gain       {stability.best_gain:.3e}")
print(f"gain tolerance  {stability.gain_tolerance:.1e}")

# %% cell: reusable-rule
holdout = rng.normal(size=(400, 2))

quantizer = sq.fit_quantizer(
    sq.ScoreSample(scores, weights),
    validation=sq.ScoreSample(holdout),
    n_bins=5,
    criterion=sq.DOptimality(),
    config=sq.SoftVoronoiConfig(seed=21, initializer_restarts=4, max_steps=120, record_every=20),
    execution=execution,
)

train = quantizer.train_report.geometric_mean_retention
validation = quantizer.validation_report.geometric_mean_retention
print(f"train retention       {train:.4f}")
print(f"validation retention  {validation:.4f}")
print(f"hardening gap         {quantizer.hardening_gap:.3e}")

# %% cell: predict-and-save
fresh = rng.normal(loc=0.2, size=(300, 2))
predicted = quantizer.predict_scores(fresh)
counts = ", ".join(f"{n}" for n in np.bincount(predicted, minlength=5))
print(f"bin counts  [{counts}]")

with tempfile.TemporaryDirectory() as directory:
    saved_path = quantizer.quantizer.save(Path(directory) / "quantizer")
    reloaded = sq.Quantizer.load(saved_path)
    reloaded_predicted = reloaded.predict_scores(fresh)

agrees = bool(np.array_equal(predicted, reloaded_predicted))
print(f"reload agrees on every row  {agrees}")

# %% cell: baseline
baseline = sq.fit_quantizer(
    sq.ScoreSample(scores, weights),
    n_bins=5,
    criterion=sq.NormalizedTrace(),
    config=sq.KMeansConfig(seed=21, solver_restarts=4),
    execution=execution,
)

baseline_retention = baseline.train_report.geometric_mean_retention
d_optimal_retention = partition.train_report.geometric_mean_retention
print(f"k-means retention        {baseline_retention:.4f}")
print(f"D-optimal retention      {d_optimal_retention:.4f}")
print(f"difference (D - k-means) {d_optimal_retention - baseline_retention:.4f}")

# %% cell: compile-bridge
if partition.exchange_stable:
    compiled = partition.compile_quantizer()
    new_scores = rng.normal(size=(200, 2))
    compiled_predicted = compiled.predict_scores(new_scores)

    positive = partition.positive_weight_mask
    training_predicted = compiled.predict_scores(partition.training_scores)
    reproduces_training = bool(
        np.array_equal(training_predicted[positive], partition.labels[positive])
    )
    compiled_counts = ", ".join(
        f"{count}" for count in np.bincount(compiled_predicted, minlength=5)
    )

    print(f"reproduces every positive-weight training label  {reproduces_training}")
    print(f"new-score bin counts  [{compiled_counts}]")

# %% cell: refusal
refusal_partition = sq.optimize_partition(
    scores,
    weights=weights,
    n_bins=5,
    criterion=sq.ProfiledDOptimality(interest=(0,)),
    config=sq.DExchangeConfig(seed=21),
    execution=execution,
)

try:
    refusal_partition.compile_quantizer()
except sq.RefusalError as exc:
    print(str(exc))

# %% cell: profiled
bound = sq.efficient_score_bound(scores, interest=(0,), weights=weights, n_bins=5)

profiled = sq.optimize_partition(
    scores,
    weights=weights,
    n_bins=5,
    criterion=sq.ProfiledDOptimality(interest=(0,)),
    config=sq.DExchangeConfig(seed=21),
    initial_labels=bound.labels,
    execution=execution,
)

print(f"efficient-score upper bound  {bound.upper_bound:.4f}")
print(f"gap to profiled partition    {float(bound.gap_to(profiled)):.3e}")

# %% cell: scalar
scalar_quantizer = sq.fit_quantizer(
    sq.ScoreSample(np.asarray(scores[:, :1])),
    n_bins=5,
    criterion=sq.DOptimality(),
    config=sq.ScalarDPConfig(),
    execution=execution,
)

scalar_retention = scalar_quantizer.train_report.geometric_mean_retention
print(f"scalar D-optimal retention (the global optimum)  {scalar_retention:.4f}")

# %% cell: certify
small = rng.normal(size=(24, 2))
incumbent = sq.optimize_partition(
    small,
    n_bins=3,
    config=sq.DExchangeConfig(seed=1),
    execution=execution,
)
certificate = sq.certify_partition(small, n_bins=3, incumbent=incumbent.labels)

print(f"status                  {certificate.status}")
print(f"gap                     {certificate.gap:.3e}")
print(f"incumbent was optimal   {bool(certificate.incumbent_was_optimal)}")
