# 3. Determinant clustering and partition exchange

> Curated theorem-level annotations. Machine records for the citation graph
> live in `graph.json`; `BIBLIOGRAPHY.md` (generated) maps every registry
> bibliography key to the heading that annotates it.

## Friedman & Rubin (1967)

**Key:** Friedman-Rubin-1967

**Paper:** *On Some Invariant Criteria for Grouping Data*  
**Result:** classical affine-invariant determinant grouping criteria.  
**Use:** determinant partition objectives are old.

- DOI: https://doi.org/10.1080/01621459.1967.10500923

## Scott & Symons (1971)

**Key:** Scott-Symons-1971

**Paper:** *Clustering Methods Based on Likelihood Ratio Criteria*  
**Result:** likelihood/determinant clustering under multivariate models.

- DOI: https://doi.org/10.2307/2529003

## Marriott

Classical determinant-based clustering criteria; useful historical terminology and objective comparison.

## Späth (1977)

**Key:** Spaeth-1977

**Paper:** *Computational experiences with the exchange method: Applied to four commonly used partitioning cluster analysis criteria*  
**Result:** single-point exchange for classical partition criteria including determinant-type criteria.  
**Use:** strong algorithmic prior art for exchange + determinant.

- DOI: https://doi.org/10.1016/S0377-2217(77)81005-9

## Späth (1985)

**Key:** Spaeth-1985

**Book:** *Cluster Dissection and Analysis: Theory, FORTRAN Programs, Examples*  
**Result/use:** determinant exchange routines and matrix/scatter update machinery in executable form.

## Coleman, Dong, Hardin, Rocke & Woodruff (1999)

**Key:** Coleman-et-al-1999

**Paper:** *Some computational issues in cluster analysis with no a priori metric*  
**Result:** computational study of determinant-style clustering and first-improvement versus steepest-ascent moves.

- DOI: https://doi.org/10.1016/S0167-9473(99)00009-2

### Critical distinction from ScoreQuant

Classical determinant clustering usually minimizes a determinant of pooled **within-cluster scatter** or an equivalent Gaussian likelihood criterion.

ScoreQuant maximizes

\[
\det\left(
\sum_bW_b\mu_b\mu_b^\top
\right),
\]

the determinant of retained **between-cell score Fisher information**.

For dimension \(d>1\), fixed total scatter \(T=W+B\) does not make \(\min\det W\) equivalent to \(\max\det B\).
