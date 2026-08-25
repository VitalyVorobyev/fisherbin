# Development

ScoreQuant uses [uv](https://docs.astral.sh/uv/) for environments, dependencies, command execution, locking, and package builds. Do not maintain a parallel pip or Conda workflow.

## Set up the repository

```bash
uv sync --all-extras --all-groups --locked
```

The core dependencies are JAX and Optax. Matplotlib, notebook tooling, and the documentation stack are optional development concerns and remain outside the runtime dependency set.

## Validate changes

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
```

X64 is an explicit application and CI choice. The package never changes global JAX configuration during import.

Ruff enforces complete function annotations and bans importing `typing.Any`. `ty` then checks those annotations across `src/`; public conversion boundaries use `numpy.typing.ArrayLike` rather than leaking JAX-specific types.

## Preview documentation

```bash
uv run mkdocs serve
```

The generated API reference is collected from NumPy-style docstrings with mkdocstrings. Public API changes must update docstrings, the handwritten [API guide](api.md), examples, and an ADR when the decision is durable.

## Benchmark harness

`benchmarks/bench.py` is a deterministic, seeded timing-and-quality harness, not a runtime
promise. It covers every public solver path — `d_exchange`, `lloyd`, `kmeans`, `soft`,
`scalar_dp`, `profiled_exchange`, and `predict` (`QuantizerResult.predict_scores`) — over a
`--rows` × `--dims` × `--bins` × `--scenarios` matrix, reporting wall-clock seconds (minimum over
`--repeats`), process-lifetime peak RSS, and a solver-appropriate quality metric (a log-determinant
objective or a geometric-mean retention) alongside solver diagnostics such as `accepted_moves`,
`scans`, and `exchange_stable`:

```bash
JAX_ENABLE_X64=1 uv run python benchmarks/bench.py --rows 20000,100000 --bins 8,64
JAX_ENABLE_X64=1 uv run python benchmarks/bench.py --rows 200000 --bins 8 --scenarios d_exchange --json out.json
```

`benchmarks/baselines.json` pins a small CI-suitable matrix (recorded machine, Python, and JAX
versions live in its `environment` field; see that file rather than dated prose here for absolute
numbers). Check a fresh run against it with:

```bash
JAX_ENABLE_X64=1 uv run python benchmarks/bench.py --check benchmarks/baselines.json \
  --time-tolerance 2.5 --quality-rtol 1e-6
```

`--check` re-runs exactly the scenarios recorded in the baseline file (its own `--rows`/`--bins`
flags are ignored in this mode) and prints a comparison table. It fails (exit 1) if any scenario
runs slower than `--time-tolerance` times its baseline — deliberately loose, since CI machines
differ — or if a quality metric drifts beyond `--quality-rtol`; deterministic seeds make quality
the real regression signal, since it is exact for a given seed and code path. The `benchmarks` CI
job runs this check after the test suite passes. To refresh `benchmarks/baselines.json` after an
intentional performance or numerical change, regenerate it with `--json` on the same matrix and
review the diff.

## Repository guidance

The root `AGENTS.md` is the durable engineering contract for coding sessions. It records numerical invariants, module boundaries, `uv` commands, validation expectations, and deferred scope.
