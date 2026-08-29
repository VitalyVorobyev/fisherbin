# 2. Trace control case

> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and
> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.
> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.

## T1. Fisher-whitened normalized trace equals weighted k-means — [BRIDGE; essentially known]

**Claims:** TRACE-WHITENED-KMEANS

With

\[
z=I_{\rm full}^{-1/2}s,
\]

\[
\boxed{
d-\operatorname{tr}(I_{\rm full}^{-1}I_q)
=E\|z-E[z\mid Z]\|^2.
}
\]

Therefore maximizing normalized retained trace is exactly squared-error vector quantization / weighted k-means in whitened score space.

This is useful as a baseline, not a headline novelty claim.

---
