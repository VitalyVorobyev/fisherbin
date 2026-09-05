# RETENTION-PLUGIN-VECTOR — error bars for the vector geometric-mean retention under a frozen rule

**Programme:** P4 (OP27) · **Opened:** 5 September 2026 · **Status:** active
**Source:** branch `score-oracle-robustness` after the O6 audit commit (check it out first)

## Goal

Extend O6 (`RETENTION-PLUGIN-CLT-FROZEN-SCALAR`, audited
`AUDITS/AUDIT-SCORE-ORACLE-ROBUSTNESS-001.md`) from one score coordinate to
a \(d\)-dimensional true score. The target is the number the library
actually reports for a frozen rule on an oracle-score evaluation sample,
`information_report(...).geometric_mean_retention`:

\[
\eta_D=\Big(\frac{\det I_Z}{\det V}\Big)^{1/d},\qquad
V=E[SS^\top],\qquad I_Z=\sum_b\frac{m_bm_b^\top}{p_b},\qquad
m_b=E[S\,\mathbf 1_{Z=b}],
\]

with the plug-in \(\hat\eta_D\) built from the same cell moments
(\(0/0:=0\) on empty cells). The question: **is \(\sqrt n(\hat\eta_D-\eta_D)\)
asymptotically normal with an explicit, consistently estimable variance, and
exactly where does the log-determinant degenerate?** This is the matrix
influence function O6.8 named as the missing derivation.

## Independence and scope

- Build on O6 as audited; do not re-prove it. Reuse its normalisation
  (frozen rule, iid equally weighted evaluation sample from the reference
  law, scores never centred) and its assumptions (A1)–(A3) in matrix form.
- Falsify before proving (`protocols/numerical.md`): exact rationals, \(d=2,3\),
  smallest rank-feasible \(K\) (\(I_Z\) has rank \(\le K\), and \(\le K-1\)
  when \(E[S]=0\): `FI-RANK-CEILING`), duplicate atoms, singleton and empty
  cells, near-singular \(V\) and near-singular \(I_Z\).
- Out of scope, flag only: refitted rules (the boundary non-smoothness of
  OP27), weights, \(D_s\)/profiled retention, bootstrap comparisons, any
  public uncertainty API. No `src/` change.

## Attack plan

1. **Finite identity.** Show \(\hat\eta_D\) equals the library's
   `geometric_mean_retention` whenever \(\hat V\succ0\) and no direction is
   projected out: the whitening \(\hat V^{-1/2}\) cancels in the determinant
   ratio, so \(\hat\eta_D=(\det\hat I_Z/\det\hat V)^{1/d}\). Name exactly what
   the library's `rank_rtol` projection does to the plug-in when \(\hat V\) is
   numerically singular (a discontinuity of the estimator, outside the CLT).
   Generalise the RSS identity: \(\hat V-\hat I_Z=\) within-cell scatter about
   cell means, so \(\hat I_Z\preceq\hat V\) and \(0\le\hat\eta_D\le1\).
2. **Smoothness and the delta method.** \(T=(\mathbf 1_{Z=b}, S\mathbf 1_{Z=b},
   \operatorname{vech}(SS^\top))_b\); \(g(p,M,V)=(\det\sum_b m_bm_b^\top/p_b/\det V)^{1/d}\)
   is \(C^\infty\) on \(\{p_b>0,\ I_Z\succ0,\ V\succ0\}\). Assumptions:
   (A1) \(p_b>0\); (A2) \(E\|S\|^4<\infty\); (A3) \(V\succ0\);
   **(A3′) \(I_Z\succ0\)** — the new hypothesis, which needs \(K\ge d+1\)
   under \(E[S]=0\); (A4) \(\sigma^2>0\).
3. **The matrix influence function.** From \(d\log\det A=\operatorname{tr}(A^{-1}dA)\),
   derive
   \[
   \psi(S,Z)=\frac{\eta_D}{d}\Big[\,2S^\top I_Z^{-1}c_Z-c_Z^\top I_Z^{-1}c_Z-S^\top V^{-1}S\,\Big]
   \quad(\text{conjectured form; verify}),
   \]
   with \(c_b=m_b/p_b\); check \(E[\psi]=0\) exactly (the trace identities
   \(\sum_bp_bc_b^\top I_Z^{-1}c_b=\operatorname{tr}(I_Z^{-1}I_Z)=d\) and
   \(E[S^\top V^{-1}S]=d\)) and that \(d=1\) recovers O6.2's
   \(\psi=((1-\eta)S^2-(S-c_Z)^2)/v\). Give the covariance form
   (numerator/denominator log-determinant influences).
4. **Consistent variance.** \(\hat\sigma^2=n^{-1}\sum\hat\psi_i^2\) as a
   continuous function of within-cell moments of order \(\le4\)
   (\(E[S_iS_jS_kS_l\mathbf 1_{Z=b}]\)); a.s. consistency under (A1)–(A3′).
5. **Degeneracies.** Characterise \(\sigma^2=0\): \(\psi=0\) a.s. is a
   quadratic variety per cell; state which laws sit on it, including
   \(\eta_D\in\{0,1\}\) (learn from O6's \(\eta=0\) correction: check the
   endpoints separately). Say what happens when \(I_Z\) is singular
   (\(\eta_D=0\) exactly, \(\log\det=-\infty\)): the plug-in is then
   \(O_p(1/n)\)-biased upward from 0 and the interval is unsupported.
6. **Closed-form references and falsification.** A \(d=2\) law with
   closed-form cell moments: e.g. the two-parameter Gaussian location–scale
   score \(S=(x-\mu,\,((x-\mu)^2-\sigma^2)/\sigma)\) under a fixed interval
   partition of \(x\) (moments are Gaussian-CDF/PDF differences), or the
   door2 three-component mixture (\(d=2\), `examples/door2_mixture_densities.py`)
   with a frozen D-exchange rule and quadrature references. Coverage at
   \(n=100,300,1000,3000\), \(\ge2000\) replicates, fresh seeds, deterministic
   revision and script hash recorded under `WORK/artifacts/RETENTION-PLUGIN-VECTOR/`.
7. **Self-adversarial pass (protocol G):** ties and duplicates; singleton and
   empty cells; \(K\le d\) (singular \(I_Z\)); numerically singular \(V\)
   (the library projects, the theorem excludes); atomic laws; heavy tails
   (only \(E\|S\|^2<\infty\)); estimated scores enter only through the label
   map; the \(D\)/\(D_s\) distinction (this packet is full-\(D\) only).

## Required deliverables

- `KNOWN_RESULTS/10-oracle.md` section **O7** in the O6 format (normalised
  target, identity, CLT, variance, Wald interval and its unsupported cases,
  what it measures, protocol-G pass, measured table, verdict).
- Claim nodes `RETENTION-PLUGIN-CLT-FROZEN-VECTOR` (status `bridge` if
  proved, with `assumptions` fully explicit and `dependencies` on the O6 node,
  `FI-QUANT-IDENTITY`, `FI-RANK-CEILING`, `INFO-D-EFFICIENCY`) and a measured
  companion; patch `OPEN-RETENTION-UNCERTAINTY` to name the remainder.
- Instrument `py/retention_plugin_vector.py` (exact `fractions.Fraction`
  identities in \(d=2,3\); closed-form or quadrature references; coverage with
  recorded seeds); ledger rows `N-VECTOR-RETENTION-*` in `NUMERICAL_EVIDENCE.md`;
  a CI pin in `tests/test_research_claims.py` (influence function against
  Gateaux finite differences in \(d=2\), and the determinant identity against
  `information_report`).
- Literature triangulation under `LITERATURE/audits/RETENTION-PLUGIN-CLT-FROZEN-VECTOR-<date>.md`:
  matrix delta method for \(\log\det\) (Anderson 2003 §3/§7; Magnus &
  Neudecker), asymptotics of determinant ratios / Wilks' lambda under
  non-normality, influence functions of multivariate effect sizes; keys
  registered with `**Key:**` lines in `LITERATURE/topics/08-plug-in-asymptotics.md`.
- `manuscripts/README.md` note; packet moved to `WORK/completed/` with an
  Outcome section; `reindex` and `validate` clean; the research-claims tests
  green.

## Stop conditions

1. **Proved:** the vector CLT, the influence function, the consistent
   variance and the Wald statement hold under explicit (A1)–(A4), with the
   \(d=1\) reduction to O6 checked exactly and coverage replicating.
2. **Reduced:** a named missing step (most likely the \(\sigma^2=0\)
   characterisation or the singular-\(I_Z\) boundary); record what is proved
   and open the gap as its own node.
3. **Refuted:** an exact counterexample to the identity or the influence
   function, serialised in `COUNTEREXAMPLES/` and pinned.

Do not close on coverage alone; the verdict is about the derivation.

## Next dependency-blocking question

Rules **refitted on the evaluation sample** (the genuine OP27): the
evaluation sample enters the cell boundaries, the pairs \((S_i,Z_i)\) are no
longer iid, and the hard-assignment non-smoothness appears. First target: the
population D-exchange/Voronoi stationary rule of `D-POP-VORONOI` with an
empirical-process argument under a margin condition, or an exact
counterexample showing the plug-in is not \(\sqrt n\)-normal without one.
