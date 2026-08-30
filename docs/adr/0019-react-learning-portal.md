# ADR 0019: Add a React learning portal beside the engineering reference

**Status:** Accepted

**Supersedes in part:** [ADR 0006](0006-documentation-site.md)

## Context

ScoreQuant now has several kinds of material with incompatible reading and interaction needs:
task-first guidance, generated API reference, executable examples, a mathematical monograph,
benchmarks with provenance, and a research claim registry. MkDocs remains effective for exhaustive
Python and contributor reference, but it should not also own the product-level learning journeys,
interactive visual explanations, or an in-browser numerical workspace.

## Decision

Create an isolated TypeScript/React workspace in `website/`, compiled and routed by Docusaurus but
rendered through a completely custom ScoreQuant shell and component system. The top-level learning
routes are Docs, API, Examples, Theory, Benchmarks, Research, and Lab. Markdown, Python docstrings,
committed benchmark JSON, and an explicit public research allowlist remain authoritative; build
adapters generate portal data rather than introducing parallel hand-maintained sources.

The portal uses editorial light reading surfaces and a midnight-navy Lab. Its visual grammar is
derived from ScoreQuant data: score-space points, Voronoi cells, Fisher ellipses, and contours. It
uses self-hosted Space Grotesk, Inter, IBM Plex Mono, and mathematical fonts, a twelve-column
desktop grid, independent mobile composition, restrained radii and shadows, visible keyboard
focus, reduced-motion behavior, and print styling for theory.

The Lab owns its browser concerns. React speaks a versioned, backend-neutral protocol generated
from one JSON Schema to a Web Worker. The worker lazily loads a pinned local Pyodide runtime and a
local ScoreQuant wheel only on Lab interaction, runs ScoreQuant's NumPy backend, emits progress,
result, error, and cancellation events, and is terminated for cancellation. Browser limits are
explicit and inputs remain local. General routes must never request Pyodide or marimo assets.
Locked marimo WASM lessons may be embedded lazily; arbitrary-code notebooks are outside v1.

Initially MkDocs remains at the existing project root and the portal is published under
`/portal/` in the same static artifact. Moving React to the root and narrowing MkDocs to
`/reference/` requires content/link parity and an explicit redirect manifest. Deployment remains
preview-only until separately authorized.

## Consequences

MkDocs is still the exhaustive API, developer, and ADR reference. React becomes the curated
learning product and may link deeply to MkDocs rather than copying it. Griffe-generated API data,
benchmark provenance, research allowlisting, content snippet tests, Pagefind indexing, and
TypeScript strictness are enforced now by `portal-preview.yml`, which runs typecheck, lint, unit
tests, and the production build on every pull request. The Playwright desktop/mobile flows,
accessibility scan, and performance budgets exist in `website/tests/e2e/` but are not yet wired
into that workflow; they are gates for promoting the portal to the site root, not for the preview
artifact, and running them in CI is tracked as part of that promotion. The two toolchains stay isolated: Python is managed only by uv; `website/` uses its pinned
Node and pnpm versions.
