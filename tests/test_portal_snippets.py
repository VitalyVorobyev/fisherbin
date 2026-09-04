"""Execute every Python snippet the portal publishes.

Two surfaces, one contract -- a published snippet runs, and it produces a
fitted result rather than merely parsing.

``website/src/pages/docs.tsx`` holds `code:` template literals, extracted and
unescaped back into Python and executed against a small shared fixture
namespace.

``website/walkthroughs/*.mdx`` holds the four walkthrough pages. Their fences
are ordinary Markdown code fences, so they reuse ``_extract_blocks`` from
``tests/test_docs_snippets.py`` rather than a second extractor; the markers
there are written ``{/* snippet: skip */}`` because MDX 3 rejects HTML
comments. Unlike the `docs.tsx` snippets, a walkthrough executes in its own
**fresh** namespace with no pre-seeded fixture, cumulatively across that
page's fences: a walkthrough must run as shown, because a reader is meant to
be able to reproduce it from what is on the page. The result assertion is per
page rather than per fence, since the arc reaches a fit once.

These fences execute published prose, so this module carries the
``docs_execution`` marker that ``tests/conftest.py`` assigns to that tier.

See ``docs/programme/S08-the-four-walkthroughs.md``, decision D3.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import numpy as np
import pytest

import scorequant as sq
from tests.test_docs_snippets import Snippet, _extract_blocks

ROOT = Path(__file__).parents[1]
DOCS_TSX = ROOT / "website/src/pages/docs.tsx"
WALKTHROUGHS = ROOT / "website/walkthroughs"

#: The four walkthroughs this session published. Named rather than globbed so
#: that a page silently failing to be discovered is a test failure instead of a
#: quietly smaller run.
EXPECTED_WALKTHROUGHS = ("flowcyt", "hep", "michelson", "ratios")


def _peak_pdf(observations: object) -> np.ndarray:
    """Gaussian bump on column 0, matching the Door 2 component model."""
    x = np.asarray(observations)[:, 0]
    return np.exp(-0.5 * ((x - 1.0) / 0.4) ** 2)


def _flat_pdf(observations: object) -> np.ndarray:
    """Flat component: ones, matching the Door 2 component model."""
    return np.ones(np.asarray(observations).shape[0])


class _DeterministicClassifier:
    """A cheap, deterministic stand-in for a calibrated two-class classifier.

    ``predict_proba`` is a logistic function of the observation's first
    column; rows are already nonnegative and sum to one, matching the
    "calibrated posteriors" contract ``DensityRatioScore.from_classifier``
    expects (see `website/walkthroughs/ratios.mdx`, "From posteriors to a
    score").
    """

    def predict_proba(self, observations: object) -> np.ndarray:
        x = np.asarray(observations)[:, 0]
        signal_probability = 1.0 / (1.0 + np.exp(-1.5 * x))
        return np.stack([1.0 - signal_probability, signal_probability], axis=1)


def _fixture_namespace() -> dict[str, object]:
    """A fresh namespace holding every free variable the portal snippets use.

    Small and deterministic: 300 rows is enough for a 6-bin D-exchange fit
    to run quickly while still exercising the real solver path.
    """
    rng = np.random.default_rng(0)
    scores = rng.normal(size=(300, 2))
    weights = np.ones(scores.shape[0])

    class_priors = [0.5, 0.5]
    fractions = [0.3, 0.7]
    is_signal = rng.random(300) < fractions[1]
    mixture = np.where(is_signal, rng.normal(1.0, 0.5, 300), rng.normal(0.0, 1.5, 300))[:, None]
    source = sq.ObservationSample(mixture)

    return {
        "sq": sq,
        "np": np,
        "scores": scores,
        "weights": weights,
        "peak_pdf": _peak_pdf,
        "flat_pdf": _flat_pdf,
        "classifier": _DeterministicClassifier(),
        "class_priors": class_priors,
        "fractions": fractions,
        "source": source,
    }


def _extract_snippets() -> list[tuple[str, str]]:
    """Return ``(eyebrow, code)`` pairs for every door, in source order."""
    source = DOCS_TSX.read_text()
    eyebrows = re.findall(r'eyebrow: "([^"]*)"', source)
    escaped_snippets = re.findall(r"code: `([^`]*)`", source)
    assert escaped_snippets
    assert len(eyebrows) == len(escaped_snippets)
    snippets = [escaped.replace(r"\n", "\n").replace(r"\"", '"') for escaped in escaped_snippets]
    return list(zip(eyebrows, snippets, strict=True))


_SNIPPETS = _extract_snippets()


@pytest.mark.parametrize("eyebrow, code", _SNIPPETS, ids=[eyebrow for eyebrow, _ in _SNIPPETS])
def test_portal_snippet_executes_and_produces_a_result(eyebrow: str, code: str) -> None:
    namespace = _fixture_namespace()
    exec(compile(code, f"website/src/pages/docs.tsx:{eyebrow}", "exec"), namespace)  # noqa: S102

    produced = namespace.get("result") or namespace.get("quantizer")
    assert isinstance(produced, (sq.PartitionResult, sq.QuantizerResult)), (
        f"snippet {eyebrow!r} did not bind `result` or `quantizer` to a fitted result"
    )


@pytest.mark.parametrize("eyebrow, code", _SNIPPETS, ids=[eyebrow for eyebrow, _ in _SNIPPETS])
def test_portal_snippet_uses_public_symbols(eyebrow: str, code: str) -> None:
    public = set(sq.__all__)
    tree = ast.parse(code, filename=f"website/src/pages/docs.tsx:{eyebrow}")
    referenced = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "sq"
    }
    assert referenced <= public, f"portal snippet {eyebrow!r} uses private or missing names"


def _walkthrough_pages() -> list[tuple[str, list[Snippet]]]:
    """Return ``(slug, blocks)`` for every walkthrough page carrying a fence."""
    pages = []
    for path in sorted(WALKTHROUGHS.glob("*.mdx")):
        if path.stem == "index":
            continue
        blocks = _extract_blocks(path.read_text(encoding="utf-8"))
        if blocks:
            pages.append((path.stem, blocks))
    return pages


_WALKTHROUGHS = _walkthrough_pages()


def test_every_walkthrough_was_discovered() -> None:
    """All four walkthroughs exist and carry executable fences.

    `docs/three-doors.md` was retired into these pages in S8; if one stops being
    discovered, the fences it absorbed stop running and the coverage the
    programme required to survive that retirement is gone.
    """
    assert [slug for slug, _ in _WALKTHROUGHS] == sorted(EXPECTED_WALKTHROUGHS)


@pytest.mark.parametrize("slug, blocks", _WALKTHROUGHS, ids=[slug for slug, _ in _WALKTHROUGHS])
def test_walkthrough_fences_execute_and_produce_a_result(slug: str, blocks: list[Snippet]) -> None:
    """Run one walkthrough's fences in order, in a namespace it builds itself."""
    namespace: dict[str, object] = {}
    for block in blocks:
        if block.fresh:
            namespace = {}
        if block.skip:
            continue
        filename = f"website/walkthroughs/{slug}.mdx:block{block.index}"
        exec(compile(block.code, filename, "exec"), namespace)  # noqa: S102

    produced = [
        value
        for value in namespace.values()
        if isinstance(value, (sq.PartitionResult, sq.QuantizerResult))
    ]
    assert produced, (
        f"walkthrough {slug!r} never bound a PartitionResult or QuantizerResult; "
        "a walkthrough must carry its narrative all the way to a fit"
    )


@pytest.mark.parametrize("slug, blocks", _WALKTHROUGHS, ids=[slug for slug, _ in _WALKTHROUGHS])
def test_walkthrough_fences_use_public_symbols(slug: str, blocks: list[Snippet]) -> None:
    """Every ``sq.<name>`` a walkthrough shows is in the public API."""
    public = set(sq.__all__)
    for block in blocks:
        tree = ast.parse(block.code, filename=f"website/walkthroughs/{slug}.mdx:{block.index}")
        referenced = {
            node.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "sq"
        }
        assert referenced <= public, (
            f"walkthrough {slug!r} block {block.index} uses private or missing names: "
            f"{sorted(referenced - public)}"
        )
