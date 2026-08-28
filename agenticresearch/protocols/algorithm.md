# Protocol: algorithm development

## Evaluate separately

- **Exact objective.** Do not label a surrogate D/\(D_s\) unless it is
  mathematically equal to the target.
- **Monotonicity.** State whether each accepted update is guaranteed to
  improve the exact objective (recall the adaptive-Lloyd counterexample:
  batch proposals must be accepted only against the exactly rebuilt
  objective).
- **Terminal meaning.** Exchange-stable? Restricted-family stationary?
  Global? Certified gap?
- **Complexity.** Report in \(N,K,d\), and for \(D_s\) also \(d_\psi\).
- **Numerical stability.** Prefer Cholesky/log-det; retain full recomputation
  paths for validation.
- **Initialization.** Compare Fisher-whitened k-means, random/multistart,
  projected efficient-score D, and domain-specific initialization.

## Deployment semantics

- D exchange terminal state: compile exactly using final centroids +
  \(I^{-1}\) (theorem-backed).
- \(D_s\)/E finite assignment: do **not** silently compile; fitting/projection
  to a geometric family is a new optimization step and must report objective
  loss.

## Evaluation report

On training and held-out samples report: objective; D/\(D_s\) efficiency;
normalized retention spectrum; worst direction; minimum cell mass/yield;
restart/bootstrap stability; upper/lower certificate gap if available;
geometry disagreement for \(D_s\)/E finite oracles.

## Special \(D_s\) protocol

Always distinguish:

- **In-bin profiled \(D_s\)** — nuisance information learned from the same
  categorical observation. Use the Schur complement, never the POI block
  alone.
- **Full-data efficient-score projected D upper problem** — uses
  \(\widehat S=S_\psi-B^*S_\lambda\) with \(B^*\) from full information; it
  upper-bounds in-bin \(D_s\) and may use nuisance information external to
  the bins. For \(d_\psi=1\) solve the projected scalar interval problem
  exactly by DP when appropriate.

A strong practical solution reports
\(\text{upper projected-D value}-\text{achieved in-bin }D_s\text{ value}\).
