# ADR 0006: Publish generated documentation through GitHub Pages

**Status:** Accepted

## Context

ScoreQuant has mathematical guides, executable examples, and a growing typed Python API. Hand-maintaining signatures in Markdown would drift from the implementation, while a future frontend should not become the documentation system for the scientific core.

## Decision

Use MkDocs with Material for MkDocs as the static documentation site and mkdocstrings-python to collect the curated public API from NumPy-style docstrings. Documentation dependencies live in a separate `docs` dependency group and package discovery uses the repository's `src` path.

Build documentation in strict mode on pull requests. After changes reach `main`, publish the generated `site/` artifact through GitHub's `configure-pages`, `upload-pages-artifact`, and `deploy-pages` Actions. Do not maintain a generated `gh-pages` branch.

## Consequences

Documentation signatures and prose are validated in CI, the site remains a static artifact with no service dependency, and Pages deployment receives only the permissions it needs. Public API changes now require useful docstrings as part of their implementation cost.

MathJax is loaded by the published site to render the existing mathematical notation. Analytics, version switching, and a custom web frontend remain outside this decision.
