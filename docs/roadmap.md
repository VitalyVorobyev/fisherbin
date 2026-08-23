# Roadmap

The roadmap intentionally avoids building infrastructure before the method is proven useful.

## M1 — Mathematical reference

Implement in NumPy:

- full and binned Fisher information from `(scores, weights)`;
- information-loss and retained-information diagnostics;
- hard partitions;
- property tests and small synthetic examples.

**Done when:** the equations in `method.md` are reproduced numerically and the core invariants are well tested.

## M2 — Useful MVP

Add:

- weighted score k-means;
- optional Fisher whitening;
- linear-component score adapter;
- simple `fit / predict / report` API;
- comparison with random and observation-space baselines.

**Done when:** the original template-fit problem can be solved through the public API and examples show measurable information retention.

## M3 — Main optimization method

Add optional PyTorch soft-Voronoi optimization:

- k-means initialization;
- soft assignments;
- D-optimal objective;
- temperature annealing;
- final hard partition;
- held-out evaluation.

**Done when:** it reliably matches or improves the k-means baseline on representative synthetic and real examples.

## M4 — Open-source quality

Prepare the first serious public release:

- clean package structure and API;
- documentation and tutorials;
- deterministic tests and CI;
- benchmark suite;
- serialization of fitted partitions;
- examples from at least two non-HEP domains or synthetic analogues.

**Target:** useful, understandable `0.1` library rather than a broad framework.

## Later, only when justified

Possible extensions:

- nuisance-parameter/profiled objectives;
- A/E-optimal or custom objectives;
- power diagrams and occupancy constraints;
- multi-reference optimization;
- analytic/autodiff/learned score adapters;
- large-data or GPU optimization;
- compiled acceleration;
- interactive frontend.

Each should be driven by a real application or benchmark, not anticipated architecture.
