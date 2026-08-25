"""Private JAX implementations of ScoreQuant geometric quantizers."""

from __future__ import annotations

from dataclasses import dataclass, field

import jax
import jax.numpy as jnp
import numpy as np
import optax

from .config import KMeansConfig, ScalarDPConfig, SoftVoronoiConfig
from .criteria import DOptimality, ProfiledDOptimality
from .transforms import fisher_transform


@dataclass(slots=True)
class QuantizerRun:
    """Aggregate state returned by a private quantizer implementation."""

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
    """Assign each point to its nearest center."""
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
    norms = np.asarray(jnp.sum(points**2, axis=1))
    order = np.lexsort((np.asarray(weights), norms))
    ordered_points = points[jnp.asarray(order)]
    ordered_weights = weights[jnp.asarray(order)]
    keys = jax.random.split(jax.random.PRNGKey(config.seed), config.n_init)
    runs = [_single_kmeans(ordered_points, ordered_weights, n_bins, config, key) for key in keys]
    return min(runs, key=lambda run: run.objective_history[-1])


def scalar_weighted_kmeans_dp(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    config: ScalarDPConfig,
) -> QuantizerRun:
    """Solve one-dimensional weighted interval k-means exactly by dynamic programming."""
    if points.ndim != 2 or points.shape[1] != 1:
        raise ValueError("ScalarDPConfig requires exactly one informative score direction")
    n_rows = points.shape[0]
    if n_rows > config.max_rows:
        raise ValueError(
            f"scalar dynamic programming received {n_rows} distinct rows, "
            f"exceeding max_rows={config.max_rows}"
        )
    order = np.argsort(np.asarray(points[:, 0]), kind="stable")
    values = np.asarray(points[order, 0], dtype=np.float64)
    ordered_weights = np.asarray(weights[order], dtype=np.float64)
    prefix_weight = np.r_[0.0, np.cumsum(ordered_weights)]
    prefix_sum = np.r_[0.0, np.cumsum(ordered_weights * values)]
    prefix_square = np.r_[0.0, np.cumsum(ordered_weights * values**2)]
    dynamic = np.full((n_bins + 1, n_rows + 1), np.inf)
    predecessor = np.full((n_bins + 1, n_rows + 1), -1, dtype=np.int32)
    dynamic[0, 0] = 0.0
    for bin_count in range(1, n_bins + 1):
        for stop in range(bin_count, n_rows + 1):
            starts = np.arange(bin_count - 1, stop)
            segment_weight = prefix_weight[stop] - prefix_weight[starts]
            segment_sum = prefix_sum[stop] - prefix_sum[starts]
            segment_square = prefix_square[stop] - prefix_square[starts]
            costs = segment_square - segment_sum**2 / segment_weight
            candidates = dynamic[bin_count - 1, starts] + costs
            selected = int(np.argmin(candidates))
            dynamic[bin_count, stop] = candidates[selected]
            predecessor[bin_count, stop] = starts[selected]
    ordered_labels = np.empty(n_rows, dtype=np.int32)
    stop = n_rows
    for label in range(n_bins - 1, -1, -1):
        start = int(predecessor[label + 1, stop])
        ordered_labels[start:stop] = label
        stop = start
    labels = np.empty(n_rows, dtype=np.int32)
    labels[order] = ordered_labels
    label_array = jnp.asarray(labels)
    bin_weights = _bin_weights(label_array, weights, n_bins)
    sums = jnp.zeros((n_bins, 1), dtype=points.dtype)
    sums = sums.at[label_array].add(weights[:, None] * points)
    centers = sums / bin_weights[:, None]
    objective = float(dynamic[n_bins, n_rows])
    return QuantizerRun(
        centers=centers,
        steps=[0],
        center_history=[centers],
        objective_history=[objective],
        bin_weight_history=[bin_weights],
    )


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


def _soft_initial_centers(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    config: SoftVoronoiConfig,
) -> jnp.ndarray:
    initializer_config = KMeansConfig(
        whiten=config.whiten,
        rank_rtol=config.rank_rtol,
        seed=config.seed,
        n_init=config.n_init,
        max_iter=config.kmeans_max_iter,
        tolerance=config.tolerance,
        record_every=config.kmeans_max_iter,
    )
    return weighted_kmeans(points, weights, n_bins, initializer_config).centers


def _soft_temperature_bounds(
    centers: jnp.ndarray,
    end_ratio: float,
) -> tuple[float, float]:
    n_bins = centers.shape[0]
    center_distances = squared_distances(centers, centers)
    center_distances = jnp.where(jnp.eye(n_bins, dtype=bool), jnp.inf, center_distances)
    nearest_separations = jnp.sqrt(jnp.min(center_distances, axis=1))
    start = float(np.asarray(jnp.median(nearest_separations)))
    if not np.isfinite(start) or start <= 0:
        raise ValueError("soft optimization requires distinct initial centers")
    return start, start * end_ratio


def _criterion_logdet(
    fisher: jnp.ndarray, criterion: DOptimality | ProfiledDOptimality
) -> tuple[jnp.ndarray, jnp.ndarray, int]:
    if isinstance(criterion, DOptimality):
        sign, value = jnp.linalg.slogdet(fisher)
        return sign, value, fisher.shape[0]
    dimension = fisher.shape[0]
    interest_set = set(criterion.interest)
    nuisance = tuple(index for index in range(dimension) if index not in interest_set)
    interest_indices = jnp.asarray(criterion.interest)
    nuisance_indices = jnp.asarray(nuisance)
    interest_block = fisher[jnp.ix_(interest_indices, interest_indices)]
    cross_block = fisher[jnp.ix_(interest_indices, nuisance_indices)]
    nuisance_block = fisher[jnp.ix_(nuisance_indices, nuisance_indices)]
    nuisance_sign, _ = jnp.linalg.slogdet(nuisance_block)
    schur = interest_block - cross_block @ jnp.linalg.solve(nuisance_block, cross_block.T)
    schur_sign, value = jnp.linalg.slogdet(0.5 * (schur + schur.T))
    return nuisance_sign * schur_sign, value, len(criterion.interest)


@dataclass(slots=True)
class _SoftHistory:
    points: jnp.ndarray
    weights: jnp.ndarray
    objective_scores: jnp.ndarray
    n_bins: int
    criterion: DOptimality | ProfiledDOptimality
    reference_objective: float
    objective_dimension: int
    steps: list[int] = field(default_factory=list)
    centers: list[jnp.ndarray] = field(default_factory=list)
    objectives: list[float] = field(default_factory=list)
    bin_weights: list[jnp.ndarray] = field(default_factory=list)
    retentions: list[float] = field(default_factory=list)
    temperatures: list[float] = field(default_factory=list)
    gradient_norms: list[float] = field(default_factory=list)

    def append(
        self,
        *,
        step: int,
        centers: jnp.ndarray,
        loss: jnp.ndarray,
        temperature: float,
        gradient_norm: jnp.ndarray,
    ) -> None:
        """Record one aggregate soft-optimization checkpoint."""
        responsibilities = soft_responsibilities(self.points, centers, temperature)
        soft_fisher = _soft_fisher(self.objective_scores, responsibilities, self.weights)
        labels = hard_assign(self.points, centers)
        self.steps.append(step)
        self.centers.append(centers)
        self.objectives.append(float(np.asarray(-loss)))
        self.bin_weights.append(_bin_weights(labels, self.weights, self.n_bins))
        sign, value, _ = _criterion_logdet(soft_fisher, self.criterion)
        retention = jnp.where(
            sign > 0,
            jnp.exp((value - self.reference_objective) / self.objective_dimension),
            0.0,
        )
        self.retentions.append(float(np.asarray(retention)))
        self.temperatures.append(float(temperature))
        self.gradient_norms.append(float(np.asarray(gradient_norm)))

    def finish(self, centers: jnp.ndarray) -> QuantizerRun:
        """Build the common quantizer result from recorded checkpoints."""
        return QuantizerRun(
            centers=centers,
            steps=self.steps,
            center_history=self.centers,
            objective_history=self.objectives,
            bin_weight_history=self.bin_weights,
            soft_retention_history=self.retentions,
            temperature_history=self.temperatures,
            gradient_norm_history=self.gradient_norms,
        )


def soft_voronoi(
    points: jnp.ndarray,
    objective_scores: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    effective_rank: int,
    criterion: DOptimality | ProfiledDOptimality,
    config: SoftVoronoiConfig,
) -> QuantizerRun:
    """Optimize soft Fisher retention, then return centers for hard assignment."""
    if n_bins < effective_rank:
        raise ValueError(
            "soft D-optimal fitting requires n_bins >= the effective Fisher rank; "
            "use k-means for smaller partitions"
        )
    centers = _soft_initial_centers(points, weights, n_bins, config)
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

    start_temperature, end_temperature = _soft_temperature_bounds(
        centers, config.temperature_end_ratio
    )
    if isinstance(criterion, DOptimality):
        objective_scores = _normalized_objective_scores(objective_scores, weights, config.rank_rtol)
    elif objective_scores.shape[1] != effective_rank:
        raise ValueError("profiled-D soft fitting requires full-rank supplied-score information")
    full_fisher = jnp.einsum("n,np,nq->pq", weights, objective_scores, objective_scores)
    reference_sign, reference_value, objective_dimension = _criterion_logdet(full_fisher, criterion)
    if float(np.asarray(reference_sign)) <= 0:
        raise ValueError("soft fitting requires nonsingular criterion information")
    reference_objective = float(np.asarray(reference_value))

    def loss_fn(current_centers: jnp.ndarray, temperature: jnp.ndarray) -> jnp.ndarray:
        resp = soft_responsibilities(points, current_centers, temperature)
        soft_fisher = _soft_fisher(objective_scores, resp, weights)
        sign, logdet, _ = _criterion_logdet(soft_fisher, criterion)
        return jnp.where(sign > 0, -logdet, jnp.inf)

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
            jnp.asarray(optax.apply_updates(current_centers, updates)),
            optimizer_state,
            jnp.asarray(loss),
            jnp.asarray(optax.tree.norm(gradients)),
        )

    history = _SoftHistory(
        points,
        weights,
        objective_scores,
        n_bins,
        criterion,
        reference_objective,
        objective_dimension,
    )

    for step in range(config.max_steps + 1):
        fraction = step / config.max_steps
        temperature = start_temperature * (end_temperature / start_temperature) ** fraction
        if step > 0:
            centers, state, loss, gradient_norm = update(centers, state, jnp.asarray(temperature))
        else:
            loss = loss_fn(centers, jnp.asarray(temperature))
            gradient_norm = jnp.asarray(0.0, dtype=points.dtype)
        if step % config.record_every == 0 or step == config.max_steps:
            history.append(
                step=step,
                centers=centers,
                loss=loss,
                temperature=temperature,
                gradient_norm=gradient_norm,
            )

    return history.finish(centers)
