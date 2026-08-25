from __future__ import annotations

import re
from pathlib import Path

import numpy as np


def test_readme_quickstart_is_executable_and_deterministic() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    match = re.search(
        r"<!-- quickstart-test:start -->\s*```python\n(.*?)\n```\s*"
        r"<!-- quickstart-test:end -->",
        readme,
        flags=re.DOTALL,
    )
    assert match is not None
    namespace: dict[str, object] = {}
    exec(compile(match.group(1), "README.md", "exec"), namespace)
    np.testing.assert_array_equal(np.sort(namespace["counts"]), [200, 485, 547, 768])
    quantizer = namespace["quantizer"]
    assert np.isclose(quantizer.train_report.geometric_mean_retention, 0.8824679259859257)


def test_readme_contains_only_current_user_facing_language() -> None:
    readme = Path("README.md").read_text(encoding="utf-8").lower()
    forbidden = ("roadmap", "adr", "pre-release", "migration history", "development phase")
    assert all(term not in readme for term in forbidden)


def test_published_markdown_has_no_internal_or_malformed_content() -> None:
    excluded_files = {
        Path("docs/development.md"),
        Path("docs/method.md"),
        Path("docs/motivation.md"),
        Path("docs/roadmap.md"),
        Path("docs/system-design.md"),
    }
    published = [
        path
        for path in Path("docs").rglob("*.md")
        if path not in excluded_files and "adr" not in path.parts
    ]
    forbidden = ("roadmap", "pre-release", "migration history", "development phase")
    for path in published:
        content = path.read_text(encoding="utf-8")
        assert "\t" not in content, f"tab character in {path}"
        lowered = content.lower()
        assert all(term not in lowered for term in forbidden), path

    mkdocs = Path("mkdocs.yml").read_text(encoding="utf-8")
    for excluded in ("development.md", "roadmap.md", "system-design.md", "adr/**"):
        assert excluded in mkdocs
