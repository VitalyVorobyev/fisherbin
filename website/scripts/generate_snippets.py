"""Generate the captured-output snippets the ``/get-started`` page renders.

``get_started_program.py`` is the single source: one runnable Python program
split into cells by ``# %% cell: <id>`` markers. This script executes that
program's preamble once and then every cell in order, in one shared
namespace -- exactly what a reader gets running the file top to bottom -- and
captures each cell's stdout. The result is written to
``website/src/generated/snippet-outputs.json``, which
``website/src/lib/snippets.ts`` is the only typed reader of and
``website/src/components/Snippet.tsx`` renders one cell of.

Run through ``pnpm generate:snippets``, or directly::

    uv run python website/scripts/generate_snippets.py
    uv run python website/scripts/generate_snippets.py --check
"""

from __future__ import annotations

import argparse
import contextlib
import difflib
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import TypedDict

# Must run before the executed cells import scorequant: every cell prints a
# bit-reproducible number, which requires float64 and a headless matplotlib
# backend (imported only transitively, but never assumed absent).
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("JAX_ENABLE_X64", "1")

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = ROOT / "website/scripts/get_started_program.py"
OUTPUT = ROOT / "website/src/generated/snippet-outputs.json"

#: One ``# %% cell: <id>`` marker line. The id is the cell's lookup key in
#: the generated file and in ``website/src/lib/snippets.ts``.
_CELL_MARKER = re.compile(r"^# %% cell: (?P<id>[a-z0-9-]+)[ \t]*$", re.MULTILINE)

SCHEMA_VERSION = 1

#: Provenance recorded alongside every cell: the runtime ``get_started_program.py``
#: pins in its ``setup`` cell. A drift here would mean the program and this
#: script disagree about what they ran, which is worse than either being wrong
#: alone.
EXECUTION: dict[str, object] = {"backend": "numpy", "precision": "float64", "seed": 21}


class CellRecord(TypedDict):
    """One executed cell's verbatim source, captured stdout, and file order."""

    code: str
    stdout: str
    order: int


def split_cells(source: str) -> list[tuple[str, str]]:
    """Split ``source`` into ``(cell_id, code)`` pairs in file order.

    Parameters
    ----------
    source
        Full text of ``get_started_program.py``.

    Returns
    -------
    list of (str, str)
        Each cell's id and its source, stripped of the marker line and of
        the blank lines surrounding it. The module docstring before the
        first marker is preamble, never a cell.

    Raises
    ------
    ValueError
        No marker is found, or the same cell id is declared twice.
    """
    matches = list(_CELL_MARKER.finditer(source))
    if not matches:
        raise ValueError(f"{PROGRAM} has no '# %% cell: <id>' markers")
    seen: set[str] = set()
    cells: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        cell_id = match.group("id")
        if cell_id in seen:
            raise ValueError(f"duplicate cell id {cell_id!r} in {PROGRAM}")
        seen.add(cell_id)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        cells.append((cell_id, source[start:end].strip("\n")))
    return cells


def _preamble(source: str) -> str:
    """Return the source before the first cell marker (the module docstring)."""
    match = _CELL_MARKER.search(source)
    return source if match is None else source[: match.start()]


def run_program(source: str) -> dict[str, CellRecord]:
    """Execute the preamble, then every cell in order, in one shared namespace.

    Parameters
    ----------
    source
        Full text of ``get_started_program.py``.

    Returns
    -------
    dict
        Mapping of cell id to its code, captured stdout, and file order.
    """
    namespace: dict[str, object] = {"__name__": "__snippet_program__"}
    exec(compile(_preamble(source), str(PROGRAM), "exec"), namespace)
    records: dict[str, CellRecord] = {}
    for order, (cell_id, code) in enumerate(split_cells(source)):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exec(compile(code, f"{PROGRAM}:{cell_id}", "exec"), namespace)
        records[cell_id] = {"code": code, "stdout": buffer.getvalue(), "order": order}
    return records


def build_payload() -> dict[str, object]:
    """Run the program and assemble the JSON-ready generated payload."""
    source = PROGRAM.read_text(encoding="utf-8")
    cells = run_program(source)
    return {"schemaVersion": SCHEMA_VERSION, "execution": EXECUTION, "cells": cells}


def render(payload: dict[str, object]) -> str:
    """Serialize a payload exactly as it is committed: indented, newline-terminated."""
    return json.dumps(payload, indent=2) + "\n"


def main() -> None:
    """Write the generated snippet file, or verify it is already current."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed file matches a fresh run instead of writing it",
    )
    arguments = parser.parse_args()

    rendered = render(build_payload())

    if arguments.check:
        if not OUTPUT.exists():
            print(f"{OUTPUT.relative_to(ROOT)} does not exist; run without --check first")
            sys.exit(1)
        committed = OUTPUT.read_text(encoding="utf-8")
        if committed != rendered:
            diff = "".join(
                difflib.unified_diff(
                    committed.splitlines(keepends=True),
                    rendered.splitlines(keepends=True),
                    fromfile=f"committed {OUTPUT.relative_to(ROOT)}",
                    tofile="freshly generated",
                )
            )
            print(f"{OUTPUT.relative_to(ROOT)} is stale:\n{diff}")
            sys.exit(1)
        print(f"{OUTPUT.relative_to(ROOT)} matches a fresh run")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
