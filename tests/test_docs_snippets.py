"""Execute the fenced Python snippets embedded in published documentation.

Every ```python fence in a page that MkDocs publishes is a claim about the
current API. This module discovers those pages from ``mkdocs.yml``, extracts
their fenced Python blocks in order, and executes each page's blocks
cumulatively in one shared namespace so the docs cannot silently drift from
the code they describe.

Two HTML-comment markers placed on the line immediately above a fence steer
execution:

- ``<!-- snippet: skip -->`` -- do not execute this block (pseudo-code or an
  illustrative fragment that depends on variables defined elsewhere in prose).
- ``<!-- snippet: fresh -->`` -- reset the accumulated namespace before this
  block runs.

Blocks without a marker execute in page order, sharing one namespace per
page; each page is isolated from every other page.
"""

from __future__ import annotations

import fnmatch
import os
import re
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
MKDOCS_CONFIG = REPO_ROOT / "mkdocs.yml"

_SKIP_MARKER = "snippet: skip"
_FRESH_MARKER = "snippet: fresh"

# An optional HTML-comment marker line directly above a ```python fence,
# followed by the fenced code itself.
_BLOCK_PATTERN = re.compile(
    r"(?:^(?P<marker><!--\s*snippet:\s*\w+\s*-->)\n)?^```python\n(?P<code>.*?)\n^```",
    re.DOTALL | re.MULTILINE,
)


@dataclass(frozen=True)
class Snippet:
    """One fenced Python block extracted from a documentation page.

    Parameters
    ----------
    index
        Zero-based position of the block among the page's Python fences.
    code
        Source text of the fenced block, without the surrounding fence.
    skip
        Whether the block carries a ``snippet: skip`` marker.
    fresh
        Whether the block carries a ``snippet: fresh`` marker.
    """

    index: int
    code: str
    skip: bool
    fresh: bool


def _load_exclude_patterns() -> list[str]:
    """Return the ``exclude_docs`` glob patterns from ``mkdocs.yml``.

    Uses ``yaml.safe_load`` when the config parses cleanly. Some MkDocs
    configurations carry ``!!python/...`` tags that ``safe_load`` rejects; in
    that case, fall back to a minimal manual parse of the ``exclude_docs``
    block scalar.
    """
    text = MKDOCS_CONFIG.read_text(encoding="utf-8")
    raw: str | None = None
    try:
        config = yaml.safe_load(text)
    except yaml.YAMLError:
        config = None
    if isinstance(config, dict) and isinstance(config.get("exclude_docs"), str):
        raw = config["exclude_docs"]
    if raw is None:
        raw = _manual_exclude_docs(text)
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _manual_exclude_docs(text: str) -> str:
    """Fall back parse of the ``exclude_docs:`` block scalar in raw text."""
    match = re.search(r"^exclude_docs:\s*\|\s*\n((?:[ \t]+\S.*\n?)+)", text, re.MULTILINE)
    return match.group(1) if match else ""


def _is_excluded(relative_page: Path, patterns: list[str]) -> bool:
    posix = relative_page.as_posix()
    return any(fnmatch.fnmatch(posix, pattern) for pattern in patterns)


def _published_pages() -> list[Path]:
    """Return published-page paths under ``docs/``, honoring ``exclude_docs``."""
    patterns = _load_exclude_patterns()
    return [
        path
        for path in sorted(DOCS_ROOT.rglob("*.md"))
        if not _is_excluded(path.relative_to(DOCS_ROOT), patterns)
    ]


def _extract_blocks(text: str) -> list[Snippet]:
    """Extract fenced ```python blocks from a page, in order."""
    blocks = []
    for index, match in enumerate(_BLOCK_PATTERN.finditer(text)):
        marker = match.group("marker") or ""
        blocks.append(
            Snippet(
                index=index,
                code=match.group("code"),
                skip=_SKIP_MARKER in marker,
                fresh=_FRESH_MARKER in marker,
            )
        )
    return blocks


def _snippet_pages() -> list[tuple[Path, list[Snippet]]]:
    """Return (page, blocks) pairs for every published page with a snippet."""
    pages = []
    for path in _published_pages():
        blocks = _extract_blocks(path.read_text(encoding="utf-8"))
        if blocks:
            pages.append((path, blocks))
    return pages


PAGES = _snippet_pages()
PAGE_IDS = [path.relative_to(DOCS_ROOT).as_posix() for path, _ in PAGES]


@pytest.mark.parametrize("page_path,blocks", PAGES, ids=PAGE_IDS)
def test_page_snippets_execute(page_path: Path, blocks: list[Snippet]) -> None:
    """Run a page's fenced Python blocks cumulatively in one namespace."""
    relative = page_path.relative_to(DOCS_ROOT).as_posix()
    namespace: dict[str, object] = {}
    try:
        for block in blocks:
            if block.fresh:
                namespace = {}
            if block.skip:
                continue
            filename = f"{relative}:block{block.index}"
            exec(compile(block.code, filename, "exec"), namespace)
    finally:
        plt.close("all")


def test_snippet_pages_were_discovered() -> None:
    """Guard against silent discovery failure hiding every page's coverage."""
    assert PAGES, "no published page with a Python snippet was discovered"
