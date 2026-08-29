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


#: Programme queue, product-first. `rank` is the order OPEN_PROBLEMS.md declares;
#: `readiness` is the field the selection rule ("the highest programme that is not
#: blocked") always assumed but nothing recorded. Nothing is blocked today.
PROGRAMMES: dict[str, dict] = {
    "P1": {
        "title": "DS-POPULATION-BRIDGE — finish practical Ds theory",
        "rank": 1,
        "readiness": "ready",
        "kind": "theorem",
    },
    "P2": {
        "title": "SCORE-ORACLE-ROBUSTNESS — estimated scores and classifiers",
        "rank": 2,
        "readiness": "ready",
        "kind": "theorem",
    },
    "P3": {
        "title": "INFORMATION-BUDGET — how many bins does a target need",
        "rank": 3,
        "readiness": "ready",
        "kind": "theorem",
    },
    "P4": {
        "title": "DEPLOYMENT-ROBUSTNESS — away from the reference point, with error bars",
        "rank": 4,
        "readiness": "ready",
        "kind": "theorem",
    },
    "P5": {
        "title": "HEP-SPECIALIZATION — template fits made mathematically explicit",
        "rank": 5,
        "readiness": "ready",
        "kind": "theorem",
    },
    "P6": {
        "title": "D-CORE-COMPLETION — the paper's remaining spine",
        "rank": 6,
        "readiness": "ready",
        "kind": "theorem",
    },
    "P7": {
        "title": "FOUNDATIONS — why D is special, complexity, randomization",
        "rank": 7,
        "readiness": "ready",
        "kind": "theorem",
    },
    "P8": {
        "title": "LITERATURE-GRAPH — coverage you can defend",
        "rank": 8,
        "readiness": "ready",
        "kind": "infrastructure",
    },
}

HEADER_KEYS = (
    "schema_version",
    "project",
    "updated",
    "canonical_problem_file",
    "human_readable_ledger",
    "open_problem_ledger",
    "counterexample_directory",
    "purpose",
    "status_definitions",
    "publication_status_definitions",
    "literature_search_status_definitions",
    "levels",
    "criteria",
    "primary_objectives",
    "primary_problem_levels",
    "score_oracle_regimes",
    "primary_application",
    "required_outputs",
    "programmes",
    "bibliography",
    "agent_usage",
)


#: Open claims documented outside OPEN_PROBLEMS.md. E6 is an open question stated
#: inline in the E-optimality chapter with no OP number of its own; it belongs to
#: the foundations programme, which also decides whether an E solver is ever built.
PROGRAMME_OVERRIDES = {"OPEN-E-COMMON-SUPERGRADIENT": "P7"}


def _programme_of_open_problem(workspace: Path) -> dict[str, str]:
    """Map each ``OPn.`` heading in OPEN_PROBLEMS.md to the programme above it."""
    mapping: dict[str, str] = {}
    current: str | None = None
    for line in (workspace / "OPEN_PROBLEMS.md").read_text().splitlines():
        programme = re.match(r"^# (P\d) ·", line)
        if programme:
            current = programme.group(1)
            continue
        heading = re.match(r"^## (OP\d+)\.", line)
        if heading and current:
            mapping[heading.group(1)] = current
    return mapping


def shard_claims(workspace: Path = WORKSPACE) -> None:
    source = workspace / "CLAIMS.json"
    registry = json.loads(source.read_text())
    claims = registry["claims"]
    original = {claim["id"]: json.dumps(claim, sort_keys=True) for claim in claims}

    programme_of = _programme_of_open_problem(workspace)
    directory = workspace / "claims"
    directory.mkdir(exist_ok=True)
    tagged = 0
    for claim in claims:
        claim.pop("priority", None)
        if claim["status"] == "open":
            section = claim["proof_location"]["section"]
            key = section.split(".")[0]
            programme = PROGRAMME_OVERRIDES.get(claim["id"]) or programme_of.get(key)
            if programme is None:
                raise ValueError(f"{claim['id']}: no programme for {section!r}")
            claim["programme"] = programme
            tagged += 1
        (directory / f"{claim['id']}.json").write_text(json.dumps(claim, indent=2) + "\n")

    header = {key: registry[key] for key in HEADER_KEYS if key in registry}
    header["schema_version"] = "4.0"
    header["programmes"] = PROGRAMMES
    # search_gap is a literature_search_status, never a claim status; declaring it
    # in both vocabularies is what let AGENT.md conflate them.
    header["status_definitions"].pop("search_gap", None)
    header["purpose"] = (
        "Machine-readable theorem/claim registry: one file per claim under claims/, "
        "with the shared vocabularies here. Use dependencies/implies as a theorem "
        "dependency graph; resolve a branch with `python py/registry.py show <ID> "
        "--deps --proof` rather than reading the directory linearly. Indexes are "
        "generated by `py/registry.py reindex`, never hand-maintained."
    )
    header["agent_usage"] = {
        "read_order": [
            "README.md defines the single canonical read order; follow it rather than any local copy."
        ],
        "rules": [
            "Resolve a claim with `python py/registry.py show <ID> --deps --proof`.",
            "Browse claims/INDEX.md (generated) to pick work; it is grouped by programme in queue order.",
            "Never hand-edit an index; run `python py/registry.py reindex`.",
            "Run `python py/registry.py validate` before finishing a session.",
        ],
        "example_queries": [
            "python py/registry.py show OPEN-DS-MARGINS-AT-OPTIMA --deps",
            "python py/registry.py show DS-EXCHANGE-LEVERAGE-BOUND --proof",
        ],
    }
    (workspace / "registry.json").write_text(json.dumps(header, indent=2) + "\n")
    source.unlink()

    # every node must survive byte-identically apart from the two intended edits
    rebuilt = {}
    for path in sorted(directory.glob("*.json")):
        node = json.loads(path.read_text())
        node.pop("programme", None)
        rebuilt[node["id"]] = json.dumps(node, sort_keys=True)
    stripped = {}
    for claim_id, blob in original.items():
        node = json.loads(blob)
        node.pop("priority", None)
        stripped[claim_id] = json.dumps(node, sort_keys=True)
    assert rebuilt == stripped, "sharding changed claim content"
    print(f"sharded {len(claims)} claims; {tagged} tagged with a programme")


#: LITERATURE.md chapter -> topic file. Chapters 7 (reading order) and 8 (search
#: vocabulary) are workflow, not paper records, and move to the index.
LITERATURE_TOPICS: list[tuple[str, str]] = [
    ("# 1. Optimal experimental design backbone", "01-optimal-design.md"),
    ("# 2. Fisher-information quantization", "02-fisher-quantization.md"),
    ("# 3. Determinant clustering and partition exchange", "03-determinant-clustering.md"),
    ("# 4. Vector quantization and Voronoi theory", "04-vector-quantization.md"),
    ("# 5. Inference-aware summaries and HEP categorization", "05-hep-inference-aware.md"),
    ("# 6. Software landscape", "06-software-landscape.md"),
    (
        "# 9. Additional score-compression and ratio-estimation sources (v2 update)",
        "07-score-compression.md",
    ),
]

LITERATURE_WORKFLOW = ("# 7. Paper reading order for literature study", "# 8. Search vocabulary for new prior art")

#: Heading prefix -> bibliography keys. The registry's keys never matched the
#: prose headings, so `claims[].literature[]` resolved to nothing; a **Key:** line
#: under each heading closes that path, mirroring **Claims:** in KNOWN_RESULTS.
BIB_ANCHORS: dict[str, list[str]] = {
    "Kiefer & Wolfowitz (1960)": ["Kiefer-Wolfowitz-1960"],
    "Wynn (1970)": ["Wynn-1970"],
    "Wynn (1972)": ["Wynn-1972"],
    "Whittle (1973)": ["Whittle-1973"],
    "Kiefer (1974)": ["Kiefer-1974"],
    "Näther & Reinsch (1981)": ["Nather-Reinsch-1981"],
    "Venkitasubramaniam, Tong & Swami (2006)": ["Venkitasubramaniam-Tong-Swami-2006"],
    "Farias & Brossier (2013/2014)": ["Farias-Brossier-2013"],
    "Barnes, Han & Özgür (2018)": ["Barnes-Han-Ozgur-2018"],
    "Dülek (2023)": ["Dulek-2023"],
    "Domain-specific D-optimal threshold quantizers": ["Jiang-et-al-2026"],
    "Friedman & Rubin (1967)": ["Friedman-Rubin-1967"],
    "Scott & Symons (1971)": ["Scott-Symons-1971"],
    "Späth (1977)": ["Spaeth-1977"],
    "Späth (1985)": ["Spaeth-1985"],
    "Coleman, Dong, Hardin, Rocke & Woodruff (1999)": ["Coleman-et-al-1999"],
    "Pollard (1981, 1982) and the k-means consistency cluster": ["Pollard-1981"],
    "Du, Faber & Gunzburger (1999)": ["Du-Faber-Gunzburger-1999"],
    "Richter & Alexa (2015)": ["Richter-Alexa-2015"],
    "Targeted audit for the DS-POPULATION-BRIDGE claims": ["Li-Mathias-2000"],
}

LITERATURE_BANNER = (
    "> Curated theorem-level annotations. Machine records for the citation graph\n"
    "> live in `graph.json`; `BIBLIOGRAPHY.md` (generated) maps every registry\n"
    "> bibliography key to the heading that annotates it.\n"
)


def _annotate_bib_keys(lines: list[str]) -> list[str]:
    """Insert a ``**Key:**`` line under every heading that anchors a bib key."""
    out: list[str] = []
    for line in lines:
        out.append(line)
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip()
        for prefix, keys in BIB_ANCHORS.items():
            if heading.startswith(prefix):
                out.append("")
                out.append(f"**Key:** {', '.join(keys)}")
                break
    return out


def split_literature(workspace: Path = WORKSPACE) -> None:
    source = workspace / "LITERATURE.md"
    blocks = _blocks(source.read_text().splitlines())
    target = workspace / "LITERATURE"
    (target / "topics").mkdir(parents=True, exist_ok=True)
    (target / "audits").mkdir(exist_ok=True)

    def extract_audits(body: list[str]) -> tuple[list[str], list[tuple[str, list[str]]]]:
        """Pull dated targeted-audit blocks out of a topical chapter."""
        kept: list[str] = []
        audits: list[tuple[str, list[str]]] = []
        current: list[str] | None = None
        heading = ""
        for line in body:
            if line.startswith("### Targeted audit"):
                if current is not None:
                    audits.append((heading, current))
                heading, current = line, [line]
                continue
            if current is not None and (line.startswith("## ") or line.startswith("# ")):
                audits.append((heading, current))
                current = None
            (current if current is not None else kept).append(line)
        if current is not None:
            audits.append((heading, current))
        return kept, audits

    collected: list[tuple[str, list[str]]] = []
    for heading, filename in LITERATURE_TOPICS:
        body, audits = extract_audits(blocks[heading])
        collected.extend(audits)
        body = _annotate_bib_keys(body)
        text = f"{heading}\n\n{LITERATURE_BANNER}\n" + "\n".join(body).rstrip() + "\n"
        (target / "topics" / filename).write_text(re.sub(r"\n{3,}", "\n\n", text))

    for heading, body in collected:
        claim = re.search(r"`?([A-Z][A-Z0-9-]+)`?", heading.split("for")[1])
        date = re.search(r"(\d{1,2} \w+ \d{4})", heading)
        slug = f"{claim.group(1) if claim else 'audit'}-{(date.group(1) if date else '').replace(' ', '-')}"
        body = _annotate_bib_keys([line.replace("### ", "# ", 1) for line in body])
        (target / "audits" / f"{slug}.md").write_text("\n".join(body).rstrip() + "\n")

    index = [
        "# Literature — index",
        "",
        "> Discovery state for the ScoreQuant prior-art search. Procedure lives in",
        "> `protocols/literature.md`; PDFs, where held, are in `../../papers/`.",
        "",
        "\n".join(blocks["__preamble__"]).strip(),
        "",
        "## Files",
        "",
        "| File | Role |",
        "|---|---|",
        "| `BIBLIOGRAPHY.md` | **Generated.** Registry bibliography key -> annotating heading. |",
        "| `topics/` | Curated theorem-level annotations, one file per research community. |",
        "| `audits/` | Dated targeted prior-art searches, one per audited claim. |",
        "| `graph.json` | Machine paper records for citation snowballing (`rounds`, `papers`). |",
        "| `seeds.md` | Anchor papers for bidirectional traversal. |",
        "| `reviewed.md`, `rejected.md`, `gaps.md` | Human-readable outcomes and coverage gaps. |",
        "",
        "## Topics",
        "",
    ]
    for heading, filename in LITERATURE_TOPICS:
        index.append(f"- `topics/{filename}` — {heading[2:]}")
    index.append("")
    for heading in LITERATURE_WORKFLOW:
        index.append(heading.replace("# ", "## ", 1))
        index.append("")
        index.append("\n".join(blocks[heading]).strip())
        index.append("")
    (target / "index.md").write_text(re.sub(r"\n{3,}", "\n\n", "\n".join(index).rstrip() + "\n"))
    source.unlink()
    print(
        f"literature split into {len(LITERATURE_TOPICS)} topics "
        f"and {len(collected)} audit records"
    )
