# 10. Plug-in asymptotics for retention functionals

> Curated theorem-level annotations. Machine records for the citation graph
> live in `graph.json`; `BIBLIOGRAPHY.md` (generated) maps every registry
> bibliography key to the heading that annotates it. Opened 5 September 2026
> for `RETENTION-PLUGIN-CLT-FROZEN-SCALAR` (O6); every entry states its
> verification status — no primary text was read in the opening round.

## van der Vaart (1998) — Asymptotic Statistics

**Key:** vanderVaart-1998

**Paper:** *Asymptotic Statistics*, Cambridge University Press.
**Result:** Theorem 3.1 (delta method): if \(r_n(T_n-\theta)\Rightarrow T\) and
\(\phi\) is differentiable at \(\theta\), then \(r_n(\phi(T_n)-\phi(\theta))\Rightarrow\phi'_\theta(T)\).
Chapter 3 works the sample variance under \(E X^4<\infty\); Chapter 5
(Theorem 5.23) gives the M-estimator sandwich and the plug-in variance
principle.
**Use:** O6.2 is this theorem applied to the sample-mean vector of
\((\mathbf 1_{Z=b}, S\mathbf 1_{Z=b}, S^2)\); O6.3's consistency argument is the
plug-in principle made explicit for a polynomial functional.
**Verification:** theorem numbers confirmed through secondary quotations only.

## Cramér (1946) — Mathematical Methods of Statistics

**Key:** Cramer-1946

**Paper:** *Mathematical Methods of Statistics*, Princeton University Press.
**Result:** Chapter 28, functions of sample moments: a smooth function of
sample moments is asymptotically normal with variance from the first-order
expansion, under the moment conditions that make the underlying sample moments
asymptotically normal.
**Use:** the oldest form of O6.2's argument; the fourth-moment condition (A2)
is exactly the classical condition for the second sample moment.
**Verification:** cited from memory; section numbering unverified.

## Serfling (1980) — Approximation Theorems of Mathematical Statistics

**Key:** Serfling-1980

**Paper:** *Approximation Theorems of Mathematical Statistics*, Wiley.
**Result:** Chapter 3 (transformations of given statistics), Section 3.3
Theorem B: the multivariate delta method for functions of asymptotically normal
vectors.
**Use:** alternative citation for O6.2 with the gradient-covariance form
\(\nabla g^\top\Sigma\nabla g\) stated explicitly.
**Verification:** Theorem B corroborated by two secondary citations; the
univariate Theorem A label unverified.

## Hampel, Ronchetti, Rousseeuw & Stahel (1986) — influence functions

**Key:** Hampel-Ronchetti-Rousseeuw-Stahel-1986

**Paper:** *Robust Statistics: The Approach Based on Influence Functions*, Wiley.
**Result:** for a statistical functional \(T\) at \(F\), the asymptotic variance
is \(V(T,F)=\int \mathrm{IF}(x;T,F)^2\,dF(x)\).
**Use:** O6.2's \(\sigma^2=E[\psi^2]\) is this formula; O6's selftest checks
the closed-form \(\psi\) against Gateaux finite differences, which is the
definition of the influence function.
**Verification:** book confirmed; section number unverified.

## Wishart (1932) — distribution of the correlation ratio

**Key:** Wishart-1932

**Paper:** *A note on the distribution of the correlation ratio*, Biometrika
24(3/4):441–456.
**Result:** normal-theory exact distribution of the sample correlation ratio
\(\eta^2\) (between-group over total centred sum of squares).
**Use:** lineage only — O6's \(\hat\eta\) is the *uncentred* correlation ratio
of \(S\) on \(Z\) with a fixed partition; nothing normal-theory transfers.
**Verification:** existence and pages from the Biometrika contents index;
text not read.

## Kelley (2007) — confidence intervals for standardized effect sizes

**Key:** Kelley-2007

**Paper:** *Confidence intervals for standardized effect sizes: theory,
application, and implementation*, Journal of Statistical Software 20(8).
**Result:** noncentral-\(F\)/\(t\)/\(\chi^2\) confidence intervals for
\(\eta^2\), \(R^2\) and Cohen's \(d\) under normal-theory ANOVA (MBESS).
**Use:** the standard applied route for \(\eta^2\) intervals, assuming
Gaussian errors and a fixed design; O6 replaces that assumption by
\(E S^4<\infty\) and a first-order limit.
**Verification:** verified at jstatsoft.org.
