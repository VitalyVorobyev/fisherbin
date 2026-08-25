#!/usr/bin/env python3
"""Addendum 2: E9 branch-and-bound exact global solver (refinement bound),
E10 tightness of the randomized/soft relaxation, E11 Theorem-6 analogs for
A-optimality and profiled D_s-optimality."""
import numpy as np, math, time, sys
from dopt_experiments import (bin_stats, info_matrix, logdet, F_labels,
                              scale_of, make_instance, random_labels,
                              whitened_kmeans, exchange, exhaustive_best)

# ----------------------------------------------------------------------
# E9: branch and bound with the refinement (singleton-completion) bound
#   Any completion of a partial assignment coarsens {partial bins} ∪
#   {singletons of unassigned points}  =>  I_completion ⪯ I_partial + R_t
#   => logdet(I_partial + R_t) is a valid, monotonically tightening UB.
# ----------------------------------------------------------------------
def branch_and_bound(S, w, K, F_inc=-np.inf, max_nodes=3_000_000, tol=1e-9):
    N, d = S.shape
    Sig = (w[:, None] * S).T @ S
    Y = np.linalg.solve(np.linalg.cholesky(Sig), S.T).T
    order = np.argsort(-np.einsum('nd,nd->n', Y, Y))   # leverage-first
    S, w = S[order], w[order]
    suffix = np.zeros((N + 1, d, d))
    for t in range(N - 1, -1, -1):
        suffix[t] = suffix[t + 1] + w[t] * np.outer(S[t], S[t])
    Wb = np.zeros(K)
    mb = np.zeros((K, d))
    lab = np.zeros(N, dtype=int)
    best = {'F': F_inc, 'lab': None, 'nodes': 0, 'capped': False}

    def Ipart():
        I = np.zeros((d, d))
        for b in range(K):
            if Wb[b] > 0:
                I += np.outer(mb[b], mb[b]) / Wb[b]
        return I

    def ub_with(extra):
        sgn, ld = np.linalg.slogdet(Ipart() + extra)
        return ld if sgn > 0 else -np.inf

    sys.setrecursionlimit(10000)

    def rec(t, nused):
        best['nodes'] += 1
        if best['capped'] or best['nodes'] > max_nodes:
            best['capped'] = True
            return
        if t == N:
            if nused == K:
                sgn, ld = np.linalg.slogdet(Ipart())
                F = ld if sgn > 0 else -np.inf
                if F > best['F']:
                    best['F'], best['lab'] = F, lab.copy()
            return
        cands = []
        for b in range(min(nused + 1, K)):          # bin-symmetry breaking
            nu = nused + (1 if b == nused else 0)
            if K - nu > N - t - 1:                  # can't fill empty bins
                continue
            Wb[b] += w[t]; mb[b] += w[t] * S[t]
            cb = ub_with(suffix[t + 1])
            Wb[b] -= w[t]; mb[b] -= w[t] * S[t]
            if cb > best['F'] + tol:
                cands.append((cb, b, nu))
        cands.sort(reverse=True)
        for cb, b, nu in cands:
            if cb <= best['F'] + tol:               # re-check: incumbent moved
                continue
            Wb[b] += w[t]; mb[b] += w[t] * S[t]; lab[t] = b
            rec(t + 1, nu)
            Wb[b] -= w[t]; mb[b] -= w[t] * S[t]
        return

    rec(0, 0)
    lab_out = None
    if best['lab'] is not None:
        lab_out = np.zeros(N, dtype=int)
        lab_out[order] = best['lab']
    return best['F'], lab_out, best['nodes'], best['capped']

def e9(seed=90):
    rng = np.random.default_rng(seed)
    print("== E9: branch-and-bound exact global optimum ==")
    # correctness vs exhaustive
    ok = True
    for t in range(5):
        S, w = make_instance(rng, N=12, d=2)
        Fstar, _, _, _, _ = exhaustive_best(S, w, 3, also_trace=False)
        eps = 1e-9 * scale_of(S, w)
        lab0, _, _, _, _ = exchange(S, w, random_labels(rng, 12, 3), 3, eps, rng)
        Finc = F_labels(S, w, lab0, 3)
        Fbb, labbb, nodes, capped = branch_and_bound(S, w, 3, F_inc=Finc - 1e-6)
        if abs(Fbb - Fstar) > 1e-7:
            ok = False
    print(f"correctness vs exhaustive (5 instances, N=12): "
          + ("PASS" if ok else "FAIL"))
    # scaling
    for N in [15, 18, 21, 24]:
        S, w = make_instance(rng, N=N, d=2, ncomp=3)
        eps = 1e-9 * scale_of(S, w)
        t0 = time.time()
        Finc, labinc = -np.inf, None
        for r in range(8):
            lab, F, _, _, _ = exchange(S, w, random_labels(rng, N, 3), 3, eps, rng)
            F = F_labels(S, w, lab, 3)
            if F > Finc:
                Finc, labinc = F, lab
        t_inc = time.time() - t0
        t0 = time.time()
        Fbb, labbb, nodes, capped = branch_and_bound(S, w, 3, F_inc=Finc - 1e-9)
        t_bb = time.time() - t0
        total = 3 ** N
        status = "CAPPED" if capped else "proved"
        gap = Fbb - Finc
        print(f"N={N}: incumbent(8x exch) {Finc:.6f} ({t_inc:.1f}s) | "
              f"B&B {status} F*={Fbb:.6f} (exch gap {gap:.2e}) "
              f"nodes={nodes:,} of 3^N={total:,} ({t_bb:.1f}s)")

# ----------------------------------------------------------------------
# E10: does the randomized (soft) relaxation beat the best hard partition?
# ----------------------------------------------------------------------
def project_simplex_rows(P):
    K = P.shape[1]
    U = np.sort(P, axis=1)[:, ::-1]
    css = np.cumsum(U, axis=1) - 1.0
    ind = np.arange(1, K + 1)
    cond = U - css / ind > 0
    rho = K - 1 - np.argmax(cond[:, ::-1], axis=1)
    theta = css[np.arange(len(P)), rho] / (rho + 1.0)
    return np.maximum(P - theta[:, None], 0.0)

def soft_F(S, w, p, eps):
    Wb = p.T @ w
    Mb = (p * w[:, None]).T @ S
    d = S.shape[1]
    I = eps * np.eye(d)
    for b in range(p.shape[1]):
        if Wb[b] > 1e-300:
            I += np.outer(Mb[b], Mb[b]) / Wb[b]
    return logdet(I), I, Wb, Mb

def soft_ascent(S, w, p0, eps, iters=1500):
    p = p0.copy()
    f, I, Wb, Mb = soft_F(S, w, p, eps)
    lr = 0.2
    for it in range(iters):
        G = np.linalg.inv(I)
        mus = Mb / np.maximum(Wb[:, None], 1e-300)
        sGs = np.einsum('nd,de,ne->n', S, G, S)
        diff = S[:, None, :] - mus[None, :, :]
        q = np.einsum('nbd,de,nbe->nb', diff, G, diff)
        grad = w[:, None] * (sGs[:, None] - q)
        ok = False
        for _ in range(30):
            pn = project_simplex_rows(p + lr * grad)
            fn, In, Wn, Mn = soft_F(S, w, pn, eps)
            if fn > f + 1e-13:
                p, f, I, Wb, Mb = pn, fn, In, Wn, Mn
                lr *= 1.2
                ok = True
                break
            lr *= 0.5
        if not ok:
            break
    return f, p

def e10(n_instances=12, seed=100):
    rng = np.random.default_rng(seed)
    print("\n== E10: randomized relaxation vs best hard partition ==")
    K = 3
    max_excess = -np.inf
    min_kkt_margin = np.inf
    for t in range(n_instances):
        N = int(rng.choice([8, 10]))
        S, w = make_instance(rng, N=N, d=2)
        eps = 1e-10 * scale_of(S, w)
        Fstar, labstar, _, _, _ = exhaustive_best(S, w, K, also_trace=False)
        # KKT margin at the hard optimum (strict-Voronoi check via gradient)
        p_hard = np.zeros((N, K)); p_hard[np.arange(N), labstar] = 1.0
        f0, I, Wb, Mb = soft_F(S, w, p_hard, eps)
        G = np.linalg.inv(I)
        mus = Mb / Wb[:, None]
        diff = S[:, None, :] - mus[None, :, :]
        q = np.einsum('nbd,de,nbe->nb', diff, G, diff)
        for i in range(N):
            a = labstar[i]
            others = [q[i, b] - q[i, a] for b in range(K) if b != a]
            min_kkt_margin = min(min_kkt_margin, min(others))
        # multistart soft ascent
        best_soft = -np.inf
        starts = []
        pj = p_hard * 0.9 + 0.1 / K
        starts.append(pj)
        starts.append(np.full((N, K), 1.0 / K) + 0.01 * rng.random((N, K)))
        for _ in range(3):
            starts.append(rng.dirichlet(np.ones(K), size=N))
        for p0 in starts:
            f, p = soft_ascent(S, w, project_simplex_rows(p0), eps)
            best_soft = max(best_soft, f)
        max_excess = max(max_excess, best_soft - Fstar)
    print(f"max over instances of (best soft F - best hard F): {max_excess:.3e}")
    print(f"min gradient/KKT margin at hard optima (should be > 0 by Thm 6): "
          f"{min_kkt_margin:.4f}")

# ----------------------------------------------------------------------
# E11: Theorem-6 analogs for A-optimality and profiled D_s
# ----------------------------------------------------------------------
def move_context(S, w, lab, K, i, b):
    W, m = bin_stats(S, w, lab, K)
    a = lab[i]
    if W[a] - w[i] <= 1e-12 or a == b:
        return None
    mus = m / W[:, None]
    ua, ub = S[i] - mus[a], S[i] - mus[b]
    alpha = w[i] * W[a] / (W[a] - w[i])
    beta = w[i] * W[b] / (W[b] + w[i])
    P = np.stack([ua, ub], axis=1)
    D = np.diag([alpha, -beta])
    return W, m, mus, a, P, D, ua, ub, alpha, beta

def e11(n_trials=15000, seed=110):
    rng = np.random.default_rng(seed)
    print("\n== E11: does 'stability => Voronoi' extend to A and D_s? ==")
    # first: verify exact-gain formulas vs brute force
    okA = okS = True
    for t in range(150):
        S, w = make_instance(rng, N=12, d=3)
        w = rng.uniform(0.5, 2.0, 12); w /= w.sum()
        S = S - (w[:, None] * S).sum(0)
        lab = random_labels(rng, 12, 4)
        i = rng.integers(12); b = rng.integers(4)
        ctx = move_context(S, w, lab, 4, i, b)
        if ctx is None: continue
        W, m, mus, a, P, D, ua, ub, alpha, beta = ctx
        I = info_matrix(W, m)
        if not np.isfinite(logdet(I)): continue
        Iinv = np.linalg.inv(I)
        lab2 = lab.copy(); lab2[i] = b
        W2, m2 = bin_stats(S, w, lab2, 4)
        I2 = info_matrix(W2, m2)
        Q = P.T @ Iinv @ P
        arg = np.linalg.det(np.eye(2) + D @ Q)
        if arg <= 1e-12 or not np.isfinite(logdet(I2)): continue
        # A-criterion gain
        C = np.linalg.inv(D) + Q
        Z = Iinv @ P
        gA = np.trace(np.linalg.solve(C, Z.T @ Z))
        gA_true = -np.trace(np.linalg.inv(I2)) + np.trace(Iinv)
        if abs(gA - gA_true) > 1e-7 * (1 + abs(gA_true)): okA = False
        # D_s gain (psi = first coord(s), lambda = rest)
        dl = [1, 2]
        Ill = I[np.ix_(dl, dl)]
        Pl = P[dl, :]
        argl = np.linalg.det(np.eye(2) + D @ (Pl.T @ np.linalg.inv(Ill) @ Pl))
        gS = math.log(arg) - math.log(argl)
        Ill2 = I2[np.ix_(dl, dl)]
        gS_true = (logdet(I2) - logdet(Ill2)) - (logdet(I) - logdet(Ill))
        if abs(gS - gS_true) > 1e-7 * (1 + abs(gS_true)): okS = False
    print("exact-gain formulas: A " + ("PASS" if okA else "FAIL")
          + ", D_s " + ("PASS" if okS else "FAIL"))

    # falsification: fo>0 (criterion-Voronoi-violating) but exact gain < 0
    counts = {'A': [0, 0, 0], 'Ds': [0, 0, 0]}   # tested, viol&neg, sat&pos
    examples = {}
    for t in range(n_trials):
        d = int(rng.choice([2, 3]))
        K = d + 1
        N = int(rng.choice([6, 8, 10]))
        S, w = make_instance(rng, N=N, d=d)
        if t % 2 == 1:
            w = rng.uniform(0.5, 4.0, N); w /= w.sum()
            S = S - (w[:, None] * S).sum(0)
        lab = random_labels(rng, N, K)
        i = rng.integers(N); b = rng.integers(K)
        ctx = move_context(S, w, lab, K, i, b)
        if ctx is None: continue
        W, m, mus, a, P, D, ua, ub, alpha, beta = ctx
        I = info_matrix(W, m)
        if not np.isfinite(logdet(I)) or np.linalg.cond(I) > 1e9: continue
        Iinv = np.linalg.inv(I)
        Q = P.T @ Iinv @ P
        arg = np.linalg.det(np.eye(2) + D @ Q)
        lab2 = lab.copy(); lab2[i] = b
        W2, m2 = bin_stats(S, w, lab2, K)
        I2 = info_matrix(W2, m2)
        if arg <= 1e-12 or not np.isfinite(logdet(I2)): continue
        # ---- A
        GA = Iinv @ Iinv
        foA = ua @ GA @ ua - ub @ GA @ ub
        gA_true = -np.trace(np.linalg.inv(I2)) + np.trace(Iinv)
        counts['A'][0] += 1
        if foA > 1e-9 and gA_true < -1e-9:
            counts['A'][1] += 1
            if 'A' not in examples or foA > examples['A'][0]:
                examples['A'] = (foA, gA_true, S.copy(), w.copy(), lab.copy(), i, b)
        if foA < -1e-9 and gA_true > 1e-9:
            counts['A'][2] += 1
        # ---- D_s (psi = coord 0, lambda = rest)
        dl = list(range(1, d))
        El = np.zeros((d, d - 1)); El[dl, range(d - 1)] = 1.0
        Ill = I[np.ix_(dl, dl)]
        GS = Iinv - El @ np.linalg.inv(Ill) @ El.T
        foS = ua @ GS @ ua - ub @ GS @ ub
        Ill2 = I2[np.ix_(dl, dl)]
        gS_true = (logdet(I2) - logdet(Ill2)) - (logdet(I) - logdet(Ill))
        counts['Ds'][0] += 1
        if foS > 1e-9 and gS_true < -1e-9:
            counts['Ds'][1] += 1
            if 'Ds' not in examples or foS > examples['Ds'][0]:
                examples['Ds'] = (foS, gS_true, S.copy(), w.copy(), lab.copy(), i, b)
        if foS < -1e-9 and gS_true > 1e-9:
            counts['Ds'][2] += 1
    for k in ['A', 'Ds']:
        tt, vn, sp = counts[k]
        print(f"{k}: tested {tt}; Voronoi-violating & exact<0: {vn}; "
              f"Voronoi-satisfied & exact>0: {sp}")
        if k in examples:
            fo, g, S, w, lab, i, b = examples[k]
            print(f"  counterexample to Thm-6 analog for {k}: fo={fo:.4f}, "
                  f"exact gain={g:.6f}, N={len(w)}, d={S.shape[1]}, "
                  f"i={i} {lab[i]}->{b}, w_i={w[i]:.3f}")
            print("  S =", np.round(S, 3).tolist())
            print("  w =", np.round(w, 3).tolist(), " labels =", lab.tolist())

if __name__ == "__main__":
    t0 = time.time()
    e9(); e10(); e11()
    print(f"\ntotal {time.time()-t0:.1f}s")
