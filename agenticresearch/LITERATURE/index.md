# Literature — index

> Discovery state for the ScoreQuant prior-art search. Procedure lives in
> `protocols/literature.md`; PDFs, where held, are in `../../papers/`.

## Files

| File | Role |
|---|---|
| `BIBLIOGRAPHY.md` | **Generated.** Registry bibliography key -> annotating heading. |
| `topics/` | Curated theorem-level annotations, one file per research community. |
| `audits/` | Dated targeted prior-art searches, one per audited claim. |
| `graph.json` | Machine paper records for citation snowballing (`rounds`, `papers`). |
| `seeds.md` | Anchor papers for bidirectional traversal. |
| `reviewed.md`, `rejected.md`, `gaps.md` | Human-readable outcomes and coverage gaps. |

## Topics

- `topics/01-optimal-design.md` — 1. Optimal experimental design backbone
- `topics/02-fisher-quantization.md` — 2. Fisher-information quantization
- `topics/03-determinant-clustering.md` — 3. Determinant clustering and partition exchange
- `topics/04-vector-quantization.md` — 4. Vector quantization and Voronoi theory
- `topics/05-hep-inference-aware.md` — 5. Inference-aware summaries and HEP categorization
- `topics/06-software-landscape.md` — 6. Software landscape
- `topics/07-score-compression.md` — 9. Additional score-compression and ratio-estimation sources (v2 update)

## 7. Paper reading order for literature study

(This orders the *papers* below for a literature deep-dive; the workspace read
order is defined once, in `README.md`.)

1. `PROBLEM.md`
2. Kiefer–Wolfowitz (D sensitivity/equivalence)
3. Whittle + Wynn 1972 + Näther–Reinsch (\(D_s\), general criteria)
4. Venkitasubramaniam–Tong–Swami (score quantization)
5. Barnes–Han–Özgür (multivariate quantized-FI geometry)
6. Dülek (trace-optimal polytopal quantizers)
7. Späth 1977/1985 + Coleman et al. (determinant exchange prior art)
8. Pollard + CVT/Lloyd literature (population consistency/geometric algorithms)
9. SALLY/SALLINO, INFERNO, ThickBrick, Learning to bin (HEP/practical inference-aware context)
10. `KNOWN_RESULTS/` and the project theorem registry

---

## 8. Search vocabulary for new prior art

Use combinations of:

- D-optimal quantization
- determinant Fisher information quantizer
- D_s optimal quantization
- nuisance-parameter optimal quantizer
- Fisher-information partition
- score-space quantization
- score-function quantization
- sufficient-statistic quantizer
- conditional score Fisher information
- determinant clustering exchange
- minimum determinant partition
- Hartigan determinant clustering
- Mahalanobis Voronoi quantization
- information preserving binning
- inference-aware categorization
- optimal event categories
- template fit bin optimization
- density-ratio binning Fisher information
- communication-constrained estimation Fisher quantization

Always inspect the actual theorem/objective; title-level similarity is not enough.
