"""Command-line entry point for the FlowCyt example."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from examples._env import is_fast_mode

from .data import (
    REFERENCE_PATIENTS,
    TEST_PATIENTS,
    FlowCytData,
    load_csv_directory_sampled,
    load_fixture,
)
from .experiment import run_experiment
from .figures import write_outputs
from .fixture import (
    write_fixture,
    write_remote_fixture,
    write_remote_full_csvs,
    write_remote_sample,
)
from .transport_audit import write_transport_audit


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the FlowCyt ScoreQuant use case")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--fixture", type=Path, help="compressed fixture path")
    source.add_argument("--data-dir", type=Path, help="FlowCyt data_original directory")
    parser.add_argument(
        "--output-dir", type=Path, help="result directory (defaults under flowcyt-results)"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="use short optimizer settings")
    mode.add_argument("--full", action="store_true", help="use the frozen research settings")
    parser.add_argument("--bins", type=int, nargs="+", default=[5, 8, 10, 15, 20, 30])
    parser.add_argument("--operating-bins", type=int, default=8)
    parser.add_argument("--uncertainty-bins", type=int, default=30)
    parser.add_argument("--max-per-patient", type=int, default=20_000)
    parser.add_argument("--write-fixture", type=Path, help="create fixture from --data-dir")
    parser.add_argument(
        "--download-fixture", type=Path, help="range-read the public FCS files into a fixture"
    )
    parser.add_argument(
        "--download-sample",
        type=Path,
        help="range-read a bounded all-patient sample from the public FCS files",
    )
    parser.add_argument(
        "--download-full-csv-dir",
        type=Path,
        help="stream all public component FCS files into thirty external Case_*.csv files",
    )
    parser.add_argument(
        "--download-chunk-rows",
        type=int,
        default=200_000,
        help="FCS rows per range request when building the full CSV corpus",
    )
    parser.add_argument(
        "--sample-blocks",
        type=int,
        default=16,
        help="stratified contiguous ranges per component for --download-sample",
    )
    parser.add_argument("--download-workers", type=int, default=12)
    parser.add_argument("--source-sha256", default="", help="upstream archive SHA-256")
    parser.add_argument(
        "--transport-audit-sample",
        type=Path,
        help="compare this bounded sample with every row under --data-dir",
    )
    parser.add_argument(
        "--transport-audit-output",
        type=Path,
        help="JSON path for the full-corpus transport audit",
    )
    parser.add_argument("--transport-audit-chunksize", type=int, default=200_000)
    return parser


def _load_data(args: argparse.Namespace) -> FlowCytData:
    if args.fixture is not None:
        return load_fixture(args.fixture)
    if args.data_dir is not None:
        reference = load_csv_directory_sampled(
            args.data_dir,
            REFERENCE_PATIENTS,
            max_per_patient=args.max_per_patient,
        )
        test = load_csv_directory_sampled(
            args.data_dir,
            TEST_PATIENTS,
            max_per_patient=args.max_per_patient,
            seed=2027,
        )
        return FlowCytData(
            features=np.concatenate([reference.features, test.features]),
            labels=np.concatenate([reference.labels, test.labels]),
            patients=np.concatenate([reference.patients, test.patients]),
            source_rows=np.concatenate([reference.source_rows, test.source_rows]),
        )
    default_fixture = Path("examples/data/flowcyt_fixture.npz")
    return load_fixture(default_fixture)


def main() -> None:
    """Parse arguments, run the experiment, and write reproducible artifacts."""
    args = _parser().parse_args()
    if args.download_fixture is not None:
        write_remote_fixture(args.download_fixture)
        return
    if args.download_sample is not None:
        write_remote_sample(
            args.download_sample,
            max_per_patient=args.max_per_patient,
            blocks_per_component=args.sample_blocks,
            workers=args.download_workers,
        )
        return
    if args.download_full_csv_dir is not None:
        write_remote_full_csvs(
            args.download_full_csv_dir,
            chunk_rows=args.download_chunk_rows,
            workers=args.download_workers,
        )
        return
    if args.write_fixture is not None:
        if args.data_dir is None or not args.source_sha256:
            raise SystemExit("--write-fixture requires --data-dir and --source-sha256")
        write_fixture(args.data_dir, args.write_fixture, source_sha256=args.source_sha256)
        return
    if args.transport_audit_sample is not None:
        if args.data_dir is None or args.transport_audit_output is None:
            raise SystemExit(
                "--transport-audit-sample requires --data-dir and --transport-audit-output"
            )
        write_transport_audit(
            args.data_dir,
            args.transport_audit_sample,
            args.transport_audit_output,
            chunksize=args.transport_audit_chunksize,
        )
        return
    data = _load_data(args)
    if args.quick:
        quick = True
    elif args.full:
        quick = False
    else:
        # No explicit --quick/--full: honor SCOREQUANT_EXAMPLE_FAST, falling back to
        # the original heuristic (fixture or unspecified data defaults to quick).
        quick = is_fast_mode() or args.fixture is not None or args.data_dir is None
    result = run_experiment(
        data,
        bin_counts=tuple(args.bins),
        operating_n_bins=args.operating_bins,
        uncertainty_n_bins=args.uncertainty_bins,
        quick=quick,
    )
    if args.fixture is not None:
        manifest_path = args.fixture.with_suffix(".json")
        if manifest_path.is_file():
            source_metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
            source_metadata["title"] = "FlowCyt ScoreQuant source manifest"
            result.metrics["source"] = source_metadata
    output_dir = args.output_dir or Path("flowcyt-results") / ("quick" if quick else "full")
    write_outputs(result, output_dir)
    print(result.metrics["run"])


if __name__ == "__main__":
    main()
