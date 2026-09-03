"""Execute the docs portal's "three doors" code snippets end to end.

The snippets in ``website/src/pages/docs.tsx`` are marketing copy, but they
are marketing copy that claims to run. This module extracts each `code:`
template literal, unescapes it back into Python source, executes it against a
small shared fixture namespace, and asserts it actually produced a
:class:`~scorequant.PartitionResult` or :class:`~scorequant.QuantizerResult`
-- the same contract the reference documentation in `docs/three-doors.md`
demonstrates for the same three doors.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import numpy as np
import pytest

import scorequant as sq

ROOT = Path(__file__).parents[1]
DOCS_TSX = ROOT / "website/src/pages/docs.tsx"


def _peak_pdf(observations: object) -> np.ndarray:
    """Gaussian bump on column 0, matching docs/three-doors.md Door 2."""
    x = np.asarray(observations)[:, 0]
    return np.exp(-0.5 * ((x - 1.0) / 0.4) ** 2)


def _flat_pdf(observations: object) -> np.ndarray:
    """Flat component: ones, matching docs/three-doors.md Door 2."""
    return np.ones(np.asarray(observations).shape[0])


class _DeterministicClassifier:
    """A cheap, deterministic stand-in for a calibrated two-class classifier.

    ``predict_proba`` is a logistic function of the observation's first
    column; rows are already nonnegative and sum to one, matching the
    "calibrated posteriors" contract ``DensityRatioScore.from_classifier``
    expects (see docs/three-doors.md, "From ratios to scores").
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
