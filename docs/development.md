# Development

FisherBin uses [uv](https://docs.astral.sh/uv/) for environments, dependencies, command execution, locking, and package builds. Do not maintain a parallel pip or Conda workflow.

## Set up the repository

```bash
uv sync --all-extras --all-groups --locked
```

The core dependencies are JAX and Optax. Matplotlib, notebook tooling, and the documentation stack are optional development concerns and remain outside the runtime dependency set.

## Validate changes

```bash
uv run ruff check .
uv run ruff format --check .
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
```

X64 is an explicit application and CI choice. The package never changes global JAX configuration during import.

## Preview documentation

```bash
uv run mkdocs serve
```

The generated API reference is collected from NumPy-style docstrings with mkdocstrings. Public API changes must update docstrings, the handwritten [API guide](api.md), examples, and an ADR when the decision is durable.

## Repository guidance

The root `AGENTS.md` is the durable engineering contract for coding sessions. It records numerical invariants, module boundaries, `uv` commands, validation expectations, and deferred scope.
