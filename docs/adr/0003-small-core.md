# ADR 0003: Keep optional concerns outside the core

**Status:** Accepted

## Decision

The initial core contains information calculations, quantizers, diagnostics, and the linear-component adapter.

The following are deferred until justified by real use cases: learned score estimation, multiple compute backends, services, plugin systems, large experiment schemas, compiled deployment runtimes, and the frontend.

A future UI must call the library rather than duplicate the statistical method.

## Why

The project should first prove the method and establish a clean API. Premature infrastructure would make both implementation and future changes harder.
