# ADR 0004: Use a JAX-native core with an array-oriented boundary

**Status:** Accepted

## Context

The first implementation needs both ordinary information calculations and differentiable optimization. Maintaining separate NumPy and autodiff implementations would duplicate the most important equations and their numerical edge cases.

## Decision

JAX implements information calculations, transforms, weighted k-means, prediction, and soft Voronoi optimization. Optax provides the gradient optimizer. Public functions accept array-like values and expose domain concepts rather than backend services or registries.

The library does not enable X64 globally. Applications and CI choose precision before JAX initialization. A formal backend abstraction remains deferred until a second backend has concrete requirements.

## Consequences

There is one executable mathematical implementation and fitted calculations remain device-capable. JAX is a required v0.1 dependency, while Matplotlib and notebook tooling remain optional. Future backends may require result-array adaptation, but the fit/config/report workflow need not change.
