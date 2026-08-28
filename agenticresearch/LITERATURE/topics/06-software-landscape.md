# 6. Software landscape

> Curated theorem-level annotations. Machine records for the citation graph
> live in `graph.json`; `BIBLIOGRAPHY.md` (generated) maps every registry
> bibliography key to the heading that annotates it.

## Historical determinant partitioning

- Späth FORTRAN code: direct historical example of determinant exchange and matrix-update implementation.

## Optimal design packages — adjacent

Useful for algorithms/terminology, not direct hard score quantization:

- PyOptEx
- PyDOE optimal-design functionality
- optdesign
- BoFire / DoE ecosystems
- OApackage

## HEP/inference-aware toolkits — adjacent

- MadMiner: score/likelihood-ratio estimation and local optimal observables.
- INFERNO implementations: differentiable inference-aware summaries.
- ThickBrick-related categorization code where available.
- Learning-to-bin / modern differentiable category optimizers.

## General binning packages

- OptBinning and related supervised binning packages solve different objectives (predictive/monotonic/statistical binning), useful only as engineering/interface references.

## Current software gap

No public package was identified whose central abstraction is:

> multivariate hard score-space quantization with D and \(D_s\) objectives, exact information accounting, direct-score / density-ratio / calibrated-classifier interfaces, deployable partitions, and theorem-aware optimality diagnostics.

This is a **search gap**, not a proof of uniqueness.

---
