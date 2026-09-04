"""Load and validate the committed FAIR Universe HiggsML fixture.

The fixture is built offline by ``examples/hep_classifier/fixture.py`` (never
run by this module, the tests, or CI) and committed at
``examples/data/hep_higgsml_fixture.npz`` with provenance recorded in the
sibling ``.json``. See ``docs/programme/S07-hep-classifier-showcase.md``
(design decisions D1, D3) for why the fixture holds seven `tes` variants of
the same 1,000 row-aligned events rather than a single feature table.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np

FIXTURE_PATH = Path("examples/data/hep_higgsml_fixture.npz")
PROVENANCE_PATH = Path("examples/data/hep_higgsml_fixture.json")

#: `tes` points the fixture commits, matching D4's convergence-study offsets:
#: delta in {0.025, 0.05, 0.10} around the reference `tes = 1.0`.
TES_POINTS: tuple[float, ...] = (0.90, 0.95, 0.975, 1.00, 1.025, 1.05, 1.10)

#: The process name D1 treats as signal; every other detailed label
#: (`ztautau`, `ttbar`, `diboson`) is collapsed into one background component.
SIGNAL_PROCESS = "htautau"


def _variant_key(tes: float) -> str:
    return f"features_tes_{tes:.4f}"


@dataclass(frozen=True, slots=True)
class HepData:
    """Row-aligned FAIR Universe HiggsML events at every committed `tes` value.

    Attributes
    ----------
    variants
        Mapping from each committed `tes` value to its ``[N, 28]`` feature
        matrix. Every matrix shares the same row order (D3/C2: upstream
        selection is held fixed, so the variants never lose or gain rows).
    weights
        Nonnegative Monte Carlo event weights, shape ``[N]``, with at least
        one strictly positive entry.
    is_signal
        Boolean signal/background label, shape ``[N]`` -- `True` where
        `detailed_labels == "htautau"`, collapsing `ztautau`, `ttbar`, and
        `diboson` into one background component (D1).
    detailed_labels
        Process name per event, shape ``[N]``.
    feature_names
        The 28 `PRI_*`/`DER_*` column names, shared by every variant.
    """

    variants: dict[float, np.ndarray]
    weights: np.ndarray
    is_signal: np.ndarray
    detailed_labels: np.ndarray
    feature_names: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate row alignment, weights, and the feature-name contract."""
        if set(self.variants) != set(TES_POINTS):
            raise ValueError(f"fixture must carry exactly the tes points {TES_POINTS}")
        n_events = self.weights.shape[0]
        for tes, matrix in self.variants.items():
            if matrix.shape != (n_events, len(self.feature_names)):
                raise ValueError(f"tes={tes} feature matrix is not row-aligned with the fixture")
            if not np.all(np.isfinite(matrix)):
                raise ValueError(f"tes={tes} feature matrix must be finite")
        if self.is_signal.shape != (n_events,) or self.is_signal.dtype != np.bool_:
            raise ValueError("is_signal must be a boolean vector of shape [N]")
        if self.detailed_labels.shape != (n_events,):
            raise ValueError("detailed_labels must have shape [N]")
        if not np.all(np.isfinite(self.weights)) or np.any(self.weights < 0):
            raise ValueError("weights must be finite and nonnegative")
        if not np.any(self.weights > 0):
            raise ValueError("at least one weight must be strictly positive")
        if not np.array_equal(self.is_signal, self.detailed_labels == SIGNAL_PROCESS):
            raise ValueError("is_signal must agree with detailed_labels == 'htautau'")

    @property
    def n_events(self) -> int:
        """Return the number of row-aligned events every variant shares."""
        return int(self.weights.shape[0])

    def features_at(self, tes: float) -> np.ndarray:
        """Return the committed feature matrix for one exact `tes` value.

        Parameters
        ----------
        tes
            One of the seven committed `tes` points; looked up by nearest
            match at ``1e-6`` tolerance rather than exact float equality.

        Returns
        -------
        numpy.ndarray
            Feature matrix with shape ``[N, 28]``.
        """
        for candidate, matrix in self.variants.items():
            if abs(candidate - tes) < 1e-6:
                return matrix
        raise KeyError(f"tes={tes} is not one of the committed points {sorted(self.variants)}")


def load_fixture(path: Path = FIXTURE_PATH) -> HepData:
    """Load and validate the committed FAIR Universe HiggsML fixture.

    Parameters
    ----------
    path
        Path to the committed ``.npz`` fixture.

    Returns
    -------
    HepData
        The row-aligned event table across every committed `tes` variant.
    """
    # The fixture stores `feature_names` as an object array of Python
    # strings (see `examples/hep_classifier/fixture.py`), so this trusted,
    # repository-committed file needs `allow_pickle=True` to load.
    with np.load(path, allow_pickle=True) as payload:
        feature_names = tuple(str(name) for name in payload["feature_names"].tolist())
        stored_points = np.asarray(payload["tes_points"], dtype=np.float64)
        if not np.allclose(sorted(stored_points), sorted(TES_POINTS), atol=1e-6):
            raise ValueError("fixture tes_points do not match the example's expected grid")
        variants = {
            tes: np.asarray(payload[_variant_key(tes)], dtype=np.float64) for tes in TES_POINTS
        }
        weights = np.asarray(payload["weights"], dtype=np.float64)
        labels = np.asarray(payload["labels"], dtype=np.int64)
        detailed_labels = np.asarray(payload["detailed_labels"], dtype=str)
    is_signal = detailed_labels == SIGNAL_PROCESS
    if not np.array_equal(labels == 1, is_signal):
        raise ValueError("fixture labels==1 must agree with detailed_labels=='htautau'")
    return HepData(
        variants=variants,
        weights=weights,
        is_signal=is_signal,
        detailed_labels=detailed_labels,
        feature_names=feature_names,
    )


def load_provenance(path: Path = PROVENANCE_PATH) -> dict[str, object]:
    """Load the fixture's provenance record for the doc page and reports.

    Returns
    -------
    dict
        The parsed ``hep_higgsml_fixture.json`` mapping: dataset name,
        licence, the Zenodo DOI, the upstream commit and byte source, the
        `dopostprocess=False` note, and the composition/weight facts D3
        measured directly against the upstream code.
    """
    with path.open(encoding="utf-8") as stream:
        return cast(dict[str, object], json.load(stream))
