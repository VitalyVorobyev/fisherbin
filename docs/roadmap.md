# Roadmap

## Current status: v0.2 empirical evidence

The v0.1 scientific core is feature-complete:

- JAX Fisher statistics, informative-rank projection, whitening, and nonnegative-weight validation;
- deterministic weighted score k-means and Optax soft Voronoi optimization;
- explicit variable, component, and score workflows with representation-specific prediction;
- immutable configs, reports, traces, held-out diagnostics, and JSON-ready conversion;
- optional Matplotlib views plus three reproducible scripts, notebooks, gallery figures, and baseline comparisons;
- X64 invariant tests, float32 smoke coverage, notebook execution, and a moderate-scale memory benchmark.

The v0.1 hardening milestone also added maintainable internals, Python 3.12
support, MIT licensing, generated API documentation, static typing gates,
package-build checks, and automatic GitHub Pages deployment.

**Status:** complete in the repository. Tagging remains an explicitly authorized
release action rather than a development prerequisite.

## v0.2: broaden empirical evidence

**Outcome:** defaults and acceptance thresholds are supported by more than the three designed proof examples.

- Add a broader deterministic fixture set spanning ranks, occupancies, weight distributions, nonlinear score geometry, and train/test shift.
- Calibrate existing defaults before exposing new optimizer controls.
- Validate at least one realistic external analysis end to end, including how its downstream likelihood consumes frozen labels.
- Compare final hard partitions, runtime, memory, and failure modes; do not make global-optimality claims.

**Exit gate:** documented default choices pass stable held-out thresholds across the expanded suite and one realistic application without dataset-specific library code.

**Application status:** the full FlowCyt evidence freeze is complete. The
broader default-calibration suite in Phase 2 remains open, so v0.2 is not yet
closed.

### Phase 1: realistic application boundary

**Outcome:** prove that an application can estimate its own scores, learn a
FisherBin partition, and consume frozen labels in a downstream likelihood.

- Use FlowCyt population quantification as the standard six-component mixture
  case, with 20 reference patients and ten untouched patients.
- Keep preprocessing, classifier calibration, bin-template estimation, and
  mixture fitting under `examples/cell_population/` while their contracts remain
  tied to this experiment. Promote a capability when it can be expressed and
  tested independently of FlowCyt; preserving the current API is not a gate.
- Commit an attributed real-data fixture for offline CI and a bounded full-data
  command for confirmatory evidence.

**Validation gate:** deterministic fixture tests cover cross-fitting, simplex
scores, binned and unbinned likelihoods, patient separation, hard-partition
evaluation, and strict documentation builds.

**Stop condition:** do not add a labelled-mixture or cytometry convenience API.
Any promoted abstraction must be named in statistical terms, compose with the
existing representation layers, and have domain-independent invariants and
tests.

### Phase 2: defaults and broader fixtures

**Outcome:** support default choices across more than the three designed
synthetic examples and one cytometry fixture.

- Add named cases for deficient rank, rare/empty occupancies, skewed and zero
  weights, nonlinear score geometry, and controlled train/test shift.
- Compare final hard partitions for current k-means and soft Voronoi defaults;
  tune only on training/reference splits and expose no new optimizer controls.
- Record retention, hardened-partition stability, runtime, peak memory, and
  explicit failure modes.

**Validation gate:** deterministic held-out thresholds pass in X64, the float32
smoke path remains finite, and invariant tests continue to pass.

**Stop condition:** a default changes only when the evidence suite shows a
consistent improvement rather than a win on one fixture.

### Phase 3: full FlowCyt evidence freeze

**Outcome:** replace fixture-level integration evidence with a reproducible
full-data result.

- Freeze preprocessing, score estimation, patient split, bin counts, baselines,
  and acceptance rules before evaluating the ten test patients.
- Publish bins-versus-RMSE, predicted-versus-expert fractions, Fisher retention,
  calibration diagnostics, runtime, and memory with machine-readable metrics.
- Report negative results and patient-shift failures without tuning on the test
  patients.

**Validation gate:** learned score partitions beat the random-partition median
in held-out D-efficiency for at least five of six bin counts and are no worse
than marker-space k-means in target-fraction RMSE for at least four of six bin
counts.

**Stop condition:** if the gate fails, keep v0.2 open and revise the upstream
score estimator using reference patients only; do not weaken the test gate.

**Status:** complete on the deterministic 600,000-cell all-patient sample. The
learned partition beat the random D-efficiency median at 6/6 bin counts and
marker-space k-means RMSE at 6/6 bin counts. Eight bins retained 0.944 held-out
D-efficiency at 0.00226 five-target macro RMSE. The published evidence also
records calibration, patient shift, empty held-out bins at larger partitions,
boundary-uncertainty failure, runtime, memory, provenance, and per-patient
predictions.

## Persistence and larger workloads

Design a versioned fitted-partition artifact only after a concrete second process or frontend needs it. Callable `LinearComponents` models cannot be serialized generically, so persistence must define whether consumers provide scores, components, or a separately identified model.

Profile before adding chunked statistics, minibatches, or accelerator-specific paths. Adopt them only when measured workloads exceed the current moderate full-batch target.

## Later statistical and application work

- nuisance-profiled and multi-reference objectives evaluated on concrete applications;
- occupancy constraints, power diagrams, and alternative optimality criteria;
- a backend abstraction after a second backend has explicit requirements;
- a Python service and React/Tauri frontends consuming a stable artifact and configuration contract;
- signed-weight formulations with explicitly revised mathematical guarantees.

These items remain outside v0.1 and are not prerequisites for proving the current method.
