# 9. Additional score-compression and ratio-estimation sources (v2 update)

> Curated theorem-level annotations. Machine records for the citation graph
> live in `graph.json`; `BIBLIOGRAPHY.md` (generated) maps every registry
> bibliography key to the heading that annotates it.

## Heavens, Jimenez & Lahav (2000) — MOPED

**Paper:** *Massive Lossless Data Compression and Multiple Parameter Estimation from Galaxy Spectra*  
**Result:** continuous linear compression to one summary per parameter preserving Fisher information under the paper's assumptions.  
**Use:** important ancestor for the “unbinned score/continuous compression is the information reference” viewpoint; not a finite hard quantizer.

- arXiv PDF: https://arxiv.org/pdf/astro-ph/9911102

## Alsing & Wandelt (2018) — generalized score compression

**Paper:** *Generalized Massive Optimal Data Compression*  
**Result:** likelihood-score compression gives locally Fisher-optimal continuous summaries under broad regularity conditions.  
**Use:** direct conceptual bridge from full observations to the score-space representation before finite quantization.

- arXiv PDF: https://arxiv.org/pdf/1712.00012

## Brehmer et al. — SALLY/SALLINO and MadMiner

**Use:** learned likelihood-score representations and practical score-space histograms in HEP. Establishes that learned scores and score histograms are prior art; ScoreQuant's question is how to optimize the hard cells under D/\(D_s\).

- Mining Gold PDF: https://arxiv.org/pdf/1805.12244
- MadMiner PDF: https://arxiv.org/pdf/1907.10621

## Wunsch et al. (2021)

**Paper:** *Optimal Statistical Inference in the Presence of Systematic Uncertainties Using Neural Network Optimization Based on Binned Poisson Likelihoods with Nuisance Parameters*  
**Use:** close HEP comparator for differentiable binned likelihood optimization with nuisances.

- arXiv PDF: https://arxiv.org/pdf/2003.07186

## Simpson & Heinrich (2022/23) — neos

**Paper:** *neos: End-to-End-Optimised Summary Statistics for High Energy Physics*  
**Use:** differentiable end-to-end expected-sensitivity optimization; adjacent software baseline, not score-Fisher hard partition theory.

- arXiv PDF: https://arxiv.org/pdf/2203.05570

## Density-ratio estimation

Direct density-ratio estimation (KLIEP, uLSIF and related methods) is a mature alternative to separately estimating component densities. Classifier posterior odds are another route. For ScoreQuant these are **model-access backends**, not the quantizer itself.

Useful reference: Sugiyama, Suzuki & Kanamori, *Density Ratio Estimation in Machine Learning*.

### Research-agent instruction

When a theorem depends on a density-ratio/classifier assumption, search the ratio-estimation literature separately from the quantization literature. Do not infer exact Fisher preservation merely from classifier discrimination performance.
