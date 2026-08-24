"""Data contracts and preprocessing for the FlowCyt use case."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

FEATURE_NAMES = (
    "FS INT",
    "SS INT",
    "FL1 INT_CD14-FITC",
    "FL2 INT_CD19-PE",
    "FL3 INT_CD13-ECD",
    "FL4 INT_CD33-PC5.5",
    "FL5 INT_CD34-PC7",
    "FL6 INT_CD117-APC",
    "FL7 INT_CD7-APC700",
    "FL8 INT_CD16-APC750",
    "FL9 INT_HLA-PB",
    "FL10 INT_CD45-KO",
)

CLASS_NAMES = ("T cells", "B cells", "monocytes", "mast cells", "HSPCs", "other")
REFERENCE_PATIENTS = (1, 2, 3, 4, 7, 10, 12, 13, 14, 16, 17, 18, 19, 21, 22, 24, 25, 26, 27, 29)
TEST_PATIENTS = (5, 6, 8, 9, 11, 15, 20, 23, 28, 30)
REFERENCE_FOLDS = (
    (4, 17, 27, 21),
    (22, 24, 10, 13),
    (18, 19, 25, 29),
    (26, 7, 2, 12),
    (1, 14, 3, 16),
)


@dataclass(frozen=True, slots=True)
class FlowCytData:
    """Store marker rows together with labels and patient provenance."""

    features: np.ndarray
    labels: np.ndarray
    patients: np.ndarray
    source_rows: np.ndarray

    def __post_init__(self) -> None:
        """Validate the tabular contract eagerly."""
        features = np.asarray(self.features)
        labels = np.asarray(self.labels)
        patients = np.asarray(self.patients)
        source_rows = np.asarray(self.source_rows)
        if features.ndim != 2 or features.shape[1] != len(FEATURE_NAMES):
            raise ValueError(f"features must have shape [N, {len(FEATURE_NAMES)}]")
        if labels.shape != (features.shape[0],):
            raise ValueError("labels must have shape [N]")
        if patients.shape != labels.shape or source_rows.shape != labels.shape:
            raise ValueError("patients and source_rows must align with labels")
        if not np.isfinite(features).all():
            raise ValueError("features must be finite")
        if not np.isin(labels, np.arange(len(CLASS_NAMES))).all():
            raise ValueError("labels must use the six declared FlowCyt classes")

    def select(self, mask: np.ndarray) -> FlowCytData:
        """Return rows selected by a boolean mask or integer indices."""
        return FlowCytData(
            self.features[mask],
            self.labels[mask],
            self.patients[mask],
            self.source_rows[mask],
        )

    def patients_in(self, patient_ids: tuple[int, ...]) -> FlowCytData:
        """Return rows belonging to the requested patients."""
        return self.select(np.isin(self.patients, patient_ids))


@dataclass(frozen=True, slots=True)
class RobustArcsinhTransform:
    """Frozen reference-only arcsinh and robust channel scaling."""

    median: np.ndarray
    scale: np.ndarray
    cofactor: float = 150.0

    @classmethod
    def fit(cls, features: np.ndarray, *, cofactor: float = 150.0) -> RobustArcsinhTransform:
        """Fit channel locations and scales without consulting test patients."""
        values = np.asarray(features, dtype=np.float64)
        if values.ndim != 2 or values.shape[1] != len(FEATURE_NAMES):
            raise ValueError(f"features must have shape [N, {len(FEATURE_NAMES)}]")
        if not np.isfinite(values).all() or not np.isfinite(cofactor) or cofactor <= 0:
            raise ValueError("features and positive cofactor must be finite")
        transformed = np.arcsinh(values / cofactor)
        median = np.median(transformed, axis=0)
        lower, upper = np.quantile(transformed, [0.25, 0.75], axis=0)
        scale = upper - lower
        if np.any(scale <= np.finfo(np.float64).eps):
            raise ValueError("reference data contain a constant marker channel")
        return cls(median=median, scale=scale, cofactor=float(cofactor))

    def apply(self, features: np.ndarray) -> np.ndarray:
        """Apply the frozen transform to marker rows."""
        values = np.asarray(features, dtype=np.float64)
        if values.ndim != 2 or values.shape[1] != len(FEATURE_NAMES):
            raise ValueError(f"features must have shape [N, {len(FEATURE_NAMES)}]")
        if not np.isfinite(values).all():
            raise ValueError("features must be finite")
        return (np.arcsinh(values / self.cofactor) - self.median) / self.scale


def load_csv_directory(data_dir: Path, patient_ids: tuple[int, ...]) -> FlowCytData:
    """Load selected FlowCyt ``Case_<id>.csv`` files."""
    feature_blocks: list[np.ndarray] = []
    label_blocks: list[np.ndarray] = []
    patient_blocks: list[np.ndarray] = []
    row_blocks: list[np.ndarray] = []
    columns = [*FEATURE_NAMES, "label"]
    for patient in patient_ids:
        path = data_dir / f"Case_{patient}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"missing FlowCyt CSV: {path}")
        frame = pd.read_csv(path, usecols=columns)
        features = frame.loc[:, FEATURE_NAMES].to_numpy(dtype=np.float64)
        labels = frame.loc[:, "label"].to_numpy(dtype=np.int16)
        feature_blocks.append(features)
        label_blocks.append(labels)
        patient_blocks.append(np.full(len(frame), patient, dtype=np.int16))
        row_blocks.append(np.arange(len(frame), dtype=np.int64))
    return FlowCytData(
        features=np.concatenate(feature_blocks),
        labels=np.concatenate(label_blocks),
        patients=np.concatenate(patient_blocks),
        source_rows=np.concatenate(row_blocks),
    )


def load_csv_directory_sampled(
    data_dir: Path,
    patient_ids: tuple[int, ...],
    *,
    max_per_patient: int,
    seed: int = 2026,
) -> FlowCytData:
    """Load a uniform, label-blind cap from each patient CSV."""
    if max_per_patient < 1:
        raise ValueError("max_per_patient must be positive")
    rng = np.random.default_rng(seed)
    blocks: list[FlowCytData] = []
    for patient in patient_ids:
        patient_data = load_csv_directory(data_dir, (patient,))
        if len(patient_data.labels) > max_per_patient:
            indices = np.sort(
                rng.choice(len(patient_data.labels), size=max_per_patient, replace=False)
            )
            patient_data = patient_data.select(indices)
        blocks.append(patient_data)
    return FlowCytData(
        features=np.concatenate([block.features for block in blocks]),
        labels=np.concatenate([block.labels for block in blocks]),
        patients=np.concatenate([block.patients for block in blocks]),
        source_rows=np.concatenate([block.source_rows for block in blocks]),
    )


def load_fixture(path: Path) -> FlowCytData:
    """Load the committed compressed FlowCyt fixture."""
    with np.load(path, allow_pickle=False) as payload:
        stored_features = tuple(str(value) for value in payload["feature_names"].tolist())
        stored_classes = tuple(str(value) for value in payload["class_names"].tolist())
        if stored_features != FEATURE_NAMES or stored_classes != CLASS_NAMES:
            raise ValueError("fixture schema does not match the FlowCyt example contract")
        return FlowCytData(
            features=np.asarray(payload["features"], dtype=np.float64),
            labels=np.asarray(payload["labels"], dtype=np.int16),
            patients=np.asarray(payload["patients"], dtype=np.int16),
            source_rows=np.asarray(payload["source_rows"], dtype=np.int64),
        )


def deterministic_group_sample(
    data: FlowCytData,
    *,
    max_per_patient_class: int,
    seed: int,
) -> FlowCytData:
    """Cap every patient/class group with reproducible without-replacement sampling."""
    if max_per_patient_class < 1:
        raise ValueError("max_per_patient_class must be positive")
    rng = np.random.default_rng(seed)
    chosen: list[np.ndarray] = []
    for patient in np.unique(data.patients):
        for label in range(len(CLASS_NAMES)):
            indices = np.flatnonzero((data.patients == patient) & (data.labels == label))
            if len(indices) == 0:
                continue
            count = min(len(indices), max_per_patient_class)
            chosen.append(np.sort(rng.choice(indices, size=count, replace=False)))
    if not chosen:
        raise ValueError("no rows were available for grouped sampling")
    return data.select(np.sort(np.concatenate(chosen)))
