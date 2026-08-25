"""Chunked full-corpus transport audit for the bounded FlowCyt sample."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd

from .data import CLASS_NAMES, FEATURE_NAMES, FlowCytData, load_fixture


@dataclass(slots=True)
class _Moments:
    rows: int
    class_counts: np.ndarray
    feature_sum: np.ndarray
    feature_square_sum: np.ndarray

    @classmethod
    def empty(cls) -> _Moments:
        return cls(
            rows=0,
            class_counts=np.zeros(len(CLASS_NAMES), dtype=np.int64),
            feature_sum=np.zeros(len(FEATURE_NAMES), dtype=np.float64),
            feature_square_sum=np.zeros(len(FEATURE_NAMES), dtype=np.float64),
        )

    def add(self, features: np.ndarray, labels: np.ndarray) -> None:
        self.rows += len(labels)
        self.class_counts += np.bincount(labels, minlength=len(CLASS_NAMES))
        self.feature_sum += np.sum(features, axis=0, dtype=np.float64)
        self.feature_square_sum += np.sum(np.square(features), axis=0, dtype=np.float64)

    def summary(self) -> dict[str, object]:
        mean = self.feature_sum / self.rows
        variance = np.maximum(self.feature_square_sum / self.rows - mean**2, 0)
        return {
            "rows": self.rows,
            "class_counts": self.class_counts.tolist(),
            "class_fractions": (self.class_counts / self.rows).tolist(),
            "feature_mean": mean.tolist(),
            "feature_std": np.sqrt(variance).tolist(),
        }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sample_moments(data: FlowCytData, patient: int) -> _Moments:
    selected = data.patients == patient
    moments = _Moments.empty()
    moments.add(data.features[selected], data.labels[selected])
    return moments


def audit_transport(
    data_dir: Path,
    sample_path: Path,
    *,
    patient_ids: tuple[int, ...] = tuple(range(1, 31)),
    chunksize: int = 200_000,
) -> dict[str, object]:
    """Compare exact full-corpus moments with a frozen bounded sample.

    The audit reads every upstream CSV row in chunks and makes no fitting or
    tuning decision. It measures transport of class fractions and the first two
    marker moments by patient.
    """
    if chunksize < 1:
        raise ValueError("chunksize must be positive")
    sample = load_fixture(sample_path)
    patients: dict[str, object] = {}
    maximum_fraction_error = 0.0
    maximum_standardized_mean_error = 0.0
    full_rows = 0
    full_files: list[dict[str, str | int]] = []
    columns = [*FEATURE_NAMES, "label"]
    for patient in patient_ids:
        path = data_dir / f"Case_{patient}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"missing FlowCyt CSV: {path}")
        full = _Moments.empty()
        for chunk in pd.read_csv(path, usecols=columns, chunksize=chunksize):
            features = chunk.loc[:, FEATURE_NAMES].to_numpy(dtype=np.float64)
            labels = chunk.loc[:, "label"].to_numpy(dtype=np.int16)
            full.add(features, labels)
        bounded = _sample_moments(sample, patient)
        if bounded.rows == 0:
            raise ValueError(f"bounded sample contains no rows for patient {patient}")
        full_summary = full.summary()
        bounded_summary = bounded.summary()
        fraction_error = np.asarray(bounded_summary["class_fractions"]) - np.asarray(
            full_summary["class_fractions"]
        )
        full_mean = np.asarray(full_summary["feature_mean"])
        bounded_mean = np.asarray(bounded_summary["feature_mean"])
        full_std = np.asarray(full_summary["feature_std"])
        standardized = (bounded_mean - full_mean) / np.maximum(full_std, 1e-12)
        maximum_fraction_error = max(maximum_fraction_error, float(np.max(np.abs(fraction_error))))
        maximum_standardized_mean_error = max(
            maximum_standardized_mean_error, float(np.max(np.abs(standardized)))
        )
        patients[str(patient)] = {
            "full": full_summary,
            "bounded": bounded_summary,
            "class_fraction_error": fraction_error.tolist(),
            "standardized_feature_mean_error": standardized.tolist(),
        }
        full_rows += full.rows
        full_files.append({"name": path.name, "sha256": _sha256(path), "rows": full.rows})
    return {
        "schema": "scorequant.flowcyt.transport-audit.v1",
        "purpose": "stress and transport audit only; no tuning or test-patient selection",
        "sample": {
            "path": str(sample_path),
            "sha256": _sha256(sample_path),
            "rows": len(sample.labels),
        },
        "full_corpus": {
            "data_dir": str(data_dir),
            "rows": full_rows,
            "files": full_files,
        },
        "maximum_absolute_class_fraction_error": maximum_fraction_error,
        "maximum_absolute_standardized_feature_mean_error": maximum_standardized_mean_error,
        "patients": patients,
    }


def write_transport_audit(
    data_dir: Path,
    sample_path: Path,
    output_path: Path,
    *,
    chunksize: int = 200_000,
) -> None:
    """Run the audit and write deterministic JSON, CSV, and figure evidence."""
    result = audit_transport(data_dir, sample_path, chunksize=chunksize)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    patient_payload = cast(dict[str, dict[str, object]], result["patients"])
    rows: list[dict[str, int | float]] = []
    for patient, payload in patient_payload.items():
        full = cast(dict[str, object], payload["full"])
        bounded = cast(dict[str, object], payload["bounded"])
        fraction_error = np.asarray(payload["class_fraction_error"], dtype=float)
        mean_error = np.asarray(payload["standardized_feature_mean_error"], dtype=float)
        rows.append(
            {
                "patient": int(patient),
                "full_rows": int(cast(int, full["rows"])),
                "bounded_rows": int(cast(int, bounded["rows"])),
                "maximum_absolute_class_fraction_error": float(np.max(np.abs(fraction_error))),
                "maximum_absolute_standardized_feature_mean_error": float(
                    np.max(np.abs(mean_error))
                ),
            }
        )
    table = pd.DataFrame(rows).sort_values("patient")
    table.to_csv(output_path.with_suffix(".csv"), index=False)

    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
    axes[0].bar(table["patient"], table["maximum_absolute_class_fraction_error"])
    axes[0].set(
        title="Bounded-sample class transport",
        xlabel="patient",
        ylabel="maximum absolute fraction error",
    )
    axes[1].bar(table["patient"], table["maximum_absolute_standardized_feature_mean_error"])
    axes[1].set(
        title="Bounded-sample marker transport",
        xlabel="patient",
        ylabel="maximum standardized mean error",
    )
    figure.suptitle("FlowCyt 600k approximation versus full corpus")
    figure.savefig(output_path.with_suffix(".png"), dpi=160)
    plt.close(figure)
