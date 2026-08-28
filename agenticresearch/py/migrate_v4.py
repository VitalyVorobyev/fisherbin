"""One-shot migration of the scientific memory to the v4.0 layout.

Two mechanical moves, each verified against the artifact it replaces:

* ``split_known_results`` turns the 1400-line ``KNOWN_RESULTS.md`` into
  ``KNOWN_RESULTS/`` -- one file per chapter, plus an index carrying the status
  vocabulary and the cross-cutting chapters -- and rewrites every
  ``proof_location.file`` to match.
* ``shard_claims`` turns ``CLAIMS.json`` into ``claims/<id>.json`` plus
  ``registry.json``, drops the hand-maintained ``indexes`` block in favour of
  ``registry.py reindex``, and replaces ``priority`` with ``programme``.

Kept in the tree (moved to ``archive/`` after the run) so the migration diff is
reproducible rather than a pile of unexplained renames.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]

#: H1 chapter heading -> output filename. Chapter 5 splits again at DS11: the
#: bridge results (DS11-DS14) are 420 lines and interlock, the core ones do not.
CHAPTERS: list[tuple[str, str]] = [
    ("# 1. Universal information structure", "01-universal.md"),
    ("# 2. Trace control case", "02-trace.md"),
    ("# 3. Generic first-order and finite screening results", "03-screening.md"),
    ("# 4. Full D-optimality", "04-d-optimality.md"),
    (r"# 5. \(D_s\)-optimality", "05a-ds-core.md"),
    ("# 6. E-optimality control theory", "06-e-optimality.md"),
    ("# 7. A-optimality control theory", "07-a-optimality.md"),
    ("# 8. Randomized/soft quantizers and empirical geometric optimization", "08-soft.md"),
    ("# 9. Empirical-to-population theory", "09-consistency.md"),
    ("# 10. Score/density-ratio/classifier access", "10-oracle.md"),
    ("# 11. Information-efficiency outputs", "11-efficiency.md"),
]

#: Chapters 12-14 are cross-cutting summaries no claim points at; they belong
#: with the index, not with a criterion.
INDEX_CHAPTERS = (
    "# 12. Numerical evidence as regression tests — [MEASURED]",
    "# 13. Guarantee hierarchy",
    "# 14. Conservative novelty boundary",
)

DS_BRIDGE_FILE = "05b-ds-bridge.md"
DS_BRIDGE_SPLIT = "## DS11."

BANNER = (
    "> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and\n"
    "> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.\n"
    "> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.\n"
)


def _blocks(lines: list[str]) -> dict[str, list[str]]:
    """Slice the ledger at its H1 headings, keyed by heading text."""
    out: dict[str, list[str]] = {}
    key = "__preamble__"
    buffer: list[str] = []
    for line in lines:
        if line.startswith("# "):
            out[key] = buffer
            key = line.rstrip()
            buffer = []
        else:
            buffer.append(line)
    out[key] = buffer
    return out


def split_known_results(workspace: Path = WORKSPACE) -> None:
    source = workspace / "KNOWN_RESULTS.md"
    lines = source.read_text().splitlines()
    blocks = _blocks(lines)

    target = workspace / "KNOWN_RESULTS"
    target.mkdir(exist_ok=True)

    title = "# Known results and current project theory"
    preamble = "\n".join(blocks[title]).strip()

    section_to_file: dict[str, str] = {}
    heading_pattern = re.compile(r"^## (.+?)(?: — \[.*\])?$")

    def record(body: list[str], filename: str) -> None:
        for line in body:
            match = heading_pattern.match(line)
            if match:
                section_to_file[match.group(1).strip()] = f"KNOWN_RESULTS/{filename}"

    def write(heading: str, body: list[str], filename: str, extra: str = "") -> None:
        text = f"{heading}\n\n{BANNER}{extra}\n" + "\n".join(body).rstrip() + "\n"
        (target / filename).write_text(re.sub(r"\n{3,}", "\n\n", text))

    ds_preamble: list[str] = []
    for heading, filename in CHAPTERS:
        body = blocks[heading]
        if filename == "05a-ds-core.md":
            cut = next(i for i, line in enumerate(body) if line.startswith(DS_BRIDGE_SPLIT))
            core, bridge = body[:cut], body[cut:]
            # DS0 defines the profiled objective; both Ds files need it standalone.
            ds0 = next(i for i, line in enumerate(core) if line.startswith("## DS0."))
            ds1 = next(i for i, line in enumerate(core) if line.startswith("## DS1."))
            ds_preamble = core[ds0:ds1]
            record(core, filename)
            write(heading, core, filename)
            # Repeat the notation, not the label: DS0 stays declared once, in
            # 05a, so result labels remain globally unique.
            formulas = [
                line
                for line in ds_preamble
                if not line.startswith(("## DS0.", "**Claims:**"))
            ]
            repeated = (
                "\n**Notation** (from DS0 in `05a-ds-core.md`, repeated so this file "
                "reads standalone).\n"
                + "\n".join(formulas).rstrip()
                + "\n"
            )
            record(bridge, DS_BRIDGE_FILE)
            write(
                r"# 5. \(D_s\)-optimality — finite-to-population bridge",
                bridge,
                DS_BRIDGE_FILE,
                extra=repeated,
            )
            continue
        record(body, filename)
        write(heading, body, filename)

    index = [
        "# Known results — index",
        "",
        "> Canonical theorem/result ledger, one file per chapter. Read `PROBLEM.md`",
        "> first. Resolve any claim id -- node, dependency closure, and proof prose --",
        "> with `python py/registry.py show <ID> --deps --proof`.",
        "",
        preamble,
        "",
        "## Chapters",
        "",
        "| Chapter | File | Results |",
        "|---|---|---|",
    ]
    listing = list(CHAPTERS)
    listing.insert(
        1 + next(i for i, (_, name) in enumerate(listing) if name == "05a-ds-core.md"),
        (r"# 5. \(D_s\)-optimality — finite-to-population bridge", DS_BRIDGE_FILE),
    )
    for heading, filename in listing:
        labels = sorted(
            {
                section.split(".")[0]
                for section, where in section_to_file.items()
                if where.endswith(filename)
            },
            key=lambda label: (re.sub(r"\d", "", label), int(re.sub(r"\D", "", label) or 0)),
        )
        index.append(f"| {heading[2:]} | `{filename}` | {', '.join(labels)} |")
    index.append("")
    for heading in INDEX_CHAPTERS:
        index.append(heading.replace("# ", "## ", 1))
        index.append("")
        index.append("\n".join(blocks[heading]).strip())
        index.append("")
    (target / "index.md").write_text("\n".join(index).rstrip() + "\n")

    registry_path = workspace / "CLAIMS.json"
    registry = json.loads(registry_path.read_text())
    moved = 0
    for claim in registry["claims"]:
        location = claim["proof_location"]
        if location["file"] != "KNOWN_RESULTS.md":
            continue
        hits = [s for s in section_to_file if s.startswith(location["section"])]
        if not hits:
            raise ValueError(f"{claim['id']}: section {location['section']!r} lost in the split")
        location["file"] = section_to_file[max(hits, key=len)]
        moved += 1
    registry["human_readable_ledger"] = "KNOWN_RESULTS/"
    registry_path.write_text(json.dumps(registry, indent=2) + "\n")
    source.unlink()
    print(f"split into {len(list(target.glob('*.md')))} files; {moved} proof_locations rewritten")


if __name__ == "__main__":
    split_known_results()
