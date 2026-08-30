from __future__ import annotations

import ast
import re
from pathlib import Path

import scorequant as sq

ROOT = Path(__file__).parents[1]


def test_react_learning_snippets_compile_and_use_public_symbols() -> None:
    source = (ROOT / "website/src/pages/docs.tsx").read_text()
    snippets = re.findall(r"code: `([^`]*)`", source)
    assert snippets
    public = set(sq.__all__)

    for index, escaped in enumerate(snippets):
        snippet = escaped.replace(r"\n", "\n")
        tree = ast.parse(snippet, filename=f"website/src/pages/docs.tsx:snippet{index}")
        referenced = {
            node.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "sq"
        }
        assert referenced <= public, f"portal snippet {index} uses private or missing names"
