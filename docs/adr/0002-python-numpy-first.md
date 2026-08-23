# ADR 0002: Start with a small Python/NumPy implementation

**Status:** Accepted

## Decision

Python is the public API and NumPy is the reference implementation. PyTorch may be added as an optional dependency for differentiable optimization.

Do not add compiled backends until profiling shows they are needed.

## Why

The mathematical core is small. Clarity, correctness, and adoption matter more than speculative performance architecture.
