"""Private JAX implementations of FisherBin's two quantizers."""

from __future__ import annotations

from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np
import optax

from .config import KMeansConfig, SoftVoronoiConfig
from .transforms import fisher_transform


@dataclass(slots=True)
class QuantizerRun:
    centers: jnp.ndarray
    steps: list[int]
    center_history: list[jnp.ndarray]
    objective_history: list[float]
    bin_weight_history: list[jnp.ndarray]
    soft_retention_history: list[float] | None = None
    temperature_history: list[float] | None = None
    gradient_norm_history: list[float] | None = None


def squared_distances(points: jnp.ndarray, centers: jnp.ndarray) -> jnp.ndarray:
    """Return the dense ``[N, B]`` squared Euclidean distance matrix."""

    return jnp.sum((points[:, None, :] - centers[None, :, :]) ** 2, axis=2)


def hard_assign(points: jnp.ndarray, centers: jnp.ndarray) -> jnp.ndarray:
    return jnp.argmin(squared_distances(points, centers), axis=1)


def _bin_weights(labels: jnp.ndarray, weights: jnp.ndarray, n_bins: int) -> jnp.ndarray:
    return jnp.zeros(n_bins, dtype=weights.dtype).at[labels].add(weights)


def _weighted_kmeans_plus_plus(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    key: jax.Array,
) -> jnp.ndarray:
    keys = jax.random.split(key, n_bins)
    first = jax.random.choice(keys[0], points.shape[0], p=weights / jnp.sum(weights))
    indices = [int(np.asarray(first))]
    minimum_distances = squared_distances(points, points[first : first + 1])[:, 0]
    for bin_index in range(1, n_bins):
        probabilities = weights * minimum_distances
        total = float(np.asarray(jnp.sum(probabilities)))
        if not np.isfinite(total) or total <= 0:
            raise ValueError(
                "n_bins exceeds the number of distinct positive-weight score coordinates"
            )
        chosen = jax.random.choice(
            keys[bin_index], points.shape[0], p=probabilities / jnp.sum(probabilities)
        )
        indices.append(int(np.asarray(chosen)))
        candidate_distances = squared_distances(points, points[chosen : chosen + 1])[:, 0]
        minimum_distances = jnp.minimum(minimum_distances, candidate_distances)
    return points[jnp.asarray(indices)]


def _single_kmeans(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    config: KMeansConfig,
    key: jax.Array,
) -> QuantizerRun:
    centers = _weighted_kmeans_plus_plus(points, weights, n_bins, key)
    steps: list[int] = []
    center_history: list[jnp.ndarray] = []
    objective_history: list[float] = []
    bin_weight_history: list[jnp.ndarray] = []
    previous_objective: float | None = None

    for iteration in range(config.max_iter):
        distances = squared_distances(points, centers)
        labels = jnp.argmin(distances, axis=1)
        selected_distances = distances[jnp.arange(points.shape[0]), labels]
        objective = float(np.asarray(jnp.sum(weights * selected_distances)))
        occupancies = _bin_weights(labels, weights, n_bins)
        weighted_sums = jnp.zeros((n_bins, points.shape[1]), dtype=points.dtype)
        weighted_sums = weighted_sums.at[labels].add(weights[:, None] * points)
        proposed = weighted_sums / jnp.where(occupancies > 0, occupancies, 1)[:, None]

        if bool(np.asarray(jnp.any(occupancies == 0))):
            residual = weights * selected_distances
            for empty_bin in np.flatnonzero(np.asarray(occupancies == 0)):
                replacement = int(np.asarray(jnp.argmax(residual)))
                proposed = proposed.at[empty_bin].set(points[replacement])
                residual = residual.at[replacement].set(-jnp.inf)

        should_record = iteration % config.record_every == 0
        converged = previous_objective is not None and abs(
            previous_objective - objective
        ) <= config.tolerance * max(abs(previous_objective), 1.0)
        if should_record or converged or iteration == config.max_iter - 1:
            steps.append(iteration)
            center_history.append(centers)
            objective_history.append(objective)
            bin_weight_history.append(occupancies)
        centers = proposed
        if converged:
            break
        previous_objective = objective

    # Record the updated final centers if they differ from the last recorded state.
    distances = squared_distances(points, centers)
    labels = jnp.argmin(distances, axis=1)
    final_objective = float(
        np.asarray(jnp.sum(weights * distances[jnp.arange(points.shape[0]), labels]))
    )
    if not objective_history or not np.isclose(final_objective, objective_history[-1]):
        steps.append(steps[-1] + 1 if steps else 0)
        center_history.append(centers)
        objective_history.append(final_objective)
        bin_weight_history.append(_bin_weights(labels, weights, n_bins))
    return QuantizerRun(
        centers=centers,
        steps=steps,
        center_history=center_history,
        objective_history=objective_history,
        bin_weight_history=bin_weight_history,
    )


def weighted_kmeans(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    config: KMeansConfig,
) -> QuantizerRun:
    """Run seeded weighted k-means restarts and return the lowest-SSE run."""

    if config.n_init < 1 or config.max_iter < 1 or config.record_every < 1:
        raise ValueError("n_init, max_iter, and record_every must be positive")
    if config.tolerance < 0 or not np.isfinite(config.tolerance):
        raise ValueError("tolerance must be finite and nonnegative")
    keys = jax.random.split(jax.random.PRNGKey(config.seed), config.n_init)
    runs = [_single_kmeans(points, weights, n_bins, config, key) for key in keys]
    return min(runs, key=lambda run: run.objective_history[-1])


def _normalized_objective_scores(
    points: jnp.ndarray, weights: jnp.ndarray, rank_rtol: float | None
) -> jnp.ndarray:
    fisher = jnp.einsum("n,np,nq->pq", weights, points, points)
    return points @ fisher_transform(fisher, whiten=True, rank_rtol=rank_rtol).matrix


def soft_responsibilities(
    points: jnp.ndarray, centers: jnp.ndarray, temperature: float | jnp.ndarray
) -> jnp.ndarray:
    """Return stable soft nearest-center responsibilities."""

    logits = -squared_distances(points, centers) / (2 * jnp.asarray(temperature) ** 2)
    return jax.nn.softmax(logits, axis=1)


def _soft_fisher(
    objective_scores: jnp.ndarray,
    responsibilities: jnp.ndarray,
    weights: jnp.ndarray,
) -> jnp.ndarray:
    weighted_resp = weights[:, None] * responsibilities
    occupancies = jnp.sum(weighted_resp, axis=0)
    sums = weighted_resp.T @ objective_scores
    means = sums / jnp.maximum(occupancies[:, None], jnp.finfo(weights.dtype).tiny)
    fisher = jnp.einsum("b,bp,bq->pq", occupancies, means, means)
    return 0.5 * (fisher + fisher.T)


def soft_voronoi(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    effective_rank: int,
    config: SoftVoronoiConfig,
) -> QuantizerRun:
    """Optimize soft Fisher retention, then return centers for hard assignment."""

    if n_bins < effective_rank:
        raise ValueError(
            "soft D-optimal fitting requires n_bins >= the effective Fisher rank; "
            "use k-means for smaller partitions"
        )
    if config.max_steps < 1 or config.record_every < 1:
        raise ValueError("max_steps and record_every must be positive")
    if config.learning_rate <= 0 or config.gradient_clip <= 0:
        raise ValueError("learning_rate and gradient_clip must be positive")
    if not 0 < config.temperature_end_ratio <= 1:
        raise ValueError("temperature_end_ratio must lie in (0, 1]")

    initializer_config = KMeansConfig(
        whiten=config.whiten,
        rank_rtol=config.rank_rtol,
        seed=config.seed,
        n_init=config.n_init,
        max_iter=config.kmeans_max_iter,
        tolerance=config.tolerance,
        record_every=max(config.kmeans_max_iter, 1),
    )
    initial = weighted_kmeans(points, weights, n_bins, initializer_config)
    centers = initial.centers
    if n_bins == 1:
        return QuantizerRun(
            centers=centers,
            steps=[0],
            center_history=[centers],
            objective_history=[0.0],
            bin_weight_history=[jnp.asarray([jnp.sum(weights)])],
            soft_retention_history=[1.0],
            temperature_history=[1.0],
            gradient_norm_history=[0.0],
        )

    center_distances = squared_distances(centers, centers)
    center_distances = jnp.where(jnp.eye(n_bins, dtype=bool), jnp.inf, center_distances)
    nearest_separations = jnp.sqrt(jnp.min(center_distances, axis=1))
    start_temperature = float(np.asarray(jnp.median(nearest_separations)))
    if not np.isfinite(start_temperature) or start_temperature <= 0:
        raise ValueError("soft optimization requires distinct initial centers")
    end_temperature = start_temperature * config.temperature_end_ratio
    objective_scores = _normalized_objective_scores(points, weights, config.rank_rtol)
    epsilon = 1e-8 if points.dtype == jnp.float64 else 1e-5
    identity = jnp.eye(effective_rank, dtype=points.dtype)

    def loss_fn(current_centers: jnp.ndarray, temperature: jnp.ndarray) -> jnp.ndarray:
        resp = soft_responsibilities(points, current_centers, temperature)
        soft_fisher = _soft_fisher(objective_scores, resp, weights)
        _, logdet = jnp.linalg.slogdet(soft_fisher + epsilon * identity)
        return -logdet

    # Fisher whitening contains the total information scale, so coordinate
    # magnitudes shrink as total sample weight grows. Express Adam's step in
    # units of the initialized center separation to keep fitting scale-invariant.
    optimizer = optax.chain(
        optax.clip_by_global_norm(config.gradient_clip),
        optax.adam(config.learning_rate * start_temperature),
    )
    state = optimizer.init(centers)

    @jax.jit
    def update(
        current_centers: jnp.ndarray, optimizer_state: optax.OptState, temperature: jnp.ndarray
    ) -> tuple[jnp.ndarray, optax.OptState, jnp.ndarray, jnp.ndarray]:
        loss, gradients = jax.value_and_grad(loss_fn)(current_centers, temperature)
        updates, optimizer_state = optimizer.update(gradients, optimizer_state, current_centers)
        return (
            optax.apply_updates(current_centers, updates),
            optimizer_state,
            loss,
            optax.tree.norm(gradients),
        )

    steps: list[int] = []
    center_history: list[jnp.ndarray] = []
    objective_history: list[float] = []
    bin_weight_history: list[jnp.ndarray] = []
    soft_retention_history: list[float] = []
    temperature_history: list[float] = []
    gradient_norm_history: list[float] = []

    for step in range(config.max_steps + 1):
        fraction = step / config.max_steps
        temperature = start_temperature * (end_temperature / start_temperature) ** fraction
        if step > 0:
            centers, state, loss, gradient_norm = update(centers, state, jnp.asarray(temperature))
        else:
            loss = loss_fn(centers, jnp.asarray(temperature))
            gradient_norm = jnp.asarray(0.0, dtype=points.dtype)
        if step % config.record_every == 0 or step == config.max_steps:
            resp = soft_responsibilities(points, centers, temperature)
            soft_fisher = _soft_fisher(objective_scores, resp, weights)
            eig = jnp.linalg.eigvalsh(soft_fisher)
            retention = float(
                np.asarray(
                    jnp.where(
                        jnp.any(eig <= 0),
                        0.0,
                        jnp.exp(jnp.mean(jnp.log(eig))),
                    )
                )
            )
            labels = hard_assign(points, centers)
            steps.append(step)
            center_history.append(centers)
            objective_history.append(float(np.asarray(-loss)))
            bin_weight_history.append(_bin_weights(labels, weights, n_bins))
            soft_retention_history.append(retention)
            temperature_history.append(float(temperature))
            gradient_norm_history.append(float(np.asarray(gradient_norm)))

    return QuantizerRun(
        centers=centers,
        steps=steps,
        center_history=center_history,
        objective_history=objective_history,
        bin_weight_history=bin_weight_history,
        soft_retention_history=soft_retention_history,
        temperature_history=temperature_history,
        gradient_norm_history=gradient_norm_history,
    )
