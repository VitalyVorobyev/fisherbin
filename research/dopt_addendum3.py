#!/usr/bin/env python3
"""Addendum 3: deeper D_s and E-optimality investigation.

E12: quantitative approximate efficient-Voronoi bound at D_s-exchange-stable
     states:  s_aa - s_bb <= w_i * q_aa * (1/W_a + 1/W_b)   (Prop 17)
     plus the intermediate chain alpha*s_aa - beta*s_bb <= alpha*beta*(g2-g2l)
     and the Gram monotonicity g2l <= g2.
E13: efficient-score domination (Thm 18):
     (i)  matrix inequality  Schur_psi(I_bin) <= BetweenScatter(shat | bins)
     (ii) optimization: DP-exact 1-d binning of the efficient score as an
          upper bound + initializer for exact F_s exchange (d_psi = 1)
     (iii) same with d_psi = 2 via 2-d D exchange on shat
E14: exact rational (Fraction-arithmetic) verification of the D_s
     counterexample to the Theorem-6 analog.
E15: E-optimality falsification: subgradient-Voronoi rule vs exact
     lambda_min change.
"""
import numpy as np, math, time
from fractions import Fraction
from dopt_experiments import (bin_stats, info_matrix, logdet, F_labels,
                              scale_of, make_instance, random_labels, exchange)

# ----------------------------------------------------------------------
# generic objective + recompute-based exchange (exactly monotone by constr.)
# ----------------------------------------------------------------------
def F_gen(S, w, lab, K, kind, dpsi, eps):
    W, m = bin_stats(S, w, lab, K)
    d = S.shape[1]
    I = info_matrix(W, m, eps)
    if kind == 'D':
        return logdet(I)
    if kind == 'Ds':
        Ill = I[dpsi:, dpsi:]
        return logdet(I) - logdet(Ill)
    if kind == 'E':
        return float(np.linalg.eigvalsh(I)[0])
    raise ValueError(kind)

def exchange_gen(S, w, lab, K, kind, dpsi, eps, rng, max_sweeps=200,
                 min_gain=1e-10):
    lab = lab.copy()
    N = S.shape[0]
    F = F_gen(S, w, lab, K, kind, dpsi, eps)
    for sweep in range(max_sweeps):
        improved = False
        for i in rng.permutation(N):
            a = lab[i]
            if np.sum(w[lab == a]) - w[i] <= 1e-14:
                continue
            best, bestb = min_gain, -1
            for b in range(K):
                if b == a:
                    continue
                lab[i] = b
                Fn = F_gen(S, w, lab, K, kind, dpsi, eps)
                lab[i] = a
                if Fn - F > best:
                    best, bestb = Fn - F, b
            if bestb >= 0:
                lab[i] = bestb
                F += best
                improved = True
        if not improved:
            break
    return lab, F_gen(S, w, lab, K, kind, dpsi, eps)

# ----------------------------------------------------------------------
# E12: approximate efficient-Voronoi bound at D_s-stable states
# ----------------------------------------------------------------------
def e12(seed=120):
    rng = np.random.default_rng(seed)
    print("== E12: Prop 17 bound at D_s-exchange-stable states ==")
    d, dpsi, K = 3, 1, 4
    print(f"{'N':>4} {'states':>7} {'moves':>7} {'viol>0':>7} "
          f"{'max viol/q_aa':>14} {'max w*L':>10} {'max ratio':>10}")
    all_ok = True
    gram_ok = True
    chain_ok = True
    for N in [8, 16, 32, 64]:
        n_states = n_moves = n_viol = 0
        max_rel = 0.0
        max_wL = 0.0
        max_ratio = 0.0
        for t in range(12):
            S, w = make_instance(rng, N=N, d=d, ncomp=3)
            eps = 1e-10 * scale_of(S, w)
            for r in range(3):
                lab, Fs = exchange_gen(S, w, random_labels(rng, N, K), K,
                                       'Ds', dpsi, eps, rng)
                W, m = bin_stats(S, w, lab, K)
                I = info_matrix(W, m)
                if not np.isfinite(logdet(I)) or np.linalg.cond(I) > 1e8:
                    continue
                n_states += 1
                Iinv = np.linalg.inv(I)
                Ill = I[dpsi:, dpsi:]
                Illinv = np.linalg.inv(Ill)
                mus = m / W[:, None]
                for i in range(N):
                    a = lab[i]
                    if W[a] - w[i] <= 1e-14:
                        continue
                    ua = S[i] - mus[a]
                    alpha = w[i] * W[a] / (W[a] - w[i])
                    qaa = ua @ Iinv @ ua
                    saa = qaa - ua[dpsi:] @ Illinv @ ua[dpsi:]
                    for b in range(K):
                        if b == a:
                            continue
                        ub = S[i] - mus[b]
                        beta = w[i] * W[b] / (W[b] + w[i])
                        qbb = ub @ Iinv @ ub
                        qab = ua @ Iinv @ ub
                        sbb = qbb - ub[dpsi:] @ Illinv @ ub[dpsi:]
                        # admissibility: move keeps I nonsingular
                        arg = (1 + alpha * qaa) * (1 - beta * qbb) \
                              + alpha * beta * qab ** 2
                        if arg <= 1e-12:
                            continue
                        n_moves += 1
                        g2 = qaa * qbb - qab ** 2
                        qab_l = ua[dpsi:] @ Illinv @ ub[dpsi:]
                        g2l = (ua[dpsi:] @ Illinv @ ua[dpsi:]) \
                              * (ub[dpsi:] @ Illinv @ ub[dpsi:]) - qab_l ** 2
                        if g2l > g2 + 1e-7 * (1 + abs(g2)):
                            gram_ok = False
                        # stability chain (equivalent to gain<=0)
                        lhs = alpha * saa - beta * sbb
                        if lhs > alpha * beta * (g2 - g2l) + 1e-6 * (1 + abs(lhs)):
                            chain_ok = False
                        margin = saa - sbb
                        if margin > 1e-10:
                            n_viol += 1
                            L = 1.0 / W[a] + 1.0 / W[b]
                            bound = w[i] * qaa * L
                            rel = margin / max(qaa, 1e-300)
                            max_rel = max(max_rel, rel)
                            max_wL = max(max_wL, w[i] * L)
                            r_ = margin / max(bound, 1e-300)
                            max_ratio = max(max_ratio, r_)
                            if margin > bound * (1 + 1e-6) + 1e-9:
                                all_ok = False
        print(f"{N:>4} {n_states:>7} {n_moves:>7} {n_viol:>7} "
              f"{max_rel:>14.4g} {max_wL:>10.4g} {max_ratio:>10.3f}")
    print("Gram monotonicity g2_lambda <= g2:       "
          + ("PASS" if gram_ok else "FAIL"))
    print("stability chain a*s_aa-b*s_bb <= ab(g2-g2l): "
          + ("PASS" if chain_ok else "FAIL"))
    print("Prop 17 bound margin <= w*q_aa*L:        "
          + ("PASS" if all_ok else "FAIL"))

# ----------------------------------------------------------------------
# E13: efficient-score domination
# ----------------------------------------------------------------------
def efficient_scores(S, w, dpsi):
    Sig = (w[:, None] * S).T @ S
    B = Sig[:dpsi, dpsi:] @ np.linalg.inv(Sig[dpsi:, dpsi:])
    return S[:, :dpsi] - S[:, dpsi:] @ B.T

def schur(I, dpsi):
    A = I[:dpsi, :dpsi]; Bm = I[:dpsi, dpsi:]; C = I[dpsi:, dpsi:]
    return A - Bm @ np.linalg.solve(C, Bm.T)

def between(Sh, w, lab, K):
    W, m = bin_stats(Sh, w, lab, K)
    return info_matrix(W, m)

def dp_1d_kmeans(x, w, K):
    """Exact 1-d weighted K-means (min within-SSE) by DP; returns labels."""
    order = np.argsort(x)
    xs, ws = x[order], w[order]
    N = len(x)
    cw = np.concatenate([[0], np.cumsum(ws)])
    cwx = np.concatenate([[0], np.cumsum(ws * xs)])
    cwx2 = np.concatenate([[0], np.cumsum(ws * xs * xs)])
    def seg(i, j):        # within-SSE of xs[i:j]
        Wt = cw[j] - cw[i]
        if Wt <= 0: return 0.0
        m = (cwx[j] - cwx[i]) / Wt
        return (cwx2[j] - cwx2[i]) - Wt * m * m
    INF = float('inf')
    dp = np.full((K + 1, N + 1), INF)
    arg = np.zeros((K + 1, N + 1), dtype=int)
    dp[0, 0] = 0.0
    for k in range(1, K + 1):
        for j in range(k, N + 1):
            for i in range(k - 1, j):
                v = dp[k - 1, i] + seg(i, j)
                if v < dp[k, j]:
                    dp[k, j] = v; arg[k, j] = i
    lab_sorted = np.zeros(N, dtype=int)
    j = N
    for k in range(K, 0, -1):
        i = arg[k, j]
        lab_sorted[i:j] = k - 1
        j = i
    lab = np.zeros(N, dtype=int)
    lab[order] = lab_sorted
    return lab

def e13(seed=130):
    rng = np.random.default_rng(seed)
    print("\n== E13: efficient-score domination (Thm 18) ==")
    # (i) matrix inequality on random partitions
    bad = 0; tested = 0
    for t in range(300):
        d = int(rng.choice([3, 4]))
        dpsi = int(rng.choice([1, 2]))
        K = d + 1
        N = int(rng.choice([12, 20, 40]))
        S, w = make_instance(rng, N=N, d=d)
        lab = random_labels(rng, N, K)
        W, m = bin_stats(S, w, lab, K)
        I = info_matrix(W, m)
        if not np.isfinite(logdet(I)):
            continue
        tested += 1
        Sh = efficient_scores(S, w, dpsi)
        Dlt = between(Sh, w, lab, K) - schur(I, dpsi)
        if np.linalg.eigvalsh(Dlt)[0] < -1e-8 * (1 + np.trace(I)):
            bad += 1
    print(f"(i) Schur(I_bin) <= Between(shat|bins): "
          f"{tested - bad}/{tested} PSD  ({'PASS' if bad == 0 else 'FAIL'})")

    # (ii) d_psi = 1: DP-exact projected bound + polish
    print("(ii) d=3, d_psi=1, K=4, N=60: DP-projected bound vs exact F_s")
    print(f"{'inst':>4} {'bound':>9} {'F_s proj':>9} {'F_s direct':>10} "
          f"{'F_s polish':>10} {'gap':>8}")
    for t in range(8):
        d, dpsi, K, N = 3, 1, 4, 60
        S, w = make_instance(rng, N=N, d=d, ncomp=3)
        eps = 1e-10 * scale_of(S, w)
        Sh = efficient_scores(S, w, dpsi)
        lab_p = dp_1d_kmeans(Sh[:, 0], w, K)
        bound = math.log(float(between(Sh, w, lab_p, K)[0, 0]))
        Fs_proj = F_gen(S, w, lab_p, K, 'Ds', dpsi, 0.0)
        best_dir = -np.inf
        for r in range(6):
            _, Fd = exchange_gen(S, w, random_labels(rng, N, K), K, 'Ds',
                                 dpsi, eps, rng)
            best_dir = max(best_dir, Fd)
        lab_pol, Fs_pol = exchange_gen(S, w, lab_p, K, 'Ds', dpsi, eps, rng)
        best = max(best_dir, Fs_pol)
        print(f"{t:>4} {bound:>9.4f} {Fs_proj:>9.4f} {best_dir:>10.4f} "
              f"{Fs_pol:>10.4f} {bound - best:>8.4f}")

    # (iii) d_psi = 2 via 2-d D exchange on shat
    print("(iii) d=4, d_psi=2, K=5, N=80")
    print(f"{'inst':>4} {'bound(2d exch)':>14} {'F_s direct':>10} "
          f"{'F_s polish':>10} {'gap':>8}")
    for t in range(4):
        d, dpsi, K, N = 4, 2, 5, 80
        S, w = make_instance(rng, N=N, d=d, ncomp=3)
        eps = 1e-10 * scale_of(S, w)
        Sh = efficient_scores(S, w, dpsi)
        eps2 = 1e-10 * scale_of(Sh, w)
        best_b, lab_b = -np.inf, None
        for r in range(6):
            labr, _, _, _, _ = exchange(Sh, w, random_labels(rng, N, K), K,
                                        eps2, rng)
            Fb = logdet(between(Sh, w, labr, K))
            if Fb > best_b:
                best_b, lab_b = Fb, labr
        best_dir = -np.inf
        for r in range(6):
            _, Fd = exchange_gen(S, w, random_labels(rng, N, K), K, 'Ds',
                                 dpsi, eps, rng)
            best_dir = max(best_dir, Fd)
        lab_pol, Fs_pol = exchange_gen(S, w, lab_b, K, 'Ds', dpsi, eps, rng)
        best = max(best_dir, Fs_pol)
        print(f"{t:>4} {best_b:>14.4f} {best_dir:>10.4f} {Fs_pol:>10.4f} "
              f"{best_b - best:>8.4f}")

# ----------------------------------------------------------------------
# E14: exact rational verification of the D_s counterexample
# ----------------------------------------------------------------------
def e14():
    print("\n== E14: exact rational D_s counterexample (Fraction arithmetic) ==")
    Sr = [(-463, -17), (32, 53), (-363, -1292), (211, -1357),
          (129, 501), (544, 594), (-24, 775), (-66, 743)]
    S = [[Fraction(a, 1000), Fraction(b, 1000)] for a, b in Sr]
    lab = [0, 1, 2, 1, 2, 1, 1, 2]
    K, N = 3, 8
    wi = Fraction(1, 8)
    # center exactly
    mean = [sum(p[j] for p in S) / N for j in range(2)]
    S = [[p[0] - mean[0], p[1] - mean[1]] for p in S]
    W = [Fraction(0)] * K
    m = [[Fraction(0), Fraction(0)] for _ in range(K)]
    for i in range(N):
        W[lab[i]] += wi
        m[lab[i]][0] += wi * S[i][0]
        m[lab[i]][1] += wi * S[i][1]
    I = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]
    for b in range(K):
        for r in range(2):
            for c in range(2):
                I[r][c] += m[b][r] * m[b][c] / W[b]
    detI = I[0][0] * I[1][1] - I[0][1] * I[1][0]
    assert detI > 0, "I singular"
    Iinv = [[I[1][1] / detI, -I[0][1] / detI],
            [-I[1][0] / detI, I[0][0] / detI]]
    Ill = I[1][1]                       # lambda = coordinate 2
    i, a, b = 5, 1, 0
    mu_a = [m[a][0] / W[a], m[a][1] / W[a]]
    mu_b = [m[b][0] / W[b], m[b][1] / W[b]]
    ua = [S[i][0] - mu_a[0], S[i][1] - mu_a[1]]
    ub = [S[i][0] - mu_b[0], S[i][1] - mu_b[1]]
    alpha = wi * W[a] / (W[a] - wi)
    beta = wi * W[b] / (W[b] + wi)
    def q(u, v):
        return sum(u[r] * Iinv[r][c] * v[c] for r in range(2) for c in range(2))
    qaa, qbb, qab = q(ua, ua), q(ub, ub), q(ua, ub)
    saa = qaa - ua[1] * ua[1] / Ill
    sbb = qbb - ub[1] * ub[1] / Ill
    margin = saa - sbb
    Rfull = (1 + alpha * qaa) * (1 - beta * qbb) + alpha * beta * qab * qab
    Rl = (1 + alpha * ua[1] * ua[1] / Ill) * (1 - beta * ub[1] * ub[1] / Ill) \
         + alpha * beta * (ua[1] * ub[1] / Ill) ** 2
    print(f"G_s-Voronoi margin s_aa - s_bb = {float(margin):.6f}  "
          f"(exact rational, > 0: {margin > 0})")
    print(f"determinant ratios: R_full = {float(Rfull):.9f}, "
          f"R_lambda = {float(Rl):.9f}")
    print(f"exact gain sign: R_full < R_lambda  ->  "
          f"{Rfull < Rl}  (Delta F_s = log(R_full/R_lambda) = "
          f"{math.log(float(Rfull / Rl)):.6f})")
    ok = (margin > 0) and (Rfull < Rl) and (Rfull > 0) and (Rl > 0)
    print("EXACT counterexample verified in rational arithmetic: "
          + ("PASS" if ok else "FAIL"))

# ----------------------------------------------------------------------
# E15: E-optimality falsification
# ----------------------------------------------------------------------
def e15(n_trials=15000, seed=150):
    rng = np.random.default_rng(seed)
    print("\n== E15: E-optimality: subgradient-Voronoi rule vs exact move ==")
    tested = viol_neg = sat_pos = 0
    ex = None
    for t in range(n_trials):
        d = int(rng.choice([2, 3]))
        K = d + 1
        N = int(rng.choice([6, 8, 10]))
        S, w = make_instance(rng, N=N, d=d)
        if t % 2 == 1:
            w = rng.uniform(0.5, 4.0, N); w /= w.sum()
            S = S - (w[:, None] * S).sum(0)
        lab = random_labels(rng, N, K)
        W, m = bin_stats(S, w, lab, K)
        I = info_matrix(W, m)
        ev, V = np.linalg.eigh(I)
        if ev[0] <= 1e-12 or ev[1] - ev[0] < 1e-6 * max(ev[-1], 1e-12):
            continue                       # need simple smallest eigenvalue
        v = V[:, 0]
        i = rng.integers(N); b = rng.integers(K)
        a = lab[i]
        if a == b or W[a] - w[i] <= 1e-12:
            continue
        mus = m / W[:, None]
        ua, ub = S[i] - mus[a], S[i] - mus[b]
        alpha = w[i] * W[a] / (W[a] - w[i])
        beta = w[i] * W[b] / (W[b] + w[i])
        fo = alpha * (v @ ua) ** 2 - beta * (v @ ub) ** 2
        lab2 = lab.copy(); lab2[i] = b
        W2, m2 = bin_stats(S, w, lab2, K)
        exact = float(np.linalg.eigvalsh(info_matrix(W2, m2))[0] - ev[0])
        tested += 1
        if fo > 1e-9 and exact < -1e-9:
            viol_neg += 1
            if ex is None or fo > ex[0]:
                ex = (fo, exact, N, d)
        if fo < -1e-9 and exact > 1e-9:
            sat_pos += 1
    print(f"tested {tested}; subgradient-rule-improving but exact "
          f"lambda_min decrease: {viol_neg}; rule-negative but exact "
          f"increase: {sat_pos}")
    if ex:
        print(f"  example: fo={ex[0]:.4f}, exact={ex[1]:.6f} (N={ex[2]}, d={ex[3]})")
    print("=> Theorem-6 analog for E-optimality: "
          + ("FALSIFIED" if viol_neg > 0 else "no counterexample found"))

if __name__ == "__main__":
    t0 = time.time()
    e12(); e13(); e14(); e15()
    print(f"\ntotal {time.time() - t0:.1f}s")
