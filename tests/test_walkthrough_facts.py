"""Guard the portal walkthroughs' numbers against the evidence behind them.

The four walkthrough pages under ``website/walkthroughs/`` may not print a
number that no run produced. ``website/scripts/generate_walkthroughs.py``
enforces the first half of that by resolving every displayed value from a JSON
Pointer into a committed evidence file; this module enforces the second half by
re-resolving every pointer independently and checking the generated file still
agrees with the evidence.

Without this, the generator could compute anything and call it traceable, and a
re-run of any example would silently leave the portal quoting superseded
numbers. See ``docs/programme/S08-the-four-walkthroughs.md``, decision D2.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "website" / "scripts" / "generate_walkthroughs.py"
GENERATED = ROOT / "website" / "src" / "generated" / "walkthrough-data.json"


def _load_generator() -> ModuleType:
    name = "_scorequant_generate_walkthroughs"
    spec = importlib.util.spec_from_file_location(name, GENERATOR)
    assert spec is not None and spec.loader is not None, GENERATOR
    module = importlib.util.module_from_spec(spec)
    # Registered before execution because the generator defines a dataclass under
    # ``from __future__ import annotations``; resolving its field types looks the
    # defining module up in ``sys.modules``.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generator() -> ModuleType:
    assert GENERATOR.is_file(), GENERATOR
    return _load_generator()


@pytest.fixture(scope="module")
def generated() -> dict[str, object]:
    return json.loads(GENERATED.read_text(encoding="utf-8"))


def test_generated_file_is_current(generator: ModuleType, generated: dict[str, object]) -> None:
    """The committed facts equal what the generator produces from today's evidence.

    CI builds the portal from the committed generated file rather than
    regenerating it, so an example re-run that is not followed by
    ``pnpm generate`` would otherwise publish stale numbers.
    """
    assert generator.build() == generated, (
        "website/src/generated/walkthrough-data.json is stale; "
        "run `uv run python website/scripts/generate_walkthroughs.py`"
    )


def test_every_fact_resolves_to_its_cited_evidence(generated: dict[str, object]) -> None:
    """Each fact's value is what its own JSON Pointer selects from its own evidence file.

    Resolved here with an independent pointer walk rather than the generator's,
    so a bug in the generator's resolver cannot validate itself.
    """
    documents: dict[str, object] = {}
    pages = generated["pages"]
    assert isinstance(pages, dict) and pages, "no walkthrough facts were generated"
    for page, facts in pages.items():
        assert isinstance(facts, dict)
        for key, fact in facts.items():
            path, _, pointer = str(fact["source"]).partition("#")
            evidence_path = ROOT / path
            assert evidence_path.is_file(), f"{page}.{key} cites missing evidence {path}"
            document = documents.setdefault(
                path, json.loads(evidence_path.read_text(encoding="utf-8"))
            )
            current: object = document
            for raw in pointer.lstrip("/").split("/"):
                token = raw.replace("~1", "/").replace("~0", "~")
                if isinstance(current, list):
                    current = current[int(token)]
                else:
                    assert isinstance(current, dict), f"{page}.{key}: {pointer} hit a scalar"
                    assert token in current, f"{page}.{key}: {pointer} has no {token!r}"
                    current = current[token]
            assert current == fact["value"], f"{page}.{key} no longer matches {fact['source']}"


def test_every_fact_text_renders_its_own_value(generated: dict[str, object]) -> None:
    """The displayed string is a faithful rendering of the value it claims to show.

    A page prints ``text`` and never ``value``, so a text that disagrees with
    its value would put an unbacked number on the site while every pointer
    still resolved.
    """
    pages = generated["pages"]
    assert isinstance(pages, dict)
    for page, facts in pages.items():
        assert isinstance(facts, dict)
        for key, fact in facts.items():
            value, text = fact["value"], str(fact["text"])
            where = f"{page}.{key}"
            if isinstance(value, str):
                assert text == value, where
                continue
            assert isinstance(value, (int, float)), where
            cleaned = text.replace(",", "").rstrip("%")
            shown = float(cleaned)
            if text.endswith("%"):
                shown /= 100.0
            decimals = len(cleaned.partition(".")[2].partition("e")[0])
            tolerance = max(0.5 * 10.0**-decimals, abs(float(value)) * 1e-9)
            assert abs(shown - float(value)) <= tolerance, (
                f"{where}: text {text!r} does not render value {value!r}"
            )


def test_facts_only_cite_declared_evidence(
    generator: ModuleType, generated: dict[str, object]
) -> None:
    """No fact sources a number from a file outside the declared evidence set."""
    allowed = set(generator.EVIDENCE)
    pages = generated["pages"]
    assert isinstance(pages, dict)
    for page, facts in pages.items():
        assert isinstance(facts, dict)
        for key, fact in facts.items():
            path = str(fact["source"]).partition("#")[0]
            assert path in allowed, f"{page}.{key} cites undeclared evidence {path}"


# Numbers a walkthrough may write as a literal, each with the reason it is not a
# measurement. Anything else must come through `factsFor`, so that adding an
# unbacked number to a page is a deliberate, reviewed edit here rather than a
# silent one in prose.
_LITERAL_ALLOWLIST: dict[str, str] = {
    "1": "counting word: one door, one fit, one parameter",
    "2": "counting word: two contracts, two components, two columns",
    "3": "counting word: three doors",
    "4": "counting word: four walkthroughs",
    "10.5281": "the DOI prefix of the HEP fixture's Zenodo record",
}

_FENCE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
_JSX_EXPRESSION = re.compile(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", re.DOTALL)
_JSX_TAG = re.compile(r"<[^>]+>", re.DOTALL)
_FRONTMATTER = re.compile(r"\A---.*?^---", re.DOTALL | re.MULTILINE)
# MDX `import`/`export` statements are JavaScript, including any continuation
# lines, which are indented or close a bracket opened on the statement's line.
_ESM = re.compile(r"^(?:import|export)\s[^\n]*(?:\n(?:[ \t)\]}][^\n]*|)(?=[^\n]))*", re.MULTILINE)
# A measurement, as distinct from a digit inside a name. The boundary classes
# exclude digits adjacent to letters, hyphens or dots, so flow-cytometry marker
# nomenclature (``CD34``, ``FL5 INT_CD34-PC7``), licence identifiers
# (``CC-BY-4.0``) and record ids (``zenodo.15131565``) are not mistaken for
# numbers a page measured.
_NUMBER = re.compile(
    r"(?<![A-Za-z0-9._\-])\d+(?:[.,]\d+)*(?:e[+-]?\d+)?(?![A-Za-z0-9._\-])",
    re.IGNORECASE,
)


def _walkthrough_prose(text: str) -> str:
    """Return a page's prose, with code, JSX expressions and tags removed.

    A fact reaches the page as ``{f("key")}``, which is a JSX expression, so
    everything legitimately numeric disappears here and what remains is
    hand-typed prose.
    """
    for pattern in (_FRONTMATTER, _FENCE, _ESM, _JSX_EXPRESSION, _JSX_TAG):
        text = pattern.sub(" ", text)
    return text


@pytest.mark.parametrize(
    "path",
    sorted((ROOT / "website" / "walkthroughs").glob("*.mdx")),
    ids=lambda path: path.name,
)
def test_walkthrough_prose_contains_no_hand_typed_numbers(path: Path) -> None:
    """No measurement is typed into a walkthrough's prose.

    The generator and `factsFor` make a displayed number traceable; this makes
    *bypassing* them visible. Without it, "every number comes from evidence"
    would hold only for the numbers that happened to go through the helper.
    """
    offenders = sorted(
        {
            match.group(0)
            for match in _NUMBER.finditer(_walkthrough_prose(path.read_text(encoding="utf-8")))
            if match.group(0) not in _LITERAL_ALLOWLIST
        }
    )
    assert not offenders, (
        f"{path.name} writes {offenders} as literals; route each through "
        "factsFor(...) or add it to _LITERAL_ALLOWLIST with the reason it is not a measurement"
    )


# `flowcyt.mdx` is the one walkthrough that also reads a generated file directly:
# its three charts need series, not scalars, so they consume
# `website/src/generated/showcase-data.json` rather than going through
# `factsFor`. That is a deliberate exception -- a bar chart cannot be driven by
# formatted strings -- but it means those numbers sit outside the fact contract's
# three layers. This closes the gap that matters most: the committed file must
# still agree with the study it was generated from, so re-running the FlowCyt
# example without regenerating the portal data is a test failure rather than a
# quietly stale chart.
SHOWCASE_GENERATOR = ROOT / "website" / "scripts" / "generate_showcase.py"
SHOWCASE_DATA = ROOT / "website" / "src" / "generated" / "showcase-data.json"


def test_showcase_chart_data_is_current() -> None:
    """The committed FlowCyt chart series match what the study now produces."""
    name = "_scorequant_generate_showcase"
    spec = importlib.util.spec_from_file_location(name, SHOWCASE_GENERATOR)
    assert spec is not None and spec.loader is not None, SHOWCASE_GENERATOR
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    committed = json.loads(SHOWCASE_DATA.read_text(encoding="utf-8"))
    assert module.build_narrative() == committed, (
        "website/src/generated/showcase-data.json is stale; "
        "run `uv run python website/scripts/generate_showcase.py`"
    )
