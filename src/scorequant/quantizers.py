"""Private JAX implementations of ScoreQuant geometric quantizers."""

from __future__ import annotations

from dataclasses import dataclass, field

import jax
import jax.numpy as jnp
import numpy as np
import optax

from ._binstats import scatter_bin_statistics
from .config import KMeansConfig, ScalarDPConfig, SoftVoronoiConfig
from .criteria import DOptimality, ProfiledDOptimality
from .transforms import fisher_transform

# One dynamic-programming stripe materializes this many [stripe, n_states]
# temporaries, and the whole stripe set is held inside the byte budget.
_DYNAMIC_STRIPE_TEMPORARIES = 8
_DYNAMIC_WORKING_SET_BYTES = 64 * 1024 * 1024


@dataclass(slots=True)
class QuantizerRun:
    """Aggregate state returned by a private quantizer implementation.

    ``objective_label`` names the units of ``objective_history`` so that a
    reported trace is never read in the wrong convention: a within-segment
    squared error and a log determinant are both scalars but not comparable.
    """

    centers: jnp.ndarray
    steps: list[int]
    center_history: list[jnp.ndarray]
    objective_history: list[float]
    bin_weight_history: list[jnp.ndarray]
    objective_label: str = "whitened_sse"
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
        statistics = scatter_bin_statistics(labels, weights, points, n_bins)
        occupancies, proposed = statistics.weights, statistics.means

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
        objective_label="whitened_sse",
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


def _dynamic_stripe_rows(n_states: int, item_size: int) -> int:
    """Return how many dynamic-programming stops one memory-bounded stripe holds.

    One stripe materializes a handful of ``[stripe, n_states]`` prefix-difference
    blocks, so the budget is divided by that temporary count rather than by one.
    """
    per_row = item_size * n_states * _DYNAMIC_STRIPE_TEMPORARIES
    return max(1, min(n_states, _DYNAMIC_WORKING_SET_BYTES // max(per_row, 1)))


def scalar_interval_dp(
    values: np.ndarray, weights: np.ndarray, n_bins: int
) -> tuple[np.ndarray, float]:
    """Solve exact one-dimensional weighted interval k-means by dynamic programming.

    On a scalar score law an optimal hard partition has ordered interval cells,
    so the global optimum is the minimal total weighted within-segment squared
    error over ``n_bins`` consecutive segments of the sorted values. Prefix sums
    turn every segment cost into a constant-time expression, and each dynamic
    stage evaluates whole blocks of stop/split pairs at once, so the quadratic
    recursion runs in a handful of memory-bounded stripes instead of one Python
    iteration per stop.

    Parameters
    ----------
    values
        Finite scalar coordinates with shape ``[N]``.
    weights
        Finite nonnegative weights with shape ``[N]``.
    n_bins
        Number of requested interval cells.

    Returns
    -------
    tuple
        Integer labels aligned with ``values`` and the minimal weighted
        within-segment squared error.
    """
    n_rows = int(values.shape[0])
    if n_bins > n_rows:
        raise ValueError("scalar dynamic programming requires n_bins <= the number of atoms")
    order = np.argsort(values, kind="stable")
    ordered_values = values[order]
    ordered_weights = weights[order]
    prefix_weight = np.r_[0.0, np.cumsum(ordered_weights)]
    prefix_sum = np.r_[0.0, np.cumsum(ordered_weights * ordered_values)]
    prefix_square = np.r_[0.0, np.cumsum(ordered_weights * ordered_values**2)]
    # ``previous`` is the completed stage of the recursion; only one stage and
    # the predecessor table are retained, so storage stays O(n_bins * n_rows).
    previous = np.full(n_rows + 1, np.inf)
    previous[0] = 0.0
    predecessor = np.zeros((n_bins + 1, n_rows + 1), dtype=np.int32)
    stripe = _dynamic_stripe_rows(n_rows + 1, prefix_weight.dtype.itemsize)
    for bin_count in range(1, n_bins + 1):
        current = np.full(n_rows + 1, np.inf)
        first_start = bin_count - 1
        for begin in range(bin_count, n_rows + 1, stripe):
            end = min(begin + stripe, n_rows + 1)
            stops = np.arange(begin, end)
            # A stop of ``end - 1`` admits no split point beyond ``end - 2``, so
            # the block is cut to the columns this stripe can actually use.
            columns = np.arange(first_start, end - 1)
            admissible = columns[None, :] < stops[:, None]
            segment_weight = prefix_weight[stops, None] - prefix_weight[None, columns]
            segment_sum = prefix_sum[stops, None] - prefix_sum[None, columns]
            segment_square = prefix_square[stops, None] - prefix_square[None, columns]
            # A zero-weight segment carries no measure, so its exact cost is
            # zero; the substituted denominator only avoids a spurious divide.
            safe_weight = np.where(segment_weight > 0, segment_weight, 1.0)
            costs = segment_square - segment_sum**2 / safe_weight
            candidates = np.where(admissible, previous[None, columns] + costs, np.inf)
            selected = np.argmin(candidates, axis=1)
            current[begin:end] = candidates[np.arange(end - begin), selected]
            predecessor[bin_count, begin:end] = first_start + selected
        previous = current
    objective = float(previous[n_rows])
    if not np.isfinite(objective):
        raise ValueError("scalar dynamic programming found no feasible interval partition")
    ordered_labels = np.empty(n_rows, dtype=np.int32)
    stop = n_rows
    for label in range(n_bins - 1, -1, -1):
        start = int(predecessor[label + 1, stop])
        ordered_labels[start:stop] = label
        stop = start
    labels = np.empty(n_rows, dtype=np.int32)
    labels[order] = ordered_labels
    return labels, objective


def scalar_weighted_kmeans_dp(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    config: ScalarDPConfig,
) -> QuantizerRun:
    """Solve one-dimensional weighted interval k-means exactly by dynamic programming."""
    rank = int(points.shape[1]) if points.ndim == 2 else 0
    if rank != 1:
        raise ValueError(
            "scalar dynamic programming requires an effective score rank of one, got "
            f"rank {rank}; reduce the score dimension or choose another solver"
        )
    n_rows = int(points.shape[0])
    if n_rows > config.max_rows:
        raise ValueError(
            f"scalar dynamic programming received {n_rows} distinct rows, "
            f"exceeding max_rows={config.max_rows}"
        )
    labels, objective = scalar_interval_dp(
        np.asarray(points[:, 0], dtype=np.float64),
        np.asarray(weights, dtype=np.float64),
        n_bins,
    )
    label_array = jnp.asarray(labels)
    statistics = scatter_bin_statistics(label_array, weights, points, n_bins)
    centers = statistics.means
    return QuantizerRun(
        centers=centers,
        steps=[0],
        center_history=[centers],
        objective_history=[objective],
        bin_weight_history=[statistics.weights],
        objective_label="whitened_sse",
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


def criterion_objective_label(criterion: DOptimality | ProfiledDOptimality) -> str:
    """Name the units of a log-determinant objective recorded for one criterion."""
    return "profiled_logdet" if isinstance(criterion, ProfiledDOptimality) else "logdet_retained"


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
            objective_label=criterion_objective_label(self.criterion),
            soft_retention_history=self.retentions,
            temperature_history=self.temperatures,
            gradient_norm_history=self.gradient_norms,
        )


def _soft_voronoi_single_cell(
    centers: jnp.ndarray, weights: jnp.ndarray, criterion: DOptimality | ProfiledDOptimality
) -> QuantizerRun:
    """Return the degenerate one-cell run: every row already shares the only center."""
    return QuantizerRun(
        centers=centers,
        steps=[0],
        center_history=[centers],
        objective_history=[0.0],
        bin_weight_history=[jnp.asarray([jnp.sum(weights)])],
        objective_label=criterion_objective_label(criterion),
        soft_retention_history=[1.0],
        temperature_history=[1.0],
        gradient_norm_history=[0.0],
    )


def _soft_voronoi_reference(
    objective_scores: jnp.ndarray,
    weights: jnp.ndarray,
    criterion: DOptimality | ProfiledDOptimality,
    *,
    effective_rank: int,
    rank_rtol: float | None,
) -> tuple[jnp.ndarray, float, int]:
    """Normalize D-optimal objective scores and check the full-data reference is regular."""
    if isinstance(criterion, DOptimality):
        objective_scores = _normalized_objective_scores(objective_scores, weights, rank_rtol)
    elif objective_scores.shape[1] != effective_rank:
        raise ValueError("profiled-D soft fitting requires full-rank supplied-score information")
    full_fisher = jnp.einsum("n,np,nq->pq", weights, objective_scores, objective_scores)
    reference_sign, reference_value, objective_dimension = _criterion_logdet(full_fisher, criterion)
    if float(np.asarray(reference_sign)) <= 0:
        raise ValueError("soft fitting requires nonsingular criterion information")
    return objective_scores, float(np.asarray(reference_value)), objective_dimension


def _soft_voronoi_optimizer(
    config: SoftVoronoiConfig, start_temperature: float
) -> optax.GradientTransformation:
    """Build the scale-invariant Adam chain for one soft-Voronoi fit.

    Fisher whitening contains the total information scale, so coordinate
    magnitudes shrink as total sample weight grows. Expressing Adam's step in
    units of the initialized center separation keeps fitting scale-invariant.
    """
    return optax.chain(
        optax.clip_by_global_norm(config.gradient_clip),
        optax.adam(config.learning_rate * start_temperature),
    )


def _run_soft_schedule(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    objective_scores: jnp.ndarray,
    n_bins: int,
    criterion: DOptimality | ProfiledDOptimality,
    config: SoftVoronoiConfig,
    *,
    centers: jnp.ndarray,
    optimizer: optax.GradientTransformation,
    start_temperature: float,
    end_temperature: float,
    reference_objective: float,
    objective_dimension: int,
) -> QuantizerRun:
    """Run the annealed Adam schedule from prepared centers and return its history."""

    def loss_fn(current_centers: jnp.ndarray, temperature: jnp.ndarray) -> jnp.ndarray:
        resp = soft_responsibilities(points, current_centers, temperature)
        soft_fisher = _soft_fisher(objective_scores, resp, weights)
        sign, logdet, _ = _criterion_logdet(soft_fisher, criterion)
        return jnp.where(sign > 0, -logdet, jnp.inf)

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
        return _soft_voronoi_single_cell(centers, weights, criterion)

    start_temperature, end_temperature = _soft_temperature_bounds(
        centers, config.temperature_end_ratio
    )
    objective_scores, reference_objective, objective_dimension = _soft_voronoi_reference(
        objective_scores,
        weights,
        criterion,
        effective_rank=effective_rank,
        rank_rtol=config.rank_rtol,
    )
    optimizer = _soft_voronoi_optimizer(config, start_temperature)
    return _run_soft_schedule(
        points,
        weights,
        objective_scores,
        n_bins,
        criterion,
        config,
        centers=centers,
        optimizer=optimizer,
        start_temperature=start_temperature,
        end_temperature=end_temperature,
        reference_objective=reference_objective,
        objective_dimension=objective_dimension,
    )
