"""Classifier-to-score bridge for the FAIR Universe HiggsML showcase.

Two classifiers, two different ratio doors:

* a signal-vs-background classifier feeds `scorequant.DensityRatioScore` under
  `scorequant.IntensityParameterization`, giving the two rate columns
  (`mu_htautau`, `nu_background`) in closed form once the ratio is known;
* a `tes`-minus-vs-plus classifier feeds `scorequant.CentralLogRatioScore`,
  the library's central-difference door, giving the one nuisance-shape
  column (`tes`) that has no closed form.

Both classifiers are cross-fitted out-of-fold with **one fold id per event**,
reused by every `tes` copy of that event (D9/F1): a plain per-row split lets
the `tes` classifier memorize an event from its eighteen `tes`-inert columns
and invert the label. Both are trained with **per-class normalized weights**
and declared training priors `(0.5, 0.5)` (D9/F2): the raw Monte Carlo
weights make the signal class statistically invisible (weighted fraction
~0.001), so the physical rate ratio enters through
`IntensityParameterization` coefficients instead, never through the priors.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

import scorequant as sq

from .data import HepData

#: The three score columns every labeling in this example is reported
#: against, in the order the composed provider emits them.
SCHEMA = sq.ScoreSchema(("mu_htautau", "nu_background", "tes"))
#: `mu_htautau` is the sole parameter of interest for every profiled-D_s call.
INTEREST = SCHEMA.select("mu_htautau")

#: A calibrated posterior within this of 0.5 counts as "not separated" for
#: the `tes` near-boundary diagnostic D4 asks for.
NEAR_HALF_TOLERANCE = 0.01


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values, axis=1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / np.sum(exponentials, axis=1, keepdims=True)


def _temperature_scale(probabilities: np.ndarray, temperature: float) -> np.ndarray:
    clipped = np.clip(probabilities, 1e-12, 1.0)
    return _softmax(np.log(clipped) / temperature)


def _weighted_log_loss(
    probabilities: np.ndarray, labels: np.ndarray, weights: np.ndarray, temperature: float
) -> float:
    calibrated = _temperature_scale(probabilities, temperature)
    losses = -np.log(np.clip(calibrated[np.arange(len(labels)), labels], 1e-12, 1.0))
    return float(np.average(losses, weights=weights))


def _fit_temperature(probabilities: np.ndarray, labels: np.ndarray, weights: np.ndarray) -> float:
    """Minimize weighted binary log loss with a deterministic golden-section search.

    Mirrors the calibration bridge in `examples/cell_population/scores.py`
    (D8), simplified to a flat weight vector: this example has no patient
    grouping to balance across.
    """
    left, right = np.log(0.25), np.log(4.0)
    golden = (np.sqrt(5.0) - 1.0) / 2.0
    x1 = right - golden * (right - left)
    x2 = left + golden * (right - left)
    f1 = _weighted_log_loss(probabilities, labels, weights, float(np.exp(x1)))
    f2 = _weighted_log_loss(probabilities, labels, weights, float(np.exp(x2)))
    for _ in range(48):
        if f1 <= f2:
            right, x2, f2 = x2, x1, f1
            x1 = right - golden * (right - left)
            f1 = _weighted_log_loss(probabilities, labels, weights, float(np.exp(x1)))
        else:
            left, x1, f1 = x1, x2, f2
            x2 = left + golden * (right - left)
            f2 = _weighted_log_loss(probabilities, labels, weights, float(np.exp(x2)))
    return float(np.exp((left + right) / 2.0))


def _balanced_class_weights(labels: np.ndarray, raw_weights: np.ndarray) -> np.ndarray:
    """Normalize raw weights so each of the two classes carries mass 0.5.

    Without this, the raw Monte Carlo weights make the signal class
    statistically invisible to the classifier (D9/F2): background events
    carry weight ~1582, signal ~3, so the weighted signal fraction is
    ~0.001.
    """
    weights = np.zeros_like(raw_weights)
    for label in (0, 1):
        mask = labels == label
        total = float(raw_weights[mask].sum())
        if total <= 0:
            raise ValueError(f"class {label} has no positive weight")
        weights[mask] = raw_weights[mask] * (0.5 / total)
    return weights


def event_folds(is_signal: np.ndarray, *, n_folds: int, seed: int) -> np.ndarray:
    """Assign one deterministic fold id per event, stratified by signal label.

    Both classifiers reuse this same per-event assignment (D9/F1): the `tes`
    minus and plus copies of one event always share its fold id, so a fold
    boundary never separates an event from its own paired variant.

    Parameters
    ----------
    is_signal
        Boolean signal label per event, shape ``[N]``.
    n_folds
        Number of stratified folds.
    seed
        Deterministic shuffle seed.

    Returns
    -------
    numpy.ndarray
        Integer fold id per event, shape ``[N]``, values in ``[0, n_folds)``.
    """
    splitter = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    fold_ids = np.full(is_signal.shape[0], -1, dtype=np.int64)
    dummy_features = np.zeros((is_signal.shape[0], 1))
    for fold_index, (_, held_out) in enumerate(splitter.split(dummy_features, is_signal)):
        fold_ids[held_out] = fold_index
    if np.any(fold_ids < 0):
        raise ValueError("every event must receive a fold id")
    return fold_ids


def _fit_signal_background_classifier(
    features: np.ndarray,
    is_signal: np.ndarray,
    raw_weights: np.ndarray,
    *,
    max_iter: int,
    seed: int,
) -> HistGradientBoostingClassifier:
    labels = is_signal.astype(np.int64)
    weights = _balanced_class_weights(labels, raw_weights)
    classifier = HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_iter=max_iter,
        max_leaf_nodes=31,
        l2_regularization=1e-3,
        early_stopping=False,
        random_state=seed,
    )
    classifier.fit(features, labels, sample_weight=weights)
    if tuple(int(value) for value in classifier.classes_) != (0, 1):
        raise ValueError("signal/background classifier must see both classes")
    return classifier


def _fit_tes_classifier(
    minus_features: np.ndarray, plus_features: np.ndarray, *, max_iter: int, seed: int
) -> HistGradientBoostingClassifier:
    features = np.concatenate([minus_features, plus_features], axis=0)
    labels = np.concatenate(
        [np.zeros(len(minus_features), dtype=np.int64), np.ones(len(plus_features), dtype=np.int64)]
    )
    classifier = HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_iter=max_iter,
        max_leaf_nodes=31,
        l2_regularization=1e-3,
        early_stopping=False,
        random_state=seed,
    )
    # Uniform weights: the minus and plus copies are balanced 1:1 by
    # construction, and the target is the tes deformation itself, not a
    # physics rate, so no class-balancing correction is needed here.
    classifier.fit(features, labels)
    if tuple(int(value) for value in classifier.classes_) != (0, 1):
        raise ValueError("tes classifier must see both the minus and plus classes")
    return classifier


@dataclass(frozen=True, slots=True)
class SignalBackgroundOOF:
    """Out-of-fold calibrated signal/background posteriors and diagnostics.

    Attributes
    ----------
    probabilities
        Calibrated out-of-fold posteriors, shape ``[N, 2]``, columns
        ``[background, signal]`` (classifier class order 0, 1).
    temperature
        Fitted temperature-scaling scalar.
    signal_fraction
        Weighted signal fraction using the raw Monte Carlo weights -- the
        physical rate that feeds `IntensityParameterization` coefficients.
    weighted_auc
        Out-of-fold AUC of the calibrated signal posterior, weighted by the
        raw Monte Carlo event weights.
    """

    probabilities: np.ndarray
    temperature: float
    signal_fraction: float
    weighted_auc: float


def fit_signal_background_oof(
    data: HepData, *, fold_ids: np.ndarray, max_iter: int, seed: int
) -> SignalBackgroundOOF:
    """Cross-fit the signal/background classifier out-of-fold on nominal features.

    Parameters
    ----------
    data
        The loaded fixture.
    fold_ids
        Per-event fold assignment from `event_folds`.
    max_iter
        Boosting round budget per fold's classifier.
    seed
        Base seed; fold ``k`` uses ``seed + k``.

    Returns
    -------
    SignalBackgroundOOF
        Calibrated out-of-fold posteriors and the diagnostics D9/F2 reports.
    """
    features = data.features_at(1.0)
    labels = data.is_signal.astype(np.int64)
    raw_oof = np.full((data.n_events, 2), np.nan)
    for fold in np.unique(fold_ids):
        train_mask = fold_ids != fold
        held_mask = fold_ids == fold
        classifier = _fit_signal_background_classifier(
            features[train_mask],
            data.is_signal[train_mask],
            data.weights[train_mask],
            max_iter=max_iter,
            seed=seed + int(fold),
        )
        raw_oof[held_mask] = classifier.predict_proba(features[held_mask])
    if not np.isfinite(raw_oof).all():
        raise ValueError("every event must receive an out-of-fold signal/background prediction")
    temperature = _fit_temperature(raw_oof, labels, _balanced_class_weights(labels, data.weights))
    calibrated = _temperature_scale(raw_oof, temperature)
    signal_fraction = float(np.sum(data.weights[data.is_signal]) / np.sum(data.weights))
    weighted_auc = float(roc_auc_score(labels, calibrated[:, 1], sample_weight=data.weights))
    return SignalBackgroundOOF(calibrated, temperature, signal_fraction, weighted_auc)


@dataclass(frozen=True, slots=True)
class TesOOF:
    """Out-of-fold calibrated `tes` posteriors, evaluated at nominal features.

    Attributes
    ----------
    delta
        The finite-difference half-offset used to build the minus/plus pair.
    probabilities
        Calibrated posteriors evaluated at each event's *nominal* (`tes=1`)
        features, shape ``[N, 2]``, columns ``[minus, plus]``. There is no
        ground-truth label at the nominal point; the calibration temperature
        is fit on the genuine minus/plus classification task and then
        applied here.
    temperature
        Fitted temperature-scaling scalar.
    minus_plus_auc
        Out-of-fold AUC of the minus/plus classification task itself
        (unweighted; the pairing is already balanced 1:1 by construction).
    near_half_fraction
        Fraction of events whose nominal-point calibrated posterior falls
        within `NEAR_HALF_TOLERANCE` of 0.5 -- D4's noise diagnostic.
    """

    delta: float
    probabilities: np.ndarray
    temperature: float
    minus_plus_auc: float
    near_half_fraction: float


def fit_tes_oof(
    data: HepData, *, delta: float, fold_ids: np.ndarray, max_iter: int, seed: int
) -> TesOOF:
    """Cross-fit the `tes` minus/plus classifier out-of-fold, grouped by event.

    Parameters
    ----------
    data
        The loaded fixture.
    delta
        Finite-difference half-offset; ``1 - delta`` and ``1 + delta`` must
        both be committed `tes` points.
    fold_ids
        Per-event fold assignment from `event_folds`, reused for both the
        minus and plus copy of every event (D9/F1).
    max_iter
        Boosting round budget per fold's classifier.
    seed
        Base seed; fold ``k`` uses ``seed + k``.

    Returns
    -------
    TesOOF
        Calibrated nominal-point posteriors and the diagnostics D4 asks for.
    """
    nominal = data.features_at(1.0)
    minus = data.features_at(round(1.0 - delta, 4))
    plus = data.features_at(round(1.0 + delta, 4))
    raw_oof = np.full((data.n_events, 2), np.nan)
    pooled_probabilities: list[np.ndarray] = []
    pooled_labels: list[np.ndarray] = []
    for fold in np.unique(fold_ids):
        train_mask = fold_ids != fold
        held_mask = fold_ids == fold
        classifier = _fit_tes_classifier(
            minus[train_mask], plus[train_mask], max_iter=max_iter, seed=seed + int(fold)
        )
        raw_oof[held_mask] = classifier.predict_proba(nominal[held_mask])
        held_count = int(np.count_nonzero(held_mask))
        pooled_probabilities.append(classifier.predict_proba(minus[held_mask]))
        pooled_probabilities.append(classifier.predict_proba(plus[held_mask]))
        pooled_labels.append(np.zeros(held_count, dtype=np.int64))
        pooled_labels.append(np.ones(held_count, dtype=np.int64))
    if not np.isfinite(raw_oof).all():
        raise ValueError("every event must receive an out-of-fold tes prediction")
    task_probabilities = np.concatenate(pooled_probabilities, axis=0)
    task_labels = np.concatenate(pooled_labels, axis=0)
    temperature = _fit_temperature(task_probabilities, task_labels, np.ones(task_labels.shape[0]))
    calibrated_nominal = _temperature_scale(raw_oof, temperature)
    minus_plus_auc = float(roc_auc_score(task_labels, task_probabilities[:, 1]))
    near_half_fraction = float(
        np.mean(np.abs(calibrated_nominal[:, 1] - 0.5) < NEAR_HALF_TOLERANCE)
    )
    return TesOOF(delta, calibrated_nominal, temperature, minus_plus_auc, near_half_fraction)


def assemble_score_sample(data: HepData, sigbg: SignalBackgroundOOF, tes: TesOOF) -> sq.ScoreSample:
    """Combine out-of-fold posteriors into the three-column `ScoreSample`.

    This is the leakage-free score table the finite study runs on: every
    column is a fold-cross-fitted prediction, never a model evaluated on the
    event it was trained on.

    Parameters
    ----------
    data
        The loaded fixture.
    sigbg
        Out-of-fold signal/background posteriors from `fit_signal_background_oof`.
    tes
        Out-of-fold `tes` posteriors from `fit_tes_oof`, at the matching `delta`.

    Returns
    -------
    scorequant.ScoreSample
        Weighted score table with `SCHEMA` and `kind="estimated_ratio"`
        provenance.
    """
    nominal = data.features_at(1.0)
    rate_provider = sq.DensityRatioScore.from_classifier(
        lambda observations: sigbg.probabilities,
        [0.5, 0.5],
        sq.IntensityParameterization([1.0 - sigbg.signal_fraction, sigbg.signal_fraction]),
        calibration="temperature",
        description="signal-vs-background classifier, out-of-fold",
    )
    tes_provider = sq.CentralLogRatioScore(
        lambda observations: tes.probabilities,
        deltas=[tes.delta],
        class_priors=[0.5, 0.5],
        description="tes minus/plus classifier, out-of-fold",
    )
    rate_scores = np.asarray(rate_provider.score(nominal))  # columns [background, signal]
    tes_scores = np.asarray(tes_provider.score(nominal))  # one column
    scores = np.concatenate([rate_scores[:, [1, 0]], tes_scores], axis=1)
    provenance = sq.ScoreProvenance(
        kind="estimated_ratio",
        description="Out-of-fold classifier scores, FAIR Universe HiggsML fixture",
        metadata={
            "delta": tes.delta,
            "signal_fraction": sigbg.signal_fraction,
            "signal_weighted_auc": sigbg.weighted_auc,
            "tes_minus_plus_auc": tes.minus_plus_auc,
        },
    )
    return sq.ScoreSample(scores, data.weights, schema=SCHEMA, provenance=provenance)


@dataclass(frozen=True, slots=True)
class HepScoreProvider:
    """Compose the signal-rate and `tes`-nuisance halves into one `ScoreProvider`.

    Implements the open `scorequant.ScoreProvider` protocol directly -- see
    its docstring in `src/scorequant/providers.py` -- rather than subclassing
    a built-in: the two halves go through different ratio doors (D2) and only
    their concatenated output is a valid three-column ScoreQuant score table.
    """

    rate: sq.DensityRatioScore
    tes: sq.CentralLogRatioScore
    provenance: sq.ScoreProvenance
    schema: sq.ScoreSchema = SCHEMA

    def score(self, observations: np.ndarray) -> np.ndarray:
        """Map raw 28-feature observation rows to the three declared score columns."""
        rate_scores = np.asarray(self.rate.score(observations))  # columns [background, signal]
        tes_scores = np.asarray(self.tes.score(observations))  # one column
        return np.concatenate([rate_scores[:, [1, 0]], tes_scores], axis=1)


def fit_final_provider(
    data: HepData, *, delta: float, max_iter: int, seed: int
) -> HepScoreProvider:
    """Fit both classifiers on every event, for use as a reusable rule.

    Unlike `assemble_score_sample`'s out-of-fold scores, this provider is
    meant to be applied to new observations -- the deliverable
    `fit_quantizer`'s reusable rule needs (D8: "the classifier is trained
    inside the example"). Scoring it back on its own training fixture is
    therefore in-sample, unlike the leakage-free finite-partition study.

    Parameters
    ----------
    data
        The loaded fixture.
    delta
        Finite-difference half-offset for the `tes` classifier.
    max_iter
        Boosting round budget for each final classifier.
    seed
        Deterministic seed; the `tes` classifier uses ``seed + 1``.

    Returns
    -------
    HepScoreProvider
        A provider whose `score` calls the two full-sample classifiers.
    """
    features = data.features_at(1.0)
    minus = data.features_at(round(1.0 - delta, 4))
    plus = data.features_at(round(1.0 + delta, 4))

    signal_classifier = _fit_signal_background_classifier(
        features, data.is_signal, data.weights, max_iter=max_iter, seed=seed
    )
    tes_classifier = _fit_tes_classifier(minus, plus, max_iter=max_iter, seed=seed + 1)

    signal_fraction = float(np.sum(data.weights[data.is_signal]) / np.sum(data.weights))
    signal_labels = data.is_signal.astype(np.int64)
    signal_temperature = _fit_temperature(
        signal_classifier.predict_proba(features),
        signal_labels,
        _balanced_class_weights(signal_labels, data.weights),
    )
    minus_plus_features = np.concatenate([minus, plus], axis=0)
    minus_plus_labels = np.concatenate(
        [np.zeros(data.n_events, dtype=np.int64), np.ones(data.n_events, dtype=np.int64)]
    )
    tes_temperature = _fit_temperature(
        tes_classifier.predict_proba(minus_plus_features),
        minus_plus_labels,
        np.ones(minus_plus_labels.shape[0]),
    )

    def predict_rate(observations: np.ndarray) -> np.ndarray:
        return _temperature_scale(
            signal_classifier.predict_proba(np.asarray(observations)), signal_temperature
        )

    def predict_tes(observations: np.ndarray) -> np.ndarray:
        return _temperature_scale(
            tes_classifier.predict_proba(np.asarray(observations)), tes_temperature
        )

    rate_provider = sq.DensityRatioScore.from_classifier(
        predict_rate,
        [0.5, 0.5],
        sq.IntensityParameterization([1.0 - signal_fraction, signal_fraction]),
        calibration="temperature",
        description="signal-vs-background classifier, full-sample fit",
    )
    tes_provider = sq.CentralLogRatioScore(
        predict_tes,
        deltas=[delta],
        class_priors=[0.5, 0.5],
        description="tes minus/plus classifier, full-sample fit",
    )
    provenance = sq.ScoreProvenance(
        kind="estimated_ratio",
        description="Reusable HEP classifier-to-score rule",
        metadata={"delta": delta, "signal_fraction": signal_fraction},
    )
    return HepScoreProvider(rate_provider, tes_provider, provenance)
