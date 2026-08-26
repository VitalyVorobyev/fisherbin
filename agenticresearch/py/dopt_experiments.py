#!/usr/bin/env python3
"""
Numerical falsification suite for D-optimal hard quantization of score space.

Implements:
  - exact bin statistics / Fisher information of a hard partition
  - Fisher-whitened weighted k-means (trace criterion)
  - soft-Voronoi (affine-logit softmax) gradient ascent of logdet
  - adaptive-Mahalanobis Lloyd iteration (batch, metric G = (I+eps)^{-1})
  - exact single-point exchange (Hartigan/Fedorov-style), provably monotone
  - exhaustive enumeration of all K-partitions for small N (ground truth)

Experiments:
  U*: unit tests of the algebra (rank-2 Delta I, determinant-lemma gain,
      first-variation limit, tie-move threshold)
  E1: search for monotonicity violations of adaptive-Mahalanobis Lloyd
  E2: exhaustive comparison of all methods against the global optimum;
      also trace-optimal vs D-optimal partition disagreement
  E3: Lloyd fixed points (Mahalanobis-Voronoi consistent) improved by exchange
  E4: exchange-stable partitions violating the Mahalanobis-Voronoi condition
"""
import numpy as np
import math

# ----------------------------------------------------------------------
# core statistics
# ----------------------------------------------------------------------

def bin_stats(S, w, labels, K):
    N, d = S.shape
    W = np.zeros(K)
    m = np.zeros((K, d))
    np.add.at(W, labels, w)
    np.add.at(m, labels, w[:, None] * S)
    return W, m

def info_matrix(W, m, eps=0.0):
    d = m.shape[1]
    I = np.zeros((d, d))
    for b in range(len(W)):
        if W[b] > 1e-300:
            I += np.outer(m[b], m[b]) / W[b]
    if eps:
        I = I + eps * np.eye(d)
    return I

def logdet(I):
    sign, ld = np.linalg.slogdet(I)
    return ld if sign > 0 else -np.inf

def F_labels(S, w, labels, K, eps=0.0):
    W, m = bin_stats(S, w, labels, K)
    return logdet(info_matrix(W, m, eps))

def scale_of(S, w):
    Sig = (w[:, None] * S).T @ S
    return np.trace(Sig) / S.shape[1]

# ----------------------------------------------------------------------
# instances
# ----------------------------------------------------------------------

def make_instance(rng, N=40, d=2, ncomp=None, spread=2.0, aniso=1.0):
    if ncomp is None:
        ncomp = rng.integers(2, 5)
    means = rng.normal(size=(ncomp, d)) * spread
    pts = []
    for i in range(N):
        c = rng.integers(ncomp)
        A = rng.normal(size=(d, d)) * 0.3
        x = means[c] + rng.normal(size=d) * np.array([1.0] + [aniso] * (d - 1)) * 0.5
        pts.append(x)
    S = np.array(pts)
    w = np.full(N, 1.0 / N)
    S = S - (w[:, None] * S).sum(0)          # enforce E[s]=0 empirically
    return S, w

def random_labels(rng, N, K):
    while True:
        lab = rng.integers(K, size=N)
        if len(np.unique(lab)) == K:
            return lab

# ----------------------------------------------------------------------
# whitened weighted k-means (trace criterion)
# ----------------------------------------------------------------------

def weighted_kmeans(Y, w, K, rng, iters=100):
    N, d = Y.shape
    # kmeans++ init
    idx = [rng.choice(N, p=w / w.sum())]
    for _ in range(K - 1):
        D2 = np.min(((Y[:, None, :] - Y[idx][None, :, :]) ** 2).sum(-1), axis=1)
        p = w * D2
        if p.sum() <= 0:
            idx.append(rng.integers(N))
        else:
            idx.append(rng.choice(N, p=p / p.sum()))
    C = Y[idx].copy()
    labels = np.zeros(N, dtype=int)
    for _ in range(iters):
        D2 = ((Y[:, None, :] - C[None, :, :]) ** 2).sum(-1)
        new = D2.argmin(1)
        # fix empties
        for b in range(K):
            if not np.any(new == b):
                j = np.argmax(D2[np.arange(N), new])
                new[j] = b
        if np.array_equal(new, labels):
            labels = new
            break
        labels = new
        for b in range(K):
            mask = labels == b
            C[b] = (w[mask, None] * Y[mask]).sum(0) / w[mask].sum()
    cost = 0.0
    for b in range(K):
        mask = labels == b
        cost += (w[mask] * ((Y[mask] - C[b]) ** 2).sum(-1)).sum()
    return labels, cost

def whitened_kmeans(S, w, K, rng, restarts=10):
    Sig = (w[:, None] * S).T @ S
    L = np.linalg.cholesky(Sig)
    Y = np.linalg.solve(L, S.T).T           # whitened scores
    best = None
    for _ in range(restarts):
        lab, cost = weighted_kmeans(Y, w, K, rng)
        if best is None or cost < best[1]:
            best = (lab, cost)
    return best[0]

# ----------------------------------------------------------------------
# adaptive-Mahalanobis Lloyd
# ----------------------------------------------------------------------

def adaptive_lloyd(S, w, labels, K, eps, max_iter=60):
    """Batch iteration: G=(I+eps)^{-1}; assign to Mahalanobis-nearest centroid;
    recompute. Returns final labels and the trajectory of *unregularized* and
    regularized logdet AFTER each state."""
    labels = labels.copy()
    N, d = S.shape
    traj_plain, traj_reg, states = [], [], []
    for it in range(max_iter):
        W, m = bin_stats(S, w, labels, K)
        I0 = info_matrix(W, m, 0.0)
        Ie = info_matrix(W, m, eps)
        traj_plain.append(logdet(I0))
        traj_reg.append(logdet(Ie))
        states.append(labels.copy())
        G = np.linalg.inv(Ie)
        mus = m / np.maximum(W[:, None], 1e-300)
        Lc = np.linalg.cholesky(G)
        X = S @ Lc
        M = mus @ Lc
        D2 = ((X[:, None, :] - M[None, :, :]) ** 2).sum(-1)
        new = D2.argmin(1)
        for b in range(K):                   # reseed empty bins
            if not np.any(new == b):
                j = np.argmax(D2[np.arange(N), new])
                new[j] = b
        if np.array_equal(new, labels):
            break
        labels = new
    return labels, traj_plain, traj_reg, states

# ----------------------------------------------------------------------
# exact single-point exchange (monotone)
# ----------------------------------------------------------------------

def exchange(S, w, labels, K, eps, rng, max_sweeps=500, min_gain=1e-11,
             paranoid=False):
    """Hartigan/Fedorov-style local search on F_eps = logdet(I_bin + eps I_d).
    Only exact strictly-positive-gain single-point moves are accepted.
    Moves that would empty a bin are forbidden (exactly-K partitions).
    Returns labels, final F_eps, sweeps, accepted moves, max |drift|."""
    labels = labels.copy()
    N, d = S.shape
    W, m = bin_stats(S, w, labels, K)
    Ie = info_matrix(W, m, eps)
    Iinv = np.linalg.inv(Ie)
    F = logdet(Ie)
    accepted = 0
    max_drift = 0.0
    sweeps_done = 0
    for sweep in range(max_sweeps):
        sweeps_done = sweep + 1
        improved = False
        for i in rng.permutation(N):
            a = labels[i]
            wi = w[i]
            s = S[i]
            if W[a] - wi <= 1e-14:           # would empty bin a
                continue
            mu_a = m[a] / W[a]
            ua = s - mu_a
            alpha = wi * W[a] / (W[a] - wi)
            va = Iinv @ ua
            qaa = float(ua @ va)
            best_gain, best = min_gain, None
            for b in range(K):
                if b == a:
                    continue
                mu_b = m[b] / W[b]
                ub = s - mu_b
                beta = wi * W[b] / (W[b] + wi)
                vb = Iinv @ ub
                qbb = float(ub @ vb)
                qab = float(ua @ vb)
                arg = (1 + alpha * qaa) * (1 - beta * qbb) + alpha * beta * qab * qab
                if arg <= 0:
                    continue
                gain = math.log(arg)
                if gain > best_gain:
                    best_gain, best = gain, (b, ub, beta)
            if best is None:
                continue
            b, ub, beta = best
            if paranoid:
                F_before = F_labels(S, w, labels, K, eps)
            labels[i] = b
            W[a] -= wi; m[a] -= wi * s
            W[b] += wi; m[b] += wi * s
            P = np.stack([ua, ub], axis=1)
            D = np.diag([alpha, -beta])
            Z = Iinv @ P
            C = np.linalg.inv(D) + P.T @ Z
            Iinv = Iinv - Z @ np.linalg.solve(C, Z.T)
            F += best_gain
            accepted += 1
            improved = True
            if paranoid:
                F_after = F_labels(S, w, labels, K, eps)
                assert F_after >= F_before - 1e-9, "monotonicity violated!"
                assert abs((F_after - F_before) - best_gain) < 1e-7, \
                    f"gain formula wrong: {F_after - F_before} vs {best_gain}"
            if accepted % 128 == 0:          # periodic refresh
                Ie = info_matrix(W, m, eps)
                Iinv = np.linalg.inv(Ie)
                F2 = logdet(Ie)
                max_drift = max(max_drift, abs(F2 - F))
                F = F2
        if not improved:
            break
    Ie = info_matrix(W, m, eps)
    F2 = logdet(Ie)
    max_drift = max(max_drift, abs(F2 - F))
    return labels, F2, sweeps_done, accepted, max_drift

def voronoi_violation(S, w, labels, K, eps):
    """max over points of q_aa - min_b q_bb (positive => Mahalanobis-Voronoi
    condition violated), using G = (I+eps)^{-1} and the partition's centroids."""
    W, m = bin_stats(S, w, labels, K)
    Ie = info_matrix(W, m, eps)
    G = np.linalg.inv(Ie)
    mus = m / W[:, None]
    worst, worst_i = -np.inf, -1
    for i in range(S.shape[0]):
        a = labels[i]
        qa = (S[i] - mus[a]) @ G @ (S[i] - mus[a])
        qb = min((S[i] - mus[b]) @ G @ (S[i] - mus[b]) for b in range(K) if b != a)
        v = qa - qb
        if v > worst:
            worst, worst_i = v, i
    return worst, worst_i

# ----------------------------------------------------------------------
# soft-Voronoi (affine logits) gradient ascent, finite differences
# ----------------------------------------------------------------------

def soft_obj(theta, S, w, K, eps_soft):
    N, d = S.shape
    V = theta[:K * d].reshape(K, d)
    t = theta[K * d:]
    Z = S @ V.T + t
    Z = Z - Z.max(1, keepdims=True)
    P = np.exp(Z)
    P /= P.sum(1, keepdims=True)
    Wb = P.T @ w
    Mb = P.T @ (w[:, None] * S)
    I = np.zeros((d, d))
    for b in range(K):
        if Wb[b] > 1e-300:
            I += np.outer(Mb[b], Mb[b]) / Wb[b]
    I += eps_soft * np.eye(d)
    return logdet(I)

def soft_voronoi(S, w, K, rng, iters=250, restarts=4):
    N, d = S.shape
    eps_soft = 1e-6 * scale_of(S, w)
    npar = K * (d + 1)
    best_lab, best_F = None, -np.inf
    for r in range(restarts):
        # init from whitened kmeans centroids -> affine Mahalanobis logits
        lab0 = whitened_kmeans(S, w, K, rng, restarts=2)
        W0, m0 = bin_stats(S, w, lab0, K)
        mus = m0 / W0[:, None]
        Sig = (w[:, None] * S).T @ S
        Gw = np.linalg.inv(Sig)
        sharp = 2.0 * (1.5 ** r)
        V = sharp * 2.0 * mus @ Gw
        t = -sharp * np.einsum('kd,de,ke->k', mus, Gw, mus)
        theta = np.concatenate([V.ravel(), t])
        lr = 0.5
        f = soft_obj(theta, S, w, K, eps_soft)
        h = 1e-5
        for it in range(iters):
            g = np.zeros(npar)
            for j in range(npar):
                tp = theta.copy(); tp[j] += h
                tm = theta.copy(); tm[j] -= h
                g[j] = (soft_obj(tp, S, w, K, eps_soft)
                        - soft_obj(tm, S, w, K, eps_soft)) / (2 * h)
            gn = np.linalg.norm(g)
            if gn < 1e-9:
                break
            ok = False
            for _ in range(25):
                cand = theta + lr * g / max(gn, 1e-12)
                fc = soft_obj(cand, S, w, K, eps_soft)
                if fc > f:
                    theta, f = cand, fc
                    lr *= 1.3
                    ok = True
                    break
                lr *= 0.5
            if not ok:
                break
        # harden
        V = theta[:K * d].reshape(K, d)
        t = theta[K * d:]
        lab = (S @ V.T + t).argmax(1)
        for b in range(K):
            if not np.any(lab == b):
                # reseed with the point of weakest margin
                Z = S @ V.T + t
                margins = Z.max(1) - np.partition(Z, -2, axis=1)[:, -2]
                lab[np.argmin(margins)] = b
        Fh = F_labels(S, w, lab, K, 0.0)
        if Fh > best_F:
            best_F, best_lab = Fh, lab.copy()
    return best_lab, best_F

# ----------------------------------------------------------------------
# exhaustive enumeration (ground truth)
# ----------------------------------------------------------------------

def all_partitions(N, K):
    """All canonical labelings (restricted growth strings) using exactly K labels."""
    total = K ** N
    idx = np.arange(total, dtype=np.int64)
    powers = K ** np.arange(N, dtype=np.int64)
    digs = ((idx[:, None] // powers[None, :]) % K).astype(np.int8)
    rm = np.maximum.accumulate(digs, axis=1)
    ok = (digs[:, 0] == 0) \
         & np.all(digs[:, 1:] <= rm[:, :-1] + 1, axis=1) \
         & (rm[:, -1] == K - 1)
    return digs[ok]

def exhaustive_best(S, w, K, also_trace=True, chunk=100000):
    N, d = S.shape
    parts = all_partitions(N, K)
    Sig = (w[:, None] * S).T @ S
    Sinv = np.linalg.inv(Sig)
    bestF, bestF_lab = -np.inf, None
    bestT, bestT_lab = -np.inf, None
    ws = w[:, None] * S
    eye = np.arange(K)
    for lo in range(0, len(parts), chunk):
        block = parts[lo:lo + chunk]
        onehot = (block[:, :, None] == eye[None, None, :])
        W = np.einsum('pnk,n->pk', onehot, w)
        M = np.einsum('pnk,nd->pkd', onehot, ws)
        I = np.einsum('pkd,pke,pk->pde', M, M, 1.0 / W)
        sign, ld = np.linalg.slogdet(I)
        ld = np.where(sign > 0, ld, -np.inf)
        j = int(np.argmax(ld))
        if ld[j] > bestF:
            bestF, bestF_lab = float(ld[j]), block[j].astype(int)
        if also_trace:
            tr = np.einsum('pde,ed->p', I, Sinv)
            j = int(np.argmax(tr))
            if tr[j] > bestT:
                bestT, bestT_lab = float(tr[j]), block[j].astype(int)
    return bestF, bestF_lab, bestT, bestT_lab, len(parts)

# ======================================================================
# unit tests
# ======================================================================

def unit_tests():
    rng = np.random.default_rng(1)
    print("== Unit tests ==")

    # U1: rank-2 Delta I formula vs brute force
    for trial in range(200):
        N, d, K = 20, 3, 4
        S, w = make_instance(rng, N=N, d=d)
        w = rng.uniform(0.5, 2.0, N); w /= w.sum()
        lab = random_labels(rng, N, K)
        W, m = bin_stats(S, w, lab, K)
        i = rng.integers(N)
        a = lab[i]
        if W[a] - w[i] <= 1e-12:
            continue
        b = (a + 1 + rng.integers(K - 1)) % K
        mu_a, mu_b = m[a] / W[a], m[b] / W[b]
        ua, ub = S[i] - mu_a, S[i] - mu_b
        alpha = w[i] * W[a] / (W[a] - w[i])
        beta = w[i] * W[b] / (W[b] + w[i])
        dI_pred = alpha * np.outer(ua, ua) - beta * np.outer(ub, ub)
        lab2 = lab.copy(); lab2[i] = b
        W2, m2 = bin_stats(S, w, lab2, K)
        dI_true = info_matrix(W2, m2) - info_matrix(W, m)
        assert np.allclose(dI_pred, dI_true, atol=1e-10), "U1 FAIL"
        # U2: determinant-lemma gain vs brute force
        eps = 1e-9 * scale_of(S, w)
        Ie = info_matrix(W, m, eps)
        Iinv = np.linalg.inv(Ie)
        qaa = ua @ Iinv @ ua; qbb = ub @ Iinv @ ub; qab = ua @ Iinv @ ub
        arg = (1 + alpha * qaa) * (1 - beta * qbb) + alpha * beta * qab ** 2
        gain_pred = math.log(arg)
        gain_true = logdet(info_matrix(W2, m2, eps)) - logdet(Ie)
        assert abs(gain_pred - gain_true) < 1e-8, "U2 FAIL"
    print("U1 rank-2 Delta-I formula: PASS (200 random trials)")
    print("U2 determinant-lemma move gain: PASS (200 random trials)")

    # U3: first-variation limit: gain/w -> q_aa - q_bb as w -> 0
    S, w = make_instance(rng, N=30, d=2)
    lab = random_labels(rng, 30, 3)
    errs = []
    for wsmall in [1e-3, 1e-4, 1e-5, 1e-6]:
        S2 = np.vstack([S, rng.normal(size=2)])
        w2 = np.concatenate([w * (1 - wsmall), [wsmall]])
        for a in range(3):
            lab2 = np.concatenate([lab, [a]])
            W, m = bin_stats(S2, w2, lab2, 3)
            I = info_matrix(W, m)
            Iinv = np.linalg.inv(I)
            mu = m / W[:, None]
            s = S2[-1]
            qa = (s - mu[a]) @ Iinv @ (s - mu[a])
            for b in range(3):
                if b == a: continue
                qb = (s - mu[b]) @ Iinv @ (s - mu[b])
                lab3 = lab2.copy(); lab3[-1] = b
                gain = F_labels(S2, w2, lab3, 3) - F_labels(S2, w2, lab2, 3)
                errs.append(abs(gain / wsmall - (qa - qb)) / (1 + abs(qa - qb)))
        # errs for this wsmall should shrink ~ linearly in wsmall
    print(f"U3 first-variation limit: rel. error at w=1e-3..1e-6: "
          f"{max(errs[:6]):.2e} -> {max(errs[-6:]):.2e}  PASS"
          if max(errs[-6:]) < 1e-4 else "U3 FAIL")

    # U4: tie-move threshold q < 1/W_a + 1/W_b (q_ab = 0 case), synthetic
    ok = True
    for trial in range(500):
        Wa, Wb, wi = rng.uniform(0.1, 0.5), rng.uniform(0.1, 0.5), 0.02
        alpha = wi * Wa / (Wa - wi); beta = wi * Wb / (Wb + wi)
        q = rng.uniform(0.01, 30.0)
        arg = (1 + alpha * q) * (1 - beta * q)          # q_ab = 0, q_aa=q_bb=q
        gain = math.log(arg) if arg > 0 else -np.inf
        thresh = 1.0 / Wa + 1.0 / Wb
        if (gain > 1e-12) != (q < thresh - 1e-9):
            if abs(q - thresh) > 1e-6:
                ok = False
    print("U4 tie-move threshold q<1/W_a+1/W_b: " + ("PASS" if ok else "FAIL"))

# ======================================================================
# E1: adaptive-Lloyd monotonicity violations
# ======================================================================

def e1_lloyd_monotonicity(n_instances=300, seed=10):
    rng = np.random.default_rng(seed)
    print("\n== E1: monotonicity of adaptive-Mahalanobis Lloyd ==")
    n_bad_inst = 0
    n_runs = 0
    n_bad_runs = 0
    smallest = None    # (N, instance seed info, traj)
    for t in range(n_instances):
        N = int(rng.choice([8, 10, 12, 16, 24, 40]))
        K = int(rng.choice([3, 4]))
        S, w = make_instance(rng, N=N, d=2, aniso=rng.uniform(0.3, 1.0))
        eps = 1e-9 * scale_of(S, w)
        bad_here = False
        for r in range(8):
            lab0 = random_labels(rng, N, K)
            lab, tp, treg, states = adaptive_lloyd(S, w, lab0, K, eps)
            n_runs += 1
            for j in range(1, len(tp)):
                if (np.isfinite(tp[j - 1]) and np.isfinite(tp[j])
                        and tp[j] < tp[j - 1] - 1e-9):
                    bad_here = True
                    n_bad_runs += 1
                    if smallest is None or N < smallest[0]:
                        smallest = (N, K, S.copy(), w.copy(),
                                    states[j - 1].copy(), states[j].copy(),
                                    tp[j - 1], tp[j])
                    break
        if bad_here:
            n_bad_inst += 1
    print(f"instances with >=1 strictly decreasing batch step: "
          f"{n_bad_inst}/{n_instances}")
    print(f"runs with a decrease: {n_bad_runs}/{n_runs}")
    if smallest:
        N, K, S, w, labA, labB, fA, fB = smallest
        print(f"\nSmallest counterexample found: N={N}, K={K}, uniform weights")
        print("scores (rows):")
        for row in S:
            print("   [%8.4f, %8.4f]" % (row[0], row[1]))
        print("state A labels:", labA, " logdet =", f"{fA:.6f}")
        print("state B labels (after one batch Lloyd step):", labB,
              " logdet =", f"{fB:.6f}")
        print(f"decrease: {fA - fB:.6f} nats")
    return smallest

# ======================================================================
# E2: exhaustive comparison
# ======================================================================

def e2_exhaustive(n_instances=30, N=12, K=3, seed=20):
    rng = np.random.default_rng(seed)
    print(f"\n== E2: exhaustive ground truth, N={N}, K={K}, d=2, "
          f"{n_instances} instances ==")
    tol = 1e-7
    hits = {k: 0 for k in ["wkmeans", "lloyd", "soft", "exch", "exch_from_km"]}
    gaps = {k: [] for k in hits}
    trace_disagree = 0
    trace_gaps = []
    example_trace = None
    for t in range(n_instances):
        S, w = make_instance(rng, N=N, d=2, aniso=rng.uniform(0.2, 1.0))
        eps = 1e-9 * scale_of(S, w)
        Fstar, labF, Tstar, labT, nparts = exhaustive_best(S, w, K)
        # trace-optimal vs D-optimal
        F_of_traceopt = F_labels(S, w, labT, K)
        if Fstar - F_of_traceopt > tol:
            trace_disagree += 1
            trace_gaps.append(Fstar - F_of_traceopt)
            if example_trace is None or (Fstar - F_of_traceopt) > example_trace[0]:
                example_trace = (Fstar - F_of_traceopt, S.copy(), labF.copy(),
                                 labT.copy(), Fstar, F_of_traceopt)
        # methods (equalized modest budgets)
        results = {}
        lab_km = whitened_kmeans(S, w, K, rng, restarts=10)
        results["wkmeans"] = F_labels(S, w, lab_km, K)
        bestL = -np.inf
        for r in range(10):
            lab0 = random_labels(rng, N, K)
            labL, tp, _, _ = adaptive_lloyd(S, w, lab0, K, eps)
            bestL = max(bestL, F_labels(S, w, labL, K))
        results["lloyd"] = bestL
        _, Fs = soft_voronoi(S, w, K, rng, restarts=3)
        results["soft"] = Fs
        bestE = -np.inf
        for r in range(10):
            lab0 = random_labels(rng, N, K)
            labE, FE, _, _, _ = exchange(S, w, lab0, K, eps, rng)
            bestE = max(bestE, F_labels(S, w, labE, K))
        results["exch"] = bestE
        labE2, FE2, _, _, _ = exchange(S, w, lab_km, K, eps, rng)
        results["exch_from_km"] = F_labels(S, w, labE2, K)
        for k, v in results.items():
            gap = Fstar - v
            gaps[k].append(gap)
            if gap < tol:
                hits[k] += 1
    print(f"partitions enumerated per instance: {nparts}")
    print(f"{'method':>14} {'hit global':>10} {'median gap':>12} {'max gap':>10}")
    for k in hits:
        g = np.array(gaps[k])
        print(f"{k:>14} {hits[k]:>7}/{n_instances} {np.median(g):>12.4g} "
              f"{g.max():>10.4g}")
    print(f"\ntrace-optimal partition != D-optimal partition (logdet gap > tol): "
          f"{trace_disagree}/{n_instances}")
    if trace_gaps:
        print(f"logdet gap of trace-optimal partition: median "
              f"{np.median(trace_gaps):.4f}, max {max(trace_gaps):.4f} nats")
    if example_trace:
        g, S, labF, labT, Fs, Ft = example_trace
        print(f"\nWorst example: logdet(D-opt)={Fs:.4f}, "
              f"logdet(trace-opt)={Ft:.4f}, gap={g:.4f}")
    return example_trace

# ======================================================================
# E3: Lloyd fixed points improved by exact exchange
# ======================================================================

def e3_fixed_points(n_instances=100, seed=30):
    rng = np.random.default_rng(seed)
    print("\n== E3: adaptive-Lloyd fixed points vs exchange stability ==")
    n_fp = 0
    n_improvable = 0
    example = None
    for t in range(n_instances):
        N = int(rng.choice([12, 20, 30]))
        K = 3
        S, w = make_instance(rng, N=N, d=2)
        eps = 1e-9 * scale_of(S, w)
        lab0 = random_labels(rng, N, K)
        lab, tp, _, _ = adaptive_lloyd(S, w, lab0, K, eps, max_iter=100)
        # confirm fixed point (assignment stable)
        lab2, tp2, _, _ = adaptive_lloyd(S, w, lab, K, eps, max_iter=2)
        if not np.array_equal(lab2, lab):
            continue
        n_fp += 1
        F0 = F_labels(S, w, lab, K)
        labE, FE, _, acc, _ = exchange(S, w, lab, K, eps, rng)
        F1 = F_labels(S, w, labE, K)
        if F1 > F0 + 1e-8:
            n_improvable += 1
            if example is None or F1 - F0 > example[0]:
                example = (F1 - F0, N, F0, F1, acc)
    print(f"Lloyd fixed points reached: {n_fp}")
    print(f"...of which strictly improved by exact exchange: {n_improvable}")
    if example:
        g, N, F0, F1, acc = example
        print(f"largest improvement: {g:.4f} nats (N={N}, "
              f"{acc} exchange moves, {F0:.4f} -> {F1:.4f})")

# ======================================================================
# E4: exchange-stable but Voronoi-violating
# ======================================================================

def e4_exchange_vs_voronoi(n_instances=400, seed=40):
    rng = np.random.default_rng(seed)
    print("\n== E4: exchange-stable partitions violating Mahalanobis-Voronoi ==")
    found = 0
    example = None
    for t in range(n_instances):
        N = int(rng.choice([6, 8, 10, 12]))
        K = 3
        S, w = make_instance(rng, N=N, d=2)
        if t % 2 == 1:
            # heavy-weight variant to boost leverage
            w = rng.uniform(0.5, 3.0, N)
            j = rng.integers(N)
            w[j] = rng.uniform(5.0, 10.0)
            w /= w.sum()
            S = S - (w[:, None] * S).sum(0)
        eps = 1e-9 * scale_of(S, w)
        lab0 = random_labels(rng, N, K)
        lab, F, _, _, _ = exchange(S, w, lab0, K, eps, rng)
        viol, i = voronoi_violation(S, w, lab, K, eps)
        # normalize violation by typical q scale
        if viol > 1e-6:
            found += 1
            if example is None or viol > example[0]:
                example = (viol, N, S.copy(), w.copy(), lab.copy(), i, F)
    print(f"exchange-stable states with a Voronoi violation: "
          f"{found}/{n_instances}")
    if example:
        viol, N, S, w, lab, i, F = example
        W, m = bin_stats(S, w, lab, 3)
        print(f"\nExample: N={N}, violation q_aa - min_b q_bb = {viol:.4f} "
              f"at point {i} (weight {w[i]:.3f}), logdet={F:.4f}")
        print("weights:", np.round(w, 3))
        print("labels: ", lab)
        print("bin masses:", np.round(W, 3))
        # confirm no single move improves
        eps = 1e-9 * scale_of(S, w)
        lab2, F2, _, acc, _ = exchange(S, w, lab, 3, eps,
                                       np.random.default_rng(0))
        print(f"re-run exchange from this state: accepted moves = {acc} "
              f"(0 confirms stability)")
    return example

# ======================================================================

# ======================================================================
# U5: theorem check: exchange-stable => Voronoi
#   Lemma: q_delta = (mu_a-mu_b)^T I^{-1} (mu_a-mu_b) <= 1/W_a + 1/W_b
#   Theorem: q_aa >= q_bb  =>  exact gain = log(1+E), E >= alpha*beta*q_delta^2/4 > 0
# ======================================================================
def u5_theorem_check(n_trials=4000, seed=99):
    rng = np.random.default_rng(seed)
    ok_lemma = ok_thm = True
    worst_margin = np.inf
    for t in range(n_trials):
        N = int(rng.choice([5, 6, 8, 12]))
        K = 3
        S, w = make_instance(rng, N=N, d=2)
        w = rng.uniform(0.2, 5.0, N); w /= w.sum()
        S = S - (w[:, None] * S).sum(0)
        lab = random_labels(rng, N, K)
        W, m = bin_stats(S, w, lab, K)
        I = info_matrix(W, m)
        if not np.isfinite(logdet(I)):
            continue
        Iinv = np.linalg.inv(I)
        mus = m / W[:, None]
        for a in range(K):
            for b in range(K):
                if a == b: continue
                dlt = mus[b] - mus[a]
                qd = dlt @ Iinv @ dlt
                bound = 1.0 / W[a] + 1.0 / W[b]
                if qd > bound * (1 + 1e-6):
                    ok_lemma = False
        for i in range(N):
            a = lab[i]
            if W[a] - w[i] <= 1e-12: continue
            ua = S[i] - mus[a]
            alpha = w[i] * W[a] / (W[a] - w[i])
            qaa = ua @ Iinv @ ua
            for b in range(K):
                if b == a: continue
                ub = S[i] - mus[b]
                beta = w[i] * W[b] / (W[b] + w[i])
                qbb = ub @ Iinv @ ub
                qab = ua @ Iinv @ ub
                if qaa >= qbb - 1e-12:      # Voronoi-violating or tie
                    dlt = mus[b] - mus[a]
                    qd = dlt @ Iinv @ dlt
                    E = alpha*qaa - beta*qbb - alpha*beta*(qaa*qbb - qab**2)
                    lower = alpha*beta*qd*qd/4.0
                    if E < lower - 1e-9:
                        ok_thm = False
                    worst_margin = min(worst_margin, E - lower)
    print("U5 lemma q_delta <= 1/W_a+1/W_b on real configs: "
          + ("PASS" if ok_lemma else "FAIL"))
    print("U5 theorem E >= alpha*beta*q_delta^2/4 for all Voronoi-violating "
          "moves: " + ("PASS" if ok_thm else "FAIL")
          + f"  (min slack {worst_margin:.2e})")

if __name__ == "__main__":
    import time
    t0 = time.time()
    unit_tests()
    u5_theorem_check()
    e1_lloyd_monotonicity()
    e2_exhaustive()
    e3_fixed_points()
    e4_exchange_vs_voronoi()
    print(f"\ntotal time: {time.time() - t0:.1f}s")
