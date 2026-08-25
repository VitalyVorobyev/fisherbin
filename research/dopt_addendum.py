#!/usr/bin/env python3
"""Addendum experiments E5-E8."""
import numpy as np, math, time
from dopt_experiments import (bin_stats, info_matrix, logdet, F_labels,
                              scale_of, make_instance, random_labels,
                              whitened_kmeans, adaptive_lloyd, exchange,
                              voronoi_violation, exhaustive_best)

# ----------------------------------------------------------------------
# E5: per-run local optima of exchange (single init) vs global optimum
# ----------------------------------------------------------------------
def e5(n_instances=20, N=12, K=3, seed=50):
    rng = np.random.default_rng(seed)
    print("== E5: single-run exchange local optima vs global (exhaustive) ==")
    tot_rand, hit_rand = 0, 0
    tot_km, hit_km = 0, 0
    worst_gap = 0.0
    for t in range(n_instances):
        S, w = make_instance(rng, N=N, d=2, aniso=rng.uniform(0.2, 1.0))
        eps = 1e-9 * scale_of(S, w)
        Fstar, _, _, _, _ = exhaustive_best(S, w, K, also_trace=False)
        for r in range(10):
            lab0 = random_labels(rng, N, K)
            lab, F, _, _, _ = exchange(S, w, lab0, K, eps, rng)
            F = F_labels(S, w, lab, K)
            tot_rand += 1
            if Fstar - F < 1e-7:
                hit_rand += 1
            else:
                worst_gap = max(worst_gap, Fstar - F)
        lab_km = whitened_kmeans(S, w, K, rng, restarts=5)
        lab, F, _, _, _ = exchange(S, w, lab_km, K, eps, rng)
        F = F_labels(S, w, lab, K)
        tot_km += 1
        if Fstar - F < 1e-7:
            hit_km += 1
    print(f"random-init single runs reaching global: {hit_rand}/{tot_rand} "
          f"({100*hit_rand/tot_rand:.0f}%), worst gap {worst_gap:.4f} nats")
    print(f"whitened-kmeans-init single runs reaching global: {hit_km}/{tot_km}")

# ----------------------------------------------------------------------
# E6: first-order vs exact move criterion disagreements (single moves)
# ----------------------------------------------------------------------
def e6(n_trials=20000, seed=60):
    rng = np.random.default_rng(seed)
    print("\n== E6: first-order vs exact single-move disagreement ==")
    n_fo_pos_exact_neg = 0     # Voronoi says move, exact says don't
    n_fo_neg_exact_pos = 0     # Voronoi says stay, exact says move
    n_tested = 0
    ex1 = ex2 = None
    for t in range(n_trials):
        N = int(rng.choice([6, 8, 10]))
        K = 3
        S, w = make_instance(rng, N=N, d=2)
        if t % 2 == 1:
            w = rng.uniform(0.5, 4.0, N); w /= w.sum()
            S = S - (w[:, None] * S).sum(0)
        lab = random_labels(rng, N, K)
        W, m = bin_stats(S, w, lab, K)
        I = info_matrix(W, m)
        if not np.isfinite(logdet(I)):
            continue
        Iinv = np.linalg.inv(I)
        i = rng.integers(N)
        a = lab[i]
        if W[a] - w[i] <= 1e-12:
            continue
        b = (a + 1 + rng.integers(K - 1)) % K
        mu_a, mu_b = m[a]/W[a], m[b]/W[b]
        ua, ub = S[i]-mu_a, S[i]-mu_b
        alpha = w[i]*W[a]/(W[a]-w[i]); beta = w[i]*W[b]/(W[b]+w[i])
        qaa = ua@Iinv@ua; qbb = ub@Iinv@ub; qab = ua@Iinv@ub
        fo = qaa - qbb
        arg = (1+alpha*qaa)*(1-beta*qbb)+alpha*beta*qab**2
        exact = math.log(arg) if arg > 0 else -np.inf
        n_tested += 1
        if fo > 1e-9 and exact < -1e-9:
            n_fo_pos_exact_neg += 1
            if ex1 is None or fo > ex1[0]:
                ex1 = (fo, exact, w[i], W[a], W[b], qaa, qbb)
        if fo < -1e-9 and exact > 1e-9:
            n_fo_neg_exact_pos += 1
            if ex2 is None or exact > ex2[1]:
                ex2 = (fo, exact, w[i], W[a], W[b], qaa, qbb)
    print(f"tested random single moves: {n_tested}")
    print(f"first-order>0 (Voronoi-violating) but exact gain<0: "
          f"{n_fo_pos_exact_neg}")
    if ex1:
        fo, exg, wi, Wa, Wb, qaa, qbb = ex1
        print(f"  example: w={wi:.3f} W_a={Wa:.3f} W_b={Wb:.3f} "
              f"q_aa={qaa:.2f} q_bb={qbb:.2f}  fo={fo:.3f} exact={exg:.4f}")
    print(f"first-order<0 (Voronoi-satisfied) but exact gain>0: "
          f"{n_fo_neg_exact_pos}")
    if ex2:
        fo, exg, wi, Wa, Wb, qaa, qbb = ex2
        print(f"  example: w={wi:.3f} W_a={Wa:.3f} W_b={Wb:.3f} "
              f"q_aa={qaa:.2f} q_bb={qbb:.2f}  fo={fo:.3f} exact={exg:.4f}")

# ----------------------------------------------------------------------
# E7: adversarial search for exchange-stable state violating Voronoi
# ----------------------------------------------------------------------
def check_exchange_stable(S, w, lab, K, eps):
    """True if no single strictly-improving move exists."""
    N = S.shape[0]
    W, m = bin_stats(S, w, lab, K)
    Ie = info_matrix(W, m, eps)
    Iinv = np.linalg.inv(Ie)
    for i in range(N):
        a = lab[i]
        if W[a]-w[i] <= 1e-14:
            continue
        mu_a = m[a]/W[a]; ua = S[i]-mu_a
        alpha = w[i]*W[a]/(W[a]-w[i])
        qaa = ua@Iinv@ua
        for b in range(K):
            if b == a: continue
            mu_b = m[b]/W[b]; ub = S[i]-mu_b
            beta = w[i]*W[b]/(W[b]+w[i])
            qbb = ub@Iinv@ub; qab = ua@Iinv@ub
            arg = (1+alpha*qaa)*(1-beta*qbb)+alpha*beta*qab**2
            if arg > 0 and math.log(arg) > 1e-10:
                return False
    return True

def e7(seed=70, budget_s=90):
    rng = np.random.default_rng(seed)
    print("\n== E7: adversarial search: exchange-stable AND Voronoi-violating ==")
    t0 = time.time()
    best_viol = 0.0
    found = None
    n_stable = 0
    while time.time() - t0 < budget_s:
        # extreme geometries: two distant heavy groups + satellites
        N = int(rng.choice([5, 6, 7, 8]))
        K = 3
        mode = rng.integers(3)
        if mode == 0:
            S = rng.normal(size=(N, 2)) * rng.uniform(0.5, 3.0)
        elif mode == 1:
            base = np.array([[-1, 0], [1, 0], [0, 0.05]])[rng.integers(3, size=N)]
            S = base * rng.uniform(1, 8) + rng.normal(size=(N, 2)) * 0.4
        else:
            ang = rng.uniform(0, 2*np.pi, N)
            rad = rng.choice([0.1, 1.0, 6.0], N)
            S = np.stack([rad*np.cos(ang), rad*np.sin(ang)], 1)
        w = rng.uniform(0.2, 1.0, N)
        if rng.random() < 0.7:
            w[rng.integers(N)] = rng.uniform(3, 12)
        w /= w.sum()
        S = S - (w[:, None]*S).sum(0)
        eps = 1e-10 * scale_of(S, w)
        lab0 = random_labels(rng, N, K)
        lab, F, _, _, _ = exchange(S, w, lab0, K, eps, rng, min_gain=1e-10)
        if not np.isfinite(F_labels(S, w, lab, K)):
            continue
        if not check_exchange_stable(S, w, lab, K, eps):
            continue
        n_stable += 1
        viol, i = voronoi_violation(S, w, lab, K, eps)
        if viol > best_viol:
            best_viol = viol
            if viol > 1e-6:
                found = (S.copy(), w.copy(), lab.copy(), i, viol)
    print(f"stable states examined: {n_stable}; "
          f"max Voronoi violation found: {best_viol:.3e}")
    if found:
        S, w, lab, i, viol = found
        print("FOUND exchange-stable Voronoi-violating state:")
        print("S =\n", np.round(S, 4))
        print("w =", np.round(w, 4), " labels =", lab,
              f" violating point {i}, q_aa - min q_bb = {viol:.4f}")
    else:
        print("none found (supports conjecture: exchange-stable => Voronoi)")

# ----------------------------------------------------------------------
# E8: larger-scale practical comparison / timing
# ----------------------------------------------------------------------
def e8(seed=80):
    rng = np.random.default_rng(seed)
    print("\n== E8: N=400, d=4, K=8 practical comparison (5 instances) ==")
    for t in range(5):
        S, w = make_instance(rng, N=400, d=4, ncomp=6)
        eps = 1e-9 * scale_of(S, w)
        # A: exchange from random
        t0 = time.time()
        best = -np.inf
        for r in range(3):
            lab0 = random_labels(rng, 400, 8)
            lab, F, sw, acc, drift = exchange(S, w, lab0, 8, eps, rng)
            best = max(best, F_labels(S, w, lab, 8))
        tA = time.time() - t0
        # B: whitened kmeans -> exchange
        t0 = time.time()
        lab_km = whitened_kmeans(S, w, 8, rng, restarts=5)
        F_km = F_labels(S, w, lab_km, 8)
        lab, F, sw, acc, drift = exchange(S, w, lab_km, 8, eps, rng)
        F_B = F_labels(S, w, lab, 8)
        tB = time.time() - t0
        # C: adaptive Lloyd from kmeans (no guard), then exchange polish
        t0 = time.time()
        labL, tp, _, _ = adaptive_lloyd(S, w, lab_km, 8, eps)
        F_L = F_labels(S, w, labL, 8)
        lab, F, _, acc2, _ = exchange(S, w, labL, 8, eps, rng)
        F_C = F_labels(S, w, lab, 8)
        tC = time.time() - t0
        dec = any(tp[j] < tp[j-1] - 1e-9 for j in range(1, len(tp)))
        print(f"inst {t}: kmeans {F_km:.4f} | 3x rand-exch {best:.4f} ({tA:.1f}s)"
              f" | km->exch {F_B:.4f} ({tB:.1f}s) | km->lloyd {F_L:.4f}"
              f"{' [DECREASED]' if dec else ''} ->exch {F_C:.4f} ({tC:.1f}s)")

if __name__ == "__main__":
    t0 = time.time()
    e5(); e6(); e7(); e8()
    print(f"\ntotal {time.time()-t0:.1f}s")
