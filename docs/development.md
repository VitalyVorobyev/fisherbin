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

## Exact-D scale benchmark

`benchmarks/exact_d.py` is a deterministic engineering benchmark, not a runtime promise:

```bash
uv run python benchmarks/exact_d.py --rows 200000 --max-sweeps 10
uv run python benchmarks/exact_d.py --rows 1000000 --max-sweeps 1
```

On the 2026-08-25 development machine (Apple Silicon, JAX CPU, float32), the first command took
2.53 seconds with 569 MiB peak RSS and accepted ten moves. The one-million-row scan took 3.71
seconds with 1.29 GiB peak RSS and accepted one move. Candidate gains are scanned in deterministic
memory-bounded chunks; accepted moves update cell moments, information, and its inverse in
\(O(P^2)\), with a residual-checked full inverse fallback. Initialization and stored input arrays
still scale with \(N\), so these measurements do not claim full-corpus or one-pass fitting.

## Repository guidance

The root `AGENTS.md` is the durable engineering contract for coding sessions. It records numerical invariants, module boundaries, `uv` commands, validation expectations, and deferred scope.
