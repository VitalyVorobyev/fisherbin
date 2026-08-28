# ScoreQuant contributor guidance

## Project contract

ScoreQuant compresses continuous or high-dimensional events into hard bins while preserving Fisher information. Keep task and representation semantics explicit:

```text
Source + (densities | density ratios | scores) -> ScoreProvider -> score law -> partition or quantizer
```

- `optimize_partition(scores, ...)` owns fixed-sample assignment and returns no predictor.
- `fit_quantizer(source, score=...)` owns reusable score-space rules.
- `scores_from_components(Phi, coefficients)` and the ratio algebra in `ratios.py` are explicit
  adapters, not fitting tasks.
- Prediction is always `predict_scores`; observation-to-score conversion remains visible.
- Model density ratios enter through providers; importance ratios are source weights. The two
  never share an argument, and estimated ratios never claim exact Fisher semantics.

Use JAX for numerical kernels and Optax for gradient optimization. Do not add PyTorch, a parallel NumPy implementation, global JAX configuration at import time, or a backend abstraction without an approved roadmap change and a concrete second backend.

## Numerical invariants

- Scores and weights are finite; weights are nonnegative and at least one is positive.
- Zero-weight rows remain predictable but contribute no information or optimization measure.
- Never center scores: the score-space origin has statistical meaning.
- Project numerically singular Fisher directions out; do not add information with a ridge.
- Validation samples are diagnostic only and never influence gradients, stopping, or checkpoint selection.
- Use deterministic seeds and judge optimizers by the final hardened partition, not only a soft objective.
- Preserve parameter-reparameterization, bin-relabeling, event-ordering, uniform-weight-scaling, and split-weight-duplication invariants.

## Code placement and API discipline

- Keep Fisher statistics in `information.py`, transforms in `transforms.py`, private optimizers in `quantizers.py`, linear-model adapters in `components.py`, density-ratio algebra in `ratios.py`, and public orchestration/results/configuration in their existing modules.
- Keep dataset generators, comparisons, tuning, custom figure layouts, and exploratory logic in `examples/`, tests, or benchmarks.
- Add public concepts only when they are reusable, stable, documented, and non-duplicative. Prefer private helpers over provisional public APIs.
- Avoid aliases and overlapping entry points. Document intentional compatibility breaks and update the API guide, examples, and an ADR when the decision is durable.
- Keep optional visualization dependencies lazy and outside numerical hot paths.
- Avoid `O(N^2)` work. Optimization histories store aggregate metrics and center snapshots, never per-observation responsibilities.

## Research workflow

- `agenticresearch/` is the mathematical scientific memory (claim registry, counterexample bank, open-problem queue). It governs itself through its own `agenticresearch/AGENT.md` and is excluded from the Ruff gate.
- The library crosses into it at exactly two points: `tests/test_research_claims.py` reads counterexample fixtures from `agenticresearch/COUNTEREXAMPLES/`, and `tests/test_research_registry.py` enforces registry integrity. Research results become library behavior only by being copied into deterministic regression tests or theorem-cited code paths.
- Code in `src/` that relies on a theorem names it; code that refuses a capability names the counterexample forcing the refusal. Keep both in sync with the registry.

## Tooling: use uv

`uv` is the only supported environment, dependency, build, and command runner. Do not introduce pip, Conda, Poetry, or manually edit `uv.lock`.

```bash
uv sync --all-extras --all-groups --locked
uv run ruff check .
uv run ruff format --check .
uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
```

Use `uv add`, `uv remove`, and `uv lock` for dependency changes. Run commands through `uv run` so local and CI environments stay aligned.

## Engineering and documentation practices

- Make small, cohesive changes and reuse existing abstractions before adding new ones.
- Preserve unrelated work. Avoid destructive Git commands and hidden behavior changes.
- Use type annotations, meaningful names, and NumPy-style docstrings for every public object. Comments should explain why, especially for numerical choices, rather than narrate code.
- Use explicit array-like and recursive JSON contracts at conversion boundaries. `typing.Any` is prohibited in `src/`; Ruff `ANN401`, a banned-import rule, and `ty` enforce this.
- Add deterministic tests for changed behavior and numerical edge cases. Use fixed seeds and measurable assertions; avoid brittle pixel snapshots.
- Validate in proportion to risk: targeted tests while iterating, then the full commands above before handoff.
- Update user guides when workflows change. Run MkDocs in strict mode so broken navigation, links, or reference collection fail CI.
- Keep architecture decisions in `docs/adr/` and executable phase gates in `docs/roadmap.md`; do not create parallel planning files.
- Do not commit caches, local environments, build output, or `site/`. Commit gallery images only when intentionally regenerated and visually inspected.
- Do not push, merge, tag, publish, or deploy unless the user authorizes that action.

Persistence, services, frontends, multiple numerical backends, signed weights, and advanced statistical objectives remain deferred to the roadmap.

## Completion checklist

Before finishing, run the relevant tests plus Ruff, the strict documentation build, and the package build. Report the exact validation performed and explain any check that could not be run.
