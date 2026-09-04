# ADR 0025: Serve the portal at the site root and MkDocs at `/reference/`

**Status:** Superseded by [ADR 0027](0027-landing-page-at-the-root.md), which moves the portal to
`/portal/`, the documentation to `/docs/`, and puts a landing page at the root

**Completes:** [ADR 0019](0019-react-learning-portal.md) stage 2

**Amended by:** [ADR 0026](0026-one-workflow-publishes-the-site.md), which lifts the deployment
freeze recorded under Decision below

## Context

ADR 0019 created the React portal and deliberately staged its rollout: "Initially MkDocs remains
at the existing project root and the portal is published under `/portal/` in the same static
artifact. Moving React to the root and narrowing MkDocs to `/reference/` requires content/link
parity and an explicit redirect manifest."

Three things changed since that decision.

The package shipped. `scorequant 0.1.0` went to PyPI on 30 August 2026 advertising
`https://vitalyvorobyev.github.io/scorequant/` as both Homepage and Documentation. That URL is now
the project's front door for every reader who arrives through the package index, and it lands them
on the reference index — an exhaustive API and method site — rather than on any explanation of
what the library is for.

The portal never shipped. `portal-preview.yml` builds it and uploads a CI artifact; nothing is
deployed. The one asset that most helps a new reader — the Lab, which runs the real ScoreQuant
wheel in the browser under Pyodide with no install — is reachable only from a nav link on a site
nobody can visit.

And the material split cleanly. The portal's job is explanation and facilitation: what problem
this solves, how to use it, and detailed walkthroughs of realistic examples. MkDocs' job is the
exhaustive reference: the generated API, the method write-up, the monograph, the evidence
studies, the gallery. Neither needs to own the other's URL space, but one of them has to own the
root, and the root should belong to explanation.

## Decision

The portal is served at the site root and MkDocs beneath it at `/reference/`.

The assembled tree is produced by `website/scripts/assemble-site.mjs`: the Docusaurus build at the
root, the MkDocs build under `reference/`, and a static redirect stub at every pre-cut MkDocs URL.
Static stubs — `<meta http-equiv="refresh">` plus `rel=canonical`, `noindex`, and a visible link
for a reader whose browser blocks the refresh — are the only mechanism available, because GitHub
Pages has no server-side rewrite.

The parity ADR 0019 asked for is a committed manifest, `website/redirects.json`, generated once
from the pre-cut sitemap and then hand-checked. It is not regenerated on each build: its purpose
is to remember URLs the new build no longer knows about, which a build-time generator by
definition cannot do. `assemble-site.mjs` verifies at the end of every run that each manifest
entry produced a stub and that each stub's target resolves in the assembled tree, so the parity
check fails CI rather than being asserted by hand.

The pre-cut sitemap listed 53 URLs. Two deliberately take no stub, and both exclusions are the
decision rather than exceptions to it:

- the site root, which now serves the portal home — that is what the promotion is for; and
- `/reference/`, which was the mkdocstrings section overview. Its content moves to
  `/reference/symbols/`, and the path is now occupied by the MkDocs reference front matter, which
  answers the same question and links onward. No stub could be written there in any case.

The remaining 51 URLs get stubs.

One consequence of the assembly is worth stating explicitly, because it is currently true by
luck rather than by design. The portal builds with `trailingSlash: false`, so a portal route emits
`api.html`, while a redirect stub for the old MkDocs URL `/api/` is written to `api/index.html`.
The two never collide on disk, and both URLs keep working — but they serve different pages that
differ only by a trailing slash: `/scorequant/api` is the portal's symbol catalogue and
`/scorequant/api/` redirects to the reference's API guide. The same holds for `/examples`. Two
things follow. The assemble script refuses to write a stub over a path that already exists in the
assembled tree, so if `trailingSlash` is ever changed this becomes a loud build failure instead of
silent content loss. And each portal page whose name a redirected MkDocs URL shares links
prominently to that MkDocs page, so a reader who arrives at either finds the other. Dropping the
stub instead was considered and rejected: without it, a previously live URL would simply 404.

MkDocs' own `reference/` section is renamed `symbols/` as part of this change. Without the rename
the mkdocstrings pages would sit at `/reference/reference/<topic>/`, and the old `/reference/`
URL would collide with the new MkDocs index. The rename costs nothing in URL terms, because the
`/reference/` prefix already changes every MkDocs URL.

Deployment does **not** change here. `docs.yml`'s publish step is frozen for the duration of the
migration, so the live site holds its last good state and every live URL keeps working while the
portal's front door and walkthroughs are written. Turning it on, against the assembled tree, is a
separate and explicitly authorized act, as ADR 0019 requires — including the Playwright and
accessibility flows that ADR 0019 named as gates for the promotion rather than for the preview
artifact.

That separate act is [ADR 0026](0026-one-workflow-publishes-the-site.md). `docs.yml` was deleted
rather than un-frozen, because it would have deployed `site/` — the MkDocs build alone, not the
assembled tree this ADR defines.

## Consequences

The URL a published package advertises now lands on an explanation. MkDocs keeps every page it
had, at a new prefix, with the old prefix redirecting; it remains the exhaustive API, developer
and ADR reference, and the portal links deeply into it rather than copying it.

The `/scorequant/portal/` prefix disappears from the source: the nine places that hard-coded it
collapse into one `SITE_BASE` constant, because a Web Worker has no React context and so
`useBaseUrl` could never have served all of them. A test fails if the literal returns.

Every future MkDocs page is born under `/reference/`, and every future portal route under the
root; a page that needs to move between them needs a manifest entry, which is the cost of having
one canonical URL space instead of two.
