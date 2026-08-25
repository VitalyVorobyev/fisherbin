# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

ScoreQuant is a Python library (JAX + Optax) for information-preserving hard binning: compressing events into a few hard labels while preserving Fisher information for parameter estimation.

The root `AGENTS.md` is the durable engineering contract — read it before making changes. It records numerical invariants, module boundaries, and deferred scope. The highlights below summarize it; `AGENTS.md` wins on any conflict.

## Commands

`uv` is the only supported environment/build/command runner. Never use pip, Conda, or Poetry; never hand-edit `uv.lock` (use `uv add` / `uv remove` / `uv lock`).

```bash
uv sync --all-extras --all-groups --locked   # set up environment
uv run ruff check .
uv run ruff format --check .
uv run ty check src                          # type checking (src only)
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest                          # full test suite
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py    # float32 path
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_fit.py -k name  # single test
uv build
uv run mkdocs build --strict                 # docs must build strictly (broken links fail)
```

Before handoff, run the full set above. X64 is an explicit CI/application choice — the package must never set global JAX config at import time.

## Architecture

Two deliberately distinct public tasks (in `api.py`):

```text
scores ---------------------------------> optimize_partition() -> PartitionResult
ScoreSample ----------------------------+
ObservationSample + ScoreProvider ------+-> fit_quantizer() ----> QuantizerResult
IntegrationSource + ScoreProvider ------+
```

- `optimize_partition(scores, ...)` owns a fixed-sample assignment; `PartitionResult` deliberately has **no** predict method. The one exception: an exchange-stable, nonsingular D-optimal result can `compile_quantizer()` into a theorem-backed Mahalanobis rule.
- `fit_quantizer(source, score=...)` owns reusable score-space rules; prediction is always the explicit `predict_scores` — observation-to-score conversion is never hidden inside prediction.
- Sources (the reference measure) and score providers (observation-to-score map) are separate contracts and are validated together: a `ScoreSample` rejects a provider; observation/integration sources require one.

Module ownership (keep code in its owning module):

- `information.py` — Fisher and retained-information algebra
- `transforms.py` — informative subspace and whitening
- `partition.py` — exact D finite relocation
- `quantizers.py` — private weighted k-means and soft-D numerical kernels
- `sources.py` — empirical/quadrature measures plus `ScoreProvenance`
- `providers.py` — framework-neutral observation-to-score adapters (`ClassifierScore`, etc.)
- `components.py` — linear models and posterior-to-score algebra
- `criteria.py`, `config.py`, `result.py`, `api.py` — public contracts and orchestration
- `examples/`, `tests/`, `benchmarks/`, `research/` — datasets, tuning, exploration (research is excluded from the Ruff gate; anything relied upon gets copied into a deterministic regression test)

Criterion/configuration pairs are a closed set (e.g. `DOptimality` + `DExchangeConfig`/`SoftVoronoiConfig`, `NormalizedTrace` + `KMeansConfig`); unsupported pairs fail before optimization. No generic criterion plugin system.

## Key invariants

- Never center scores — the score-space origin has statistical meaning.
- Project numerically singular Fisher directions out; never repair with a ridge.
- Validation samples are diagnostic only: they must not influence gradients, stopping, or checkpoint selection.
- Weights are nonnegative and finite with at least one positive; zero-weight rows remain predictable but contribute nothing.
- Judge optimizers by the final hardened partition, with deterministic seeds.
- Avoid `O(N^2)` work; histories store aggregate metrics and center snapshots, never per-observation responsibilities.
- JAX only for numerical kernels, Optax for gradients. No PyTorch, no parallel NumPy implementation, no backend abstraction.

## Conventions

- `typing.Any` is banned in `src/` (Ruff `ANN401` + banned-import rule + `ty`); use explicit boundary types — public conversion boundaries take `numpy.typing.ArrayLike`.
- NumPy-style docstrings on every public object; mkdocstrings collects them into the reference.
- Public API changes must update docstrings, the handwritten `docs/api.md`, examples, and an ADR in `docs/adr/` when the decision is durable. Executable phase gates live in `docs/roadmap.md` — don't create parallel planning files.
- Optional visualization deps (matplotlib) stay lazy imports outside numerical hot paths.
- Don't commit caches, `site/`, build output, or local environments. Gallery images only when intentionally regenerated and inspected.
