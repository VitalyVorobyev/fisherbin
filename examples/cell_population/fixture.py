"""Create attributed bounded datasets from the upstream FlowCyt files."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np

from .data import (
    CLASS_NAMES,
    FEATURE_NAMES,
    REFERENCE_PATIENTS,
    TEST_PATIENTS,
    FlowCytData,
    deterministic_group_sample,
    load_csv_directory,
)

SOURCE_URL = "https://cuicloud.unige.ch/index.php/s/55PHBLEynrp5pN8"
SOURCE_REPOSITORY = "https://github.com/VIPER-GENEVA/FlowCyt-Classification-Benchmark"
REMOTE_RAW = "https://cuicloud.unige.ch/public.php/dav/files/55PHBLEynrp5pN8/raw"
CLASS_CODES = ("O", "N", "G", "P", "K", "B")


def _uniform_sample(data: FlowCytData, size: int, rng: np.random.Generator) -> FlowCytData:
    count = min(size, len(data.labels))
    indices = np.sort(rng.choice(len(data.labels), size=count, replace=False))
    return data.select(indices)


def write_fixture(
    data_dir: Path,
    output: Path,
    *,
    source_sha256: str,
    seed: int = 2026,
    reference_per_patient_class: int = 128,
    test_per_patient: int = 2_048,
) -> None:
    """Write a deterministic real-data fixture plus an attribution manifest."""
    rng = np.random.default_rng(seed)
    blocks: list[FlowCytData] = []
    for patient in REFERENCE_PATIENTS:
        patient_data = load_csv_directory(data_dir, (patient,))
        blocks.append(
            deterministic_group_sample(
                patient_data,
                max_per_patient_class=reference_per_patient_class,
                seed=seed + patient,
            )
        )
    for patient in TEST_PATIENTS:
        blocks.append(
            _uniform_sample(load_csv_directory(data_dir, (patient,)), test_per_patient, rng)
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        features=np.concatenate([block.features for block in blocks]).astype(np.float32),
        labels=np.concatenate([block.labels for block in blocks]).astype(np.int16),
        patients=np.concatenate([block.patients for block in blocks]).astype(np.int16),
        source_rows=np.concatenate([block.source_rows for block in blocks]).astype(np.int64),
        feature_names=np.asarray(FEATURE_NAMES),
        class_names=np.asarray(CLASS_NAMES),
    )
    manifest = {
        "title": "FlowCyt deterministic ScoreQuant fixture",
        "source_url": SOURCE_URL,
        "source_repository": SOURCE_REPOSITORY,
        "source_sha256": source_sha256,
        "source_license": "CC-BY-NC-SA-4.0",
        "seed": seed,
        "reference_patients": list(REFERENCE_PATIENTS),
        "test_patients": list(TEST_PATIENTS),
        "reference_per_patient_class": reference_per_patient_class,
        "test_per_patient": test_per_patient,
        "feature_names": list(FEATURE_NAMES),
        "class_names": list(CLASS_NAMES),
        "notes": (
            "Test rows were sampled uniformly without using labels; labels are evaluation-only."
        ),
    }
    output.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _range_request(url: str, start: int, end: int) -> bytes:
    request = Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urlopen(request, timeout=60) as response:  # noqa: S310 - fixed HTTPS source
        return response.read()


def _fcs_metadata(url: str) -> tuple[dict[str, str], int, int]:
    header = _range_request(url, 0, 8191)
    if not header.startswith(b"FCS3.0"):
        raise ValueError(f"unsupported FCS header at {url}")
    text_start = int(header[10:18].strip())
    text_end = int(header[18:26].strip())
    if text_end >= len(header):
        header = _range_request(url, 0, text_end)
    text = header[text_start : text_end + 1].decode("latin-1")
    delimiter = text[0]
    fields = text[1:].split(delimiter)
    if fields and fields[-1] == "":
        fields.pop()
    metadata = dict(zip(fields[0::2], fields[1::2], strict=True))
    return metadata, int(metadata["$BEGINDATA"]), int(metadata["$TOT"])


def _read_fcs_prefix(url: str, count: int) -> tuple[np.ndarray, int]:
    metadata, data_start, total = _fcs_metadata(url)
    n_parameters = int(metadata["$PAR"])
    selected_count = min(count, total)
    if metadata["$DATATYPE"] != "F" or any(
        metadata[f"$P{index}B"] != "32" for index in range(1, n_parameters + 1)
    ):
        raise ValueError("fixture generator expects 32-bit floating-point FCS data")
    byte_order = metadata["$BYTEORD"]
    if byte_order not in {"4,3,2,1", "1,2,3,4"}:
        raise ValueError(f"unsupported FCS byte order: {byte_order}")
    dtype = np.dtype(">f4" if byte_order == "4,3,2,1" else "<f4")
    byte_count = selected_count * n_parameters * dtype.itemsize
    payload = _range_request(url, data_start, data_start + byte_count - 1)
    matrix = np.frombuffer(payload, dtype=dtype, count=selected_count * n_parameters).reshape(
        selected_count, n_parameters
    )
    if n_parameters < 14:
        raise ValueError("FlowCyt fixture generator expects at least fourteen channels")
    indices = [0, 2, *range(4, 14)]
    return matrix[:, indices].astype(np.float64), total


def _stratified_patient_ranges(
    totals: tuple[int, ...],
    size: int,
    blocks: int,
    rng: np.random.Generator,
) -> tuple[tuple[tuple[int, int], ...], ...]:
    """Plan label-blind contiguous ranges over concatenated component files."""
    if not totals or any(total < 0 for total in totals):
        raise ValueError("totals must be a nonempty sequence of nonnegative counts")
    total = sum(totals)
    if size < 1 or blocks < 1 or total < 1:
        raise ValueError("size, blocks, and the total event count must be positive")
    target = min(size, total)
    n_strata = min(blocks, target)
    edges = np.linspace(0, total, n_strata + 1, dtype=np.int64)
    widths = np.diff(edges)
    raw_counts = widths.astype(np.float64) * target / total
    sample_counts = np.floor(raw_counts).astype(np.int64)
    remainder = target - int(np.sum(sample_counts))
    if remainder:
        priorities = np.argsort(-(raw_counts - sample_counts), kind="stable")
        sample_counts[priorities[:remainder]] += 1

    boundaries = np.concatenate([[0], np.cumsum(np.asarray(totals, dtype=np.int64))])
    planned: list[list[tuple[int, int]]] = [[] for _ in totals]
    for lower, upper, count in zip(edges[:-1], edges[1:], sample_counts, strict=True):
        if count == 0:
            continue
        start = int(rng.integers(lower, upper - count + 1))
        stop = start + int(count)
        while start < stop:
            file_index = int(np.searchsorted(boundaries[1:], start, side="right"))
            local_start = start - int(boundaries[file_index])
            take = min(stop - start, int(boundaries[file_index + 1]) - start)
            planned[file_index].append((local_start, take))
            start += take
    return tuple(tuple(ranges) for ranges in planned)


def _proportional_counts(totals: tuple[int, ...], size: int) -> tuple[int, ...]:
    """Allocate a bounded sample by deterministic largest-remainder rounding."""
    if not totals or any(total < 0 for total in totals):
        raise ValueError("totals must be a nonempty sequence of nonnegative counts")
    total = sum(totals)
    if size < 1 or total < 1:
        raise ValueError("size and the total event count must be positive")
    target = min(size, total)
    raw = np.asarray(totals, dtype=np.float64) * target / total
    counts = np.floor(raw).astype(np.int64)
    remainder = target - int(np.sum(counts))
    if remainder:
        priorities = np.argsort(-(raw - counts), kind="stable")
        counts[priorities[:remainder]] += 1
    return tuple(int(count) for count in counts)


def _read_fcs_range(
    url: str,
    metadata: dict[str, str],
    data_start: int,
    start_row: int,
    count: int,
) -> np.ndarray:
    """Read one contiguous event range from a 32-bit FlowCyt FCS file."""
    n_parameters = int(metadata["$PAR"])
    if metadata["$DATATYPE"] != "F" or any(
        metadata[f"$P{index}B"] != "32" for index in range(1, n_parameters + 1)
    ):
        raise ValueError("sample generator expects 32-bit floating-point FCS data")
    byte_order = metadata["$BYTEORD"]
    if byte_order not in {"4,3,2,1", "1,2,3,4"}:
        raise ValueError(f"unsupported FCS byte order: {byte_order}")
    dtype = np.dtype(">f4" if byte_order == "4,3,2,1" else "<f4")
    byte_start = data_start + start_row * n_parameters * dtype.itemsize
    byte_count = count * n_parameters * dtype.itemsize
    payload = _range_request(url, byte_start, byte_start + byte_count - 1)
    if len(payload) != byte_count:
        raise ValueError(f"incomplete FCS range from {url}: expected {byte_count} bytes")
    matrix = np.frombuffer(payload, dtype=dtype).reshape(count, n_parameters)
    if n_parameters < 14:
        raise ValueError("FlowCyt sample generator expects at least fourteen channels")
    return matrix[:, [0, 2, *range(4, 14)]].astype(np.float64)


def write_remote_sample(
    output: Path,
    *,
    seed: int = 2026,
    max_per_patient: int = 20_000,
    blocks_per_component: int = 16,
    workers: int = 12,
) -> None:
    """Range-read a composition-preserving sample from all thirty patients."""
    if max_per_patient < 1 or blocks_per_component < 1 or workers < 1:
        raise ValueError("sample size, block count, and worker count must be positive")
    files = [
        (patient, label, f"{REMOTE_RAW}/Case{patient}_{code}.fcs")
        for patient in (*REFERENCE_PATIENTS, *TEST_PATIENTS)
        for label, code in enumerate(CLASS_CODES)
    ]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        layouts = list(executor.map(lambda item: _fcs_metadata(item[2]), files))

    layout_by_file = {
        (patient, label): (url, metadata, data_start, total)
        for (patient, label, url), (metadata, data_start, total) in zip(files, layouts, strict=True)
    }
    rng = np.random.default_rng(seed)
    tasks: list[tuple[int, int, str, dict[str, str], int, int, int]] = []
    file_totals: dict[str, int] = {}
    for patient in (*REFERENCE_PATIENTS, *TEST_PATIENTS):
        totals = tuple(layout_by_file[(patient, label)][3] for label in range(len(CLASS_CODES)))
        counts = _proportional_counts(totals, max_per_patient)
        for label, (total, count) in enumerate(zip(totals, counts, strict=True)):
            url, metadata, data_start, total = layout_by_file[(patient, label)]
            file_totals[f"Case{patient}_{CLASS_CODES[label]}.fcs"] = total
            label_ranges = (
                ()
                if count == 0
                else _stratified_patient_ranges((total,), count, blocks_per_component, rng)[0]
            )
            tasks.extend(
                (patient, label, url, metadata, data_start, start, count)
                for start, count in label_ranges
            )

    def fetch(
        task: tuple[int, int, str, dict[str, str], int, int, int],
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        patient, label, url, metadata, data_start, start, count = task
        return (
            _read_fcs_range(url, metadata, data_start, start, count),
            np.full(count, label, dtype=np.int16),
            np.full(count, patient, dtype=np.int16),
            np.arange(start, start + count, dtype=np.int64),
        )

    with ThreadPoolExecutor(max_workers=workers) as executor:
        blocks = list(executor.map(fetch, tasks))
    features = np.concatenate([block[0] for block in blocks]).astype(np.float32)
    labels = np.concatenate([block[1] for block in blocks])
    patients = np.concatenate([block[2] for block in blocks])
    source_rows = np.concatenate([block[3] for block in blocks])
    order = np.lexsort((source_rows, labels, patients))

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        features=features[order],
        labels=labels[order],
        patients=patients[order],
        source_rows=source_rows[order],
        feature_names=np.asarray(FEATURE_NAMES),
        class_names=np.asarray(CLASS_NAMES),
    )
    digest = sha256(output.read_bytes()).hexdigest()
    manifest = {
        "title": "FlowCyt bounded all-patient ScoreQuant research sample",
        "source_url": SOURCE_URL,
        "source_repository": SOURCE_REPOSITORY,
        "source_license": "CC-BY-NC-SA-4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "seed": seed,
        "sampling": (
            "component-stratified ranges with largest-remainder allocation from exact FCS totals"
        ),
        "max_per_patient": max_per_patient,
        "blocks_per_component": blocks_per_component,
        "workers": workers,
        "sample_rows": len(labels),
        "sample_sha256": digest,
        "reference_patients": list(REFERENCE_PATIENTS),
        "test_patients": list(TEST_PATIENTS),
        "feature_names": list(FEATURE_NAMES),
        "class_names": list(CLASS_NAMES),
        "upstream_file_totals": file_totals,
        "notes": (
            "Rows are spread deterministically within each upstream labelled component so the "
            "bounded sample preserves patient composition. Test labels remain evaluation-only "
            "after dataset assembly."
        ),
    }
    output.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_remote_fixture(
    output: Path,
    *,
    seed: int = 2026,
    reference_per_patient_class: int = 128,
    test_per_patient: int = 2_048,
) -> None:
    """Build the fixture with HTTP range reads from the licensed FCS files."""
    rng = np.random.default_rng(seed)
    feature_blocks: list[np.ndarray] = []
    label_blocks: list[np.ndarray] = []
    patient_blocks: list[np.ndarray] = []
    source_blocks: list[np.ndarray] = []
    file_totals: dict[str, int] = {}

    for patient in (*REFERENCE_PATIENTS, *TEST_PATIENTS):
        cached: list[tuple[np.ndarray, int]] = []
        for code in CLASS_CODES:
            url = f"{REMOTE_RAW}/Case{patient}_{code}.fcs"
            rows, total = _read_fcs_prefix(url, max(reference_per_patient_class, test_per_patient))
            cached.append((rows, total))
            file_totals[f"Case{patient}_{code}.fcs"] = total
        if patient in REFERENCE_PATIENTS:
            counts = [min(reference_per_patient_class, total) for _, total in cached]
        else:
            totals = np.asarray([total for _, total in cached], dtype=np.float64)
            counts = rng.multinomial(test_per_patient, totals / np.sum(totals)).tolist()
        for label, ((rows, total), count) in enumerate(zip(cached, counts, strict=True)):
            selected = min(count, len(rows), total)
            if selected == 0:
                continue
            feature_blocks.append(rows[:selected])
            label_blocks.append(np.full(selected, label, dtype=np.int16))
            patient_blocks.append(np.full(selected, patient, dtype=np.int16))
            source_blocks.append(np.arange(selected, dtype=np.int64))

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        features=np.concatenate(feature_blocks).astype(np.float32),
        labels=np.concatenate(label_blocks),
        patients=np.concatenate(patient_blocks),
        source_rows=np.concatenate(source_blocks),
        feature_names=np.asarray(FEATURE_NAMES),
        class_names=np.asarray(CLASS_NAMES),
    )
    manifest = {
        "title": "FlowCyt deterministic ScoreQuant fixture",
        "source_url": SOURCE_URL,
        "source_repository": SOURCE_REPOSITORY,
        "source_license": "CC-BY-NC-SA-4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "seed": seed,
        "sampling": "prefix rows per class; test class counts sampled from each file's $TOT",
        "reference_patients": list(REFERENCE_PATIENTS),
        "test_patients": list(TEST_PATIENTS),
        "reference_per_patient_class": reference_per_patient_class,
        "test_per_patient": test_per_patient,
        "feature_names": list(FEATURE_NAMES),
        "class_names": list(CLASS_NAMES),
        "upstream_file_totals": file_totals,
        "notes": (
            "Test mixture counts use file metadata; labels are evaluation-only after assembly."
        ),
    }
    output.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
