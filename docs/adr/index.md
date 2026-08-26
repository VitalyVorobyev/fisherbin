# Architecture Decision Records

Only decisions that materially constrain future implementation are recorded here.

1. [ADR 0001 — Scores are the core data contract](0001-score-contract.md)
2. [ADR 0002 — Start with a small Python/NumPy implementation](0002-python-numpy-first.md) — superseded
3. [ADR 0003 — Keep optional concerns outside the core](0003-small-core.md)
4. [ADR 0004 — Use a JAX-native core with an array-oriented boundary](0004-jax-first.md)
5. [ADR 0005 — Make variables, components, and scores explicit API layers](0005-explicit-representations.md) — superseded
6. [ADR 0006 — Publish generated documentation through GitHub Pages](0006-documentation-site.md)
7. [ADR 0007 — Evolve the API around generic statistical contracts](0007-generic-api-evolution.md)
8. [ADR 0008 — Expose only the mathematical classifier-posterior bridge](0008-classifier-posterior-bridge.md) — superseded in part
9. [ADR 0009 — Separate finite partitions from quantizers](0009-partition-quantizer-separation.md)
10. [ADR 0010 — Separate sources from score providers](0010-source-provider-separation.md)
11. [ADR 0011 — Keep solver semantics criterion-specific](0011-criterion-specific-semantics.md) — partially superseded by ADR 0014
12. [ADR 0012 — Keep classifier training outside the core](0012-classifier-callback-boundary.md)
13. [ADR 0013 — Complete the pre-1.0 API with capability-specific boundaries](0013-complete-pre-1-api-boundaries.md) — partially superseded by ADR 0014
14. [ADR 0014 — One exchange engine with criterion-specific objectives and explicit certificates](0014-unified-exchange-and-certificates.md)
15. [ADR 0015 — Efficient-score upper bound and solver initialization](0015-efficient-score-bound-and-initialization.md)
16. [ADR 0016 — Verify partition geometry at the tolerance it was optimized at](0016-tolerance-consistent-geometry-verification.md) — refines ADR 0014
