"""Complete variables -> components -> scores -> bins user workflow."""

from __future__ import annotations

import numpy as np

import scorequant as sq


def signal(X: np.ndarray) -> np.ndarray:
    energy, cos_theta = X.T
    return 0.05 + np.exp(-0.5 * ((energy - 0.62) / 0.10) ** 2) * (1 + 0.5 * cos_theta)


def background_1(X: np.ndarray) -> np.ndarray:
    energy, cos_theta = X.T
    return 0.2 + (1 - energy) ** 2 * (1 - 0.25 * cos_theta)


def background_2(X: np.ndarray) -> np.ndarray:
    energy, cos_theta = X.T
    return 0.15 + energy * (1 + 0.4 * cos_theta**2)


def build_model() -> sq.LinearComponents:
    return sq.LinearComponents(
        components={
            "signal": signal,
            "background_1": background_1,
            "background_2": background_2,
        },
        coefficients={"signal": 1.0, "background_1": 0.4, "background_2": 0.2},
        variables=["energy", "cos_theta"],
    )


def run(seed: int = 17) -> tuple[sq.QuantizerResult, np.ndarray]:
    rng = np.random.default_rng(seed)
    X_mc = np.column_stack([rng.uniform(0, 1, 2_000), rng.uniform(-1, 1, 2_000)])
    mc_weights = 0.5 + rng.random(len(X_mc))
    model = build_model()
    result = sq.fit_quantizer(
        sq.ObservationSample(X_mc, mc_weights),
        score=sq.LinearComponentScore(model),
        n_bins=8,
        criterion=sq.DOptimality(),
        config=sq.DExchangeConfig(seed=seed),
    )

    X_data = np.column_stack([rng.uniform(0, 1, 500), rng.uniform(-1, 1, 500)])
    data_bins = result.predict_scores(sq.LinearComponentScore(model).score(X_data))
    counts = np.bincount(np.asarray(data_bins), minlength=result.n_bins)
    return result, counts


if __name__ == "__main__":
    fitted, bin_counts = run()
    print(fitted.report())
    print("data counts:", bin_counts)
