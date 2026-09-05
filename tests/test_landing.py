"""Guards for the landing page at the site root (ADR 0027).

The landing page is one hand-written HTML file with no build step, so nothing
executes its code or checks its links unless a test does. Three things are
pinned here:

- Its code block is byte-for-byte the first Python fence of ``README.md``,
  which ``test_readme`` executes. The landing page therefore never shows
  code no run executed.
- Every link into ``docs/`` names a page that exists in the MkDocs source. The
  portal side and the assembled tree are checked by
  ``website/scripts/assemble-site.mjs`` after the build.
- Its prose carries no measured number. Numbers drift; the pages behind the
  links own them.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LANDING = REPO_ROOT / "landing" / "index.html"
README = REPO_ROOT / "README.md"


def _landing() -> str:
    return LANDING.read_text(encoding="utf-8")


def test_landing_code_block_is_the_readme_quickstart() -> None:
    fences = re.findall(r"```python\n(.*?)```", README.read_text(encoding="utf-8"), flags=re.S)
    assert fences, "README.md carries no Python fence to mirror"
    blocks = re.findall(r"<pre><code>(.*?)</code></pre>", _landing(), flags=re.S)
    assert len(blocks) == 1, "the landing page carries exactly one code block"
    assert html.unescape(blocks[0]) == fences[0]


def test_landing_docs_links_resolve_to_pages() -> None:
    hrefs = re.findall(r'href="(docs/[^"#?]*)"', _landing())
    assert hrefs
    for href in hrefs:
        relative = href[len("docs/") :]
        assert relative == "" or relative.endswith("/"), href
        page = (
            REPO_ROOT
            / "docs"
            / (
                f"{relative}index.md"
                if relative == "" or (REPO_ROOT / "docs" / relative).is_dir()
                else f"{relative.rstrip('/')}.md"
            )
        )
        assert page.is_file(), (href, page)


def test_landing_links_to_both_surfaces() -> None:
    text = _landing()
    assert 'href="docs/"' in text
    assert 'href="portal/"' in text


def test_landing_prose_carries_no_measured_number() -> None:
    text = re.sub(r"<pre>.*?</pre>", "", _landing(), flags=re.S)
    text = re.sub(r"<head>.*?</head>", "", text, flags=re.S)
    prose = re.sub(r"<[^>]+>", " ", text)
    # A version like 3.12 is allowed; a retention like 0.9853 or a row count
    # like 20000 is what this forbids.
    offenders = re.findall(r"\d+\.\d{3,}|\d{3,}|\d+\s?%", prose)
    assert offenders == [], offenders
