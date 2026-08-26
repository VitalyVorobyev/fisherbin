"""Sampling profiler for the ScoreQuant benchmark matrix.

This driver reuses the scenario runners in ``benchmarks/bench.py`` so that a
profile always measures exactly the code path the timing harness and
``benchmarks/baselines.json`` measure. It separates a JIT/trace warm-up pass
from the sampled steady-state pass, samples the main thread's Python stack from
a background thread, and writes two artifacts per cell:

* a folded-stack file (``stack;frames count``) that ``flamegraph.pl``,
  ``inferno-flamegraph``, or speedscope render directly, and
* a JSON summary holding the elapsed seconds plus the top self-time and
  cumulative-time frames.

``py-spy`` is the preferred external profiler and is pinned in the ``dev``
group, but on macOS it requires root; this in-process sampler needs no
elevated permissions and attributes time to the same Python frames. Both are
statistical: a frame's share is a sample count, not an exact duration, and time
spent inside XLA kernels is attributed to the Python frame that dispatched
them.

Results are checkpointed after every cell, so re-running the same command with
the same ``--json`` resumes an interrupted campaign instead of repeating
finished work.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import threading
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter, sleep
from types import FrameType

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bench import (  # noqa: E402
    _RUNNERS,
    _SCENARIO_NAMES,
    JsonValue,
    ScenarioConfig,
    _environment,
    _scenario_dims,
    _skip_reason,
)

_DEFAULT_RATE_HZ = 200.0
_DEFAULT_TOP = 25
# The sampler thread must take the GIL to read the main thread's frames, so the
# interpreter switch interval bounds its worst-case latency. CPython's 5 ms
# default is coarser than the sample period; 1 ms keeps the bias small without
# meaningfully perturbing the workload.
_SWITCH_INTERVAL_SECONDS = 0.001
_REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True, slots=True)
class ProfileSummary:
    """Sampled attribution of one scenario run."""

    config: ScenarioConfig
    elapsed_seconds: float
    samples: int
    rate_hz: float
    self_counts: Counter[str]
    total_counts: Counter[str]
    folded: Counter[str]

    def to_json(self, top: int) -> dict[str, JsonValue]:
        """Return a compact JSON record of this profile."""
        total = max(1, self.samples)
        return {
            "scenario": self.config.scenario,
            "rows": self.config.rows,
            "dims": self.config.dims,
            "bins": self.config.bins,
            "seed": self.config.seed,
            "max_scans": self.config.max_scans,
            "elapsed_seconds": self.elapsed_seconds,
            "samples": self.samples,
            "rate_hz": self.rate_hz,
            "self_percent": [
                {"frame": frame, "percent": 100.0 * count / total, "samples": count}
                for frame, count in self.self_counts.most_common(top)
            ],
            "cumulative_percent": [
                {"frame": frame, "percent": 100.0 * count / total, "samples": count}
                for frame, count in self.total_counts.most_common(top)
            ],
        }


class _StackSampler:
    """Background thread that periodically records the main thread's stack."""

    def __init__(self, target: int, rate_hz: float) -> None:
        self._target = target
        self._interval = 1.0 / rate_hz
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self.folded: Counter[str] = Counter()
        self.self_counts: Counter[str] = Counter()
        self.total_counts: Counter[str] = Counter()
        self.samples = 0

    def __enter__(self) -> _StackSampler:
        self._previous_switch = sys.getswitchinterval()
        sys.setswitchinterval(_SWITCH_INTERVAL_SECONDS)
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        self._thread.join(timeout=5.0)
        sys.setswitchinterval(self._previous_switch)

    def _loop(self) -> None:
        while not self._stop.is_set():
            frame = sys._current_frames().get(self._target)
            if frame is not None:
                self._record(frame)
            sleep(self._interval)

    def _record(self, frame: FrameType) -> None:
        stack: list[str] = []
        current: FrameType | None = frame
        while current is not None:
            stack.append(_frame_label(current))
            current = current.f_back
        stack.reverse()
        self.samples += 1
        # A run of the same label is recursion. Its depth is not what these
        # profiles are read for, and keeping it makes nearly every sample of a
        # recursive search a unique stack, so the folded file collapses each run
        # to one frame. Self and cumulative attribution are unaffected.
        collapsed = [
            label for index, label in enumerate(stack) if index == 0 or label != stack[index - 1]
        ]
        self.folded[";".join(collapsed)] += 1
        self.self_counts[stack[-1]] += 1
        for label in dict.fromkeys(stack):
            self.total_counts[label] += 1


def _frame_label(frame: FrameType) -> str:
    """Return a stable ``module:function`` label for one interpreter frame.

    Third-party frames are reported from their installed package root rather
    than from the environment prefix, so a folded-stack file stays readable and
    stays the same size whether the virtual environment lives inside the
    repository or beside it.
    """
    path = Path(frame.f_code.co_filename)
    parts = path.parts
    if "site-packages" in parts:
        module = "/".join(parts[parts.index("site-packages") + 1 :])
    else:
        try:
            module = path.relative_to(_REPO_ROOT).as_posix()
        except ValueError:
            module = "/".join(parts[-2:]) if len(parts) >= 2 else path.name
    return f"{module}:{frame.f_code.co_name}"


def _profile_cell(cfg: ScenarioConfig, rate_hz: float, warmups: int) -> ProfileSummary:
    """Warm the scenario up, then run it once under the stack sampler."""
    runner = _RUNNERS[cfg.scenario]
    for _ in range(warmups):
        runner(cfg, 1)
    main_thread = threading.main_thread().ident
    assert main_thread is not None
    started = perf_counter()
    with _StackSampler(main_thread, rate_hz) as sampler:
        runner(cfg, 1)
    elapsed = perf_counter() - started
    return ProfileSummary(
        config=cfg,
        elapsed_seconds=elapsed,
        samples=sampler.samples,
        rate_hz=rate_hz,
        self_counts=sampler.self_counts,
        total_counts=sampler.total_counts,
        folded=sampler.folded,
    )


def _cell_key(cfg: ScenarioConfig) -> str:
    suffix = "" if cfg.max_scans is None else f"_s{cfg.max_scans}"
    return f"{cfg.scenario}_n{cfg.rows}_r{cfg.dims}_b{cfg.bins}{suffix}"


def _write_folded(summary: ProfileSummary, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{_cell_key(summary.config)}.folded"
    lines = [f"{stack} {count}" for stack, count in summary.folded.most_common()]
    path.write_text("\n".join(lines) + "\n")
    return path


def _load_checkpoint(path: Path | None) -> dict[str, JsonValue]:
    if path is None or not path.exists():
        return {}
    document = json.loads(path.read_text())
    records: dict[str, JsonValue] = {}
    for record in document.get("profiles", []):
        cfg = ScenarioConfig(
            scenario=str(record["scenario"]),
            rows=int(record["rows"]),
            dims=int(record["dims"]),
            bins=int(record["bins"]),
            seed=int(record["seed"]),
            max_scans=(None if record.get("max_scans") is None else int(record["max_scans"])),
        )
        records[_cell_key(cfg)] = record
    return records


def _save_checkpoint(path: Path, records: dict[str, JsonValue]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document: dict[str, JsonValue] = {
        "environment": {**_environment(), "cpu": platform.processor()},
        "profiles": list(records.values()),
    }
    path.write_text(json.dumps(document, indent=2) + "\n")


def _format_summary(summary: ProfileSummary, top: int) -> str:
    total = max(1, summary.samples)
    header = (
        f"{summary.config.scenario} rows={summary.config.rows} dims={summary.config.dims} "
        f"bins={summary.config.bins}: {summary.elapsed_seconds:.3f} s, "
        f"{summary.samples} samples @ {summary.rate_hz:g} Hz"
    )
    lines = [header, f"{'self %':>8}  frame"]
    for frame, count in summary.self_counts.most_common(top):
        lines.append(f"{100.0 * count / total:8.2f}  {frame}")
    return "\n".join(lines)


def _parse_int_list(raw: str) -> list[int]:
    return [int(token) for token in raw.split(",") if token.strip()]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sample-profile the ScoreQuant solver matrix.")
    parser.add_argument("--scenarios", type=str, default="d_exchange")
    parser.add_argument("--rows", type=str, default="100000")
    parser.add_argument("--dims", type=int, default=8)
    parser.add_argument("--bins", type=str, default="64")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-scans", type=int, default=None)
    parser.add_argument("--rate", type=float, default=_DEFAULT_RATE_HZ)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--top", type=int, default=_DEFAULT_TOP)
    parser.add_argument("--json", type=Path, default=None)
    parser.add_argument("--folded-dir", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Profile every requested matrix cell, checkpointing after each one."""
    args = _build_parser().parse_args(argv)
    scenarios = [token.strip() for token in args.scenarios.split(",") if token.strip()]
    for name in scenarios:
        if name not in _SCENARIO_NAMES:
            raise SystemExit(f"unknown scenario {name!r}; choose from {', '.join(_SCENARIO_NAMES)}")
    records = {} if args.force else _load_checkpoint(args.json)

    for scenario in scenarios:
        dims = _scenario_dims(scenario, args.dims)
        for rows in _parse_int_list(args.rows):
            for bins in _parse_int_list(args.bins):
                cfg = ScenarioConfig(scenario, rows, dims, bins, args.seed, args.max_scans)
                key = _cell_key(cfg)
                if key in records:
                    print(f"resume: {key} already recorded")
                    continue
                reason = _skip_reason(scenario, rows, dims, bins)
                if reason is not None:
                    print(f"skip: {key}: {reason}")
                    continue
                summary = _profile_cell(cfg, args.rate, args.warmups)
                print(_format_summary(summary, args.top))
                print()
                if args.folded_dir is not None:
                    _write_folded(summary, args.folded_dir)
                records[key] = summary.to_json(args.top)
                if args.json is not None:
                    _save_checkpoint(args.json, records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
