# ADR 0016: verify partition geometry at the tolerance it was optimized at

**Status:** Accepted; refines the certificate contract of ADR 0014.

## Context

Theorem 3 says a one-point-exchange-stable, nonsingular finite D partition *is* a strict
\(I^{-1}\)-Mahalanobis Voronoi partition of the observed rows: an admissible move that
violates the nearest-centroid rule raises the log determinant by at least
\(\log(1+\alpha\beta q_\delta^2/4)>0\). That implication is what makes
`PartitionResult.compile_quantizer` bookkeeping rather than a new fit, and ScoreQuant
checks it rather than assuming it — in the terminal self-check of `optimize_d_partition`,
in `GeometryReport`, and again inside `compile_quantizer`.

The theorem is exact. The solver is not: it stops when no relocation gains more than
`gain_tolerance`, so what it certifies is exchange stability *at a tolerance* \(\tau\).
All three verifications above compared at tolerance zero — the terminal check and
`compile_quantizer` by testing labels for exact equality against the rule, `GeometryReport`
by testing a distance gap against `0.0`.

That mismatch is invisible on small samples and fatal on large ones. The guaranteed gain
\(\log(1+\alpha\beta q_\delta^2/4)\) is driven by the cell separation \(q_\delta\), which
falls like \(1/N\) as the sample grows, so the guarantee falls like \(1/N^2\). Around
\(N=10^6\) it drops below the default \(\tau=10^{-10}\), and exchange stability at \(\tau\)
stops forbidding a row from sitting a hair past a cell boundary. The profiling campaign
measured exactly that: a converged 1 000 000-row, rank-3, 8-cell D-exchange fit — 280
scans, 99 001 accepted moves, `exchange_stable=True`, `best_remaining_gain` \(=8.7\times
10^{-11}\) — was rejected outright by

```
ValueError: terminal D state is geometrically degenerate;
duplicate/tied score atoms must be merged or assigned consistently
```

because 13 rows out of a million disagreed with the terminal Voronoi rule, by an absolute
Mahalanobis gap of about \(10^{-11}\) on distances of order \(1.5\times 10^{-6}\). The
guaranteed gain of those violations was \(2.2\times 10^{-11}\) and their exact gain
\(8.7\times 10^{-11}\), both under \(\tau\). Nothing was degenerate; the certificate was
issued at \(\tau\) and then verified at zero. The guarded Mahalanobis-Lloyd solver tripped
identically, since it shares the terminal check.

Two further mismatches were tangled into the same code. The verdict was taken on a
Mahalanobis *distance gap* while the solver stops on a log-determinant *gain*, which are
different units and only agree to first order at unit row weight; and neither
`StabilityReport` nor `GeometryReport` recorded the tolerance it was issued at, so a reader
could not tell what had actually been certified.

## Decision

**A certificate states the tolerance it holds at, and every verification uses a tolerance
consistent with the optimizer that produced the partition.** Concretely:

- The verdict is taken in **gain units**, never on a distance gap compared to zero. The
  quantity is the exact log-determinant gain of the offending relocation, computed by the
  same per-row kernel the exchange scan uses. `GeometryReport` gains
  `maximum_violation_gain` — the largest exact gain over admissible Voronoi-violating
  moves — and `voronoi_consistent` now means `maximum_violation_gain <= gain_tolerance`.
  `maximum_voronoi_violation` survives unchanged as a diagnostic, and
  `guaranteed_violation_gain` is retained as the Theorem-3 lower bound on the same
  quantity, so `guaranteed_violation_gain <= maximum_violation_gain` is an invariant the
  report now makes checkable.
- The terminal check in `optimize_d_partition` compares the terminal labels against the
  terminal Voronoi rule as before, but prices each disagreement: a row may be relabeled by
  the rule only when relocating it there gains at most `gain_tolerance`. A row whose cell
  holds no other weight admits no relocation at all, so no tolerance can excuse a rule that
  moves it; that case still raises.
- The tolerance is **not a new parameter**. It is `config.gain_tolerance` of the
  configuration that produced the labels — the only tolerance the result was ever optimized
  at. `exchange_stability_report` keeps its existing `gain_tolerance` argument, because it
  certifies labels of unknown origin and must be told which tolerance to hold them to.
  `compile_quantizer` takes no tolerance argument: overriding it would let a caller claim a
  certificate at a tolerance the optimizer never ran at.
- Both certificates record their tolerance: `StabilityReport.gain_tolerance` and
  `GeometryReport.gain_tolerance`.
- `compile_quantizer` delegates. Only the solver holds the row weights an exact relocation
  gain needs, so a `PartitionResult` cannot re-derive one; on a disagreement it accepts the
  tolerance-stamped `geometry` certificate and refuses when that certificate is absent or
  not `voronoi_consistent`.
- **Assignment is untouched.** `predict_scores` keeps the ordinary `argmin` rule, which is
  deterministic and resolves a tie toward the lowest cell index. The tolerance governs
  verification only; a boundary tie is assigned, not deferred.

Theorem 3 itself is unchanged and stays exact. What changes is the honest statement of the
compile bridge: the compiled rule is **self-consistent at tolerance \(\tau\)** — it
reproduces every training label except on rows whose relocation is worth at most \(\tau\).
The docstrings, `docs/api.md`, `docs/method.md`, and the practical-bridge paragraph of
[Chapter 8](../book/ch08-d-optimality.md) say so; the theorem statement in that chapter is
left mathematical, with the tolerance confined to the finite-precision verification that
follows it.

## Consequences

- A converged 10^6-row D-exchange or Mahalanobis-Lloyd fit is usable again: it returns,
  reports `voronoi_consistent=True` at its stated tolerance, and compiles. The open scale
  limit recorded in `benchmarks/README.md` is closed.
- `compile_quantizer` no longer promises bit-exact label reproduction. On a partition with
  boundary rows inside \(\tau\), `predict_scores` on the training scores differs from
  `PartitionResult.labels` on those rows, and `QuantizerResult.labels` keeps the
  partition's labels, which stay authoritative for the fixed sample. The induced objective
  difference is bounded by \(\tau\) per relabeled row.
- Optimization paths are untouched: only verification changed, and the golden engine
  fixtures are bit-identical.
- `GeometryReport` and `StabilityReport` each gain fields, so `to_dict()` output grows.
  Neither type is constructed outside the library.
- A tighter certificate is still available on demand: `exchange_stability_report(...,
  gain_tolerance=0.0)` verifies at exactly zero and will report an in-tolerance boundary
  row as an improving move, which is the correct answer to a different question.
- The relationship between \(\tau\) and sample size is now a documented property rather
  than a surprise. A caller who wants Voronoi self-consistency at a smaller gap on a large
  sample must lower `gain_tolerance` and pay for the extra scans, and the certificate will
  say which tolerance was bought.
