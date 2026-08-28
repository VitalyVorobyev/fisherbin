# Targeted audit for the DS-POPULATION-BRIDGE claims — 28 August 2026

**Key:** Li-Mathias-2000

The independent audit (`AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md`) reran the
novelty searches for DS11–DS14 with fresh queries. Two outcomes.

**DS11 (`DS-PROFILED-VARIATIONAL`): prior art found.** The boxed identity is
the extremal characterization of the generalized Schur complement.

- **Li & Mathias (2000)**, *Extremal Characterizations of the Schur Complement
  and Resulting Inequalities*, SIAM Review 42(2):233–246,
  doi:10.1137/S0036144599337290. **Exact problem:** PSD block matrix \(H\),
  generalized Schur complement \(S(H)=H_{22}-H_{12}^*H_{11}^\dagger H_{12}\).
  **Exact result (Thm 2.2):** \([Z|I]H[Z|I]^*\ge S(H)\) in the Loewner order
  for every \(Z\), equality iff \((Z+H_{12}^*H_{11}^\dagger)H_{11}=0\).
  **Transfers:** with \(Z=-B\) this is DS11's identity verbatim, including the
  Moore–Penrose extension and the exact attainment set \(BI_{\lambda\lambda}
  =I_{\psi\lambda}\). The paper attributes the characterization to **M. G.
  Krein (1947)** and notes **Anderson's shorted operator (1971;
  Anderson–Trapp 1975)** and Butler–Morley as independent sources.
  **Does not cover:** the binned-score reading via U1 (which needs centered
  scores), the refinement-neutrality/wasted-cell corollaries on the quantizer
  feasible set, and the DS9 feasibility-boundary observation — those stay
  project-level.
- **Classical statistics form:** the efficient score
  \(\ell_\psi-I_{\psi\lambda}I_{\lambda\lambda}^{-1}\ell_\lambda\) with
  variance the Schur complement (van der Vaart 1998 §25.4;
  Bickel–Klaassen–Ritov–Wellner 1993) is the nonsingular statistical special
  case; best-linear-predictor/partial-covariance algebra is the regression
  form.

**DS12–DS14: search gap re-confirmed.** Independent queries (adaptive/
Mahalanobis quantizer consistency with solution-dependent metrics;
determinant-criterion partition consistency; profiled-Fisher binning in HEP)
found no direct equivalent. New nearest-practice sources recorded:

- **INFERNO (de Castro & Dorigo 2018)** and **binned Poisson-likelihood NN
  optimization (Wunsch et al. 2020, doi:10.1007/s41781-020-00049-5)**:
  optimize profiled/Asimov Fisher information of binned likelihoods with
  nuisance parameters through soft binning — the engineering practice a DS14
  bridge would certify. **Does not transfer:** algorithms only; no hard-bin
  finite-to-population consistency statement, no margin analysis.
- **"Learning to bin" (2026, arXiv:2601.07756)**: differentiable/Bayesian
  optimization of multi-dimensional hard binnings for HEP discriminants;
  same status — optimization practice, no consistency theory.

The Pollard/Graf–Luschgy/Sabin–Gray non-transfer table above was re-checked
against the original settings and stands: fixed source-independent metrics
and additive per-point distortion throughout; no determinant/Schur functional
of aggregated cell moments, no fitted-semimetric self-consistency.
