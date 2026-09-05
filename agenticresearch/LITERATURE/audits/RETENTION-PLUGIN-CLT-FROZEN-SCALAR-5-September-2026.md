# Targeted prior-art triangulation: O6 (RETENTION-PLUGIN-CLT-FROZEN-SCALAR)

Run 5 September 2026 by the SCORE-ORACLE-ROBUSTNESS researcher session
(`protocols/literature.md`, per-theorem minimum) on the frozen O6 statements:
the RSS identity (O6.1), the conditional CLT with influence function
\(\psi=((1-\eta)S^2-(S-c_Z)^2)/v\) (O6.2), the consistent plug-in variance
(O6.3) and the Wald interval with its \(\sigma^2=0\) characterisation (O6.4).
Retrieval was delegated (web verification of metadata; no primary text read);
triangulation judgments are the researcher's. Registration: round 9 of
`LITERATURE/graph.json`; annotations in `topics/08-plug-in-asymptotics.md`.
`literature_search_status` on the claim is `prior_art_found`: the method is
textbook and no novelty is claimed. The specific closed-form influence
function for the uncentred fixed-partition ratio and the two-atoms-per-cell
degeneracy were not located as stated; they are project algebra inside a
bridge node, not a search gap.

## Triangulation (six fields per source)

- **van der Vaart (1998), *Asymptotic Statistics*, CUP, Thm 3.1; Ch. 3
  sample-variance example; Ch. 5 Thm 5.23.** *(theorem numbers via secondary
  quotations)* **Exact problem:** limit law of \(\phi(T_n)\) given
  \(r_n(T_n-\theta)\Rightarrow T\). **Exact result:** delta method; sandwich
  variances for M-estimators. **Objective:** none (limit theory).
  **Feasible set:** any differentiable \(\phi\) at \(\theta\). **What
  transfers:** everything in O6.2 — \(\hat\eta\) is \(g\) of a sample-mean
  vector, \(g\) is smooth on \(\{p_b>0,v>0\}\), finite fourth moment gives the
  CLT for \(S^2\). **What does not:** the empty-cell convention and the
  \(\sigma^2=0\) cases are outside the theorem (handled separately in O6.2/O6.4).
- **Cramér (1946), *Mathematical Methods of Statistics*, Ch. 28, functions of
  sample moments.** *(from memory; numbering unverified)* **Exact
  problem/result:** normal limit of smooth functions of sample moments with
  first-order variance. **What transfers:** the classical statement of the
  same fact; the moment condition. **What does not:** no partition structure.
- **Serfling (1980), *Approximation Theorems*, Sec. 3.3 Thm B.** *(Thm B
  corroborated; Thm A label unverified)* **Exact result:** multivariate delta
  method with \(\nabla g^\top\Sigma\nabla g\). **What transfers:** the
  gradient-covariance form used to expose the numerator–denominator
  covariance in O6.2. **What does not:** nothing further.
- **Hampel, Ronchetti, Rousseeuw & Stahel (1986), *Robust Statistics*.**
  *(section number unverified)* **Exact result:**
  \(V(T,F)=\int\mathrm{IF}^2\,dF\). **What transfers:** \(\sigma^2=E[\psi^2]\)
  and the Gateaux-derivative definition the selftest checks. **What does
  not:** robustness content (breakdown, gross-error sensitivity) is unused;
  note \(\psi\) is unbounded in \(S\), so \(\hat\eta\) is not robust.
- **Wishart (1932), Biometrika 24:441–456; Kelley (2007), JSS 20(8).**
  *(existence verified; texts not read)* **Exact problem:** distribution and
  confidence intervals of the centred correlation ratio \(\eta^2\) under
  normal-theory ANOVA. **What transfers:** the name and the identity
  "between over total" (O6.1 is its uncentred, fixed-partition form). **What
  does not:** normality, centring, noncentral-\(F\) intervals.

## Gaps

- Kendall & Stuart, *Advanced Theory of Statistics* Vol. 2, is expected to
  contain the asymptotic variance of the sample correlation ratio under
  non-normality but was not located to a section; not registered.
- A direct statement of O6.2's influence function for an uncentred ratio with
  a fixed partition was not found. It would be surprising if it were new;
  before any publication use, a dedicated novelty search on "asymptotic
  variance of the (uncentred) correlation ratio" and on the ANOVA
  \(\eta^2\) delta-method literature is required (protocol: a search gap is
  not novelty).
