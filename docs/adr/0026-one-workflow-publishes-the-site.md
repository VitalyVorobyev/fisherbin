# ADR 0026: One workflow builds and publishes the assembled site

**Status:** Accepted

**Completes:** [ADR 0019](0019-react-learning-portal.md)'s deployment authorization and lifts the
freeze recorded in [ADR 0025](0025-portal-at-the-site-root.md).

## Context

ADR 0019 created the portal and made its publication conditional: "Deployment remains preview-only
until separately authorized." ADR 0025 moved the portal to the site root and MkDocs to
`/reference/`, and deliberately left that condition in place — "Deployment does **not** change
here" — so that the live site held its last good state while the front door was written.

Three workflows had accumulated under that arrangement, and none of them published what ADR 0025
had defined:

- `docs.yml` deployed to Pages with `path: site` — the MkDocs build alone, never the assembled
  tree — and its publish step was frozen for the migration.
- `portal-preview.yml` built the portal and uploaded a CI artifact that nothing consumed.
- Neither deployed `.pages-preview`, the tree `pnpm assemble:site` writes and the only tree in
  which the portal, the reference beneath it, and the 53 pre-cut redirect URLs are all correct.

One consequence is worth recording because it decided a question in S10: **the portal has never
been deployed.** The Pages artifact path was `site` from the first commit that introduced it
through the S6 freeze, so no portal URL has ever resolved. A route retired from the portal
therefore needs no redirect stub — a stub would redirect from a URL that only ever returned 404.

The remaining work was never the deployment mechanism. It was the front door (S10) and the design
pass, the demos, and the accessibility gates (S11). Both are now done, and the assembled tree
verifies locally.

## Decision

One workflow, `site.yml`, builds and publishes the site.

It runs the strict MkDocs reference build, the portal's typecheck, lint, unit tests, production
build, and the Playwright end-to-end and accessibility suites, then `pnpm assemble:site`, and
uploads `.pages-preview` twice: as an inspectable artifact, and as the Pages artifact.

**A pull request builds and uploads. Only a push to `main` deploys.** Publication stays an
authorized action rather than a merge side effect, which is what ADR 0019 asked for; the gate is
now expressed in the workflow's `if` condition instead of in a frozen step.

`docs.yml` is **deleted rather than un-frozen.** Un-freezing it would have restored a deployment of
`site/`, which is the wrong tree — it would overwrite the assembled root with the MkDocs build and
take every portal URL down with it. The deployment moved; it did not resume. `portal-preview.yml`
is deleted for the same reason: `site.yml` is that workflow plus the reference build plus the
publish gate, and keeping it would have made every pull request build the site twice.

The strict reference build therefore now runs in exactly one place, and it runs early: a broken
reference link fails the pull request before the portal is built and tested.

**The deployment stays host-agnostic.** Every base-path consumer already resolves through the
single `SITE_BASE` constant that ADR 0025 introduced, and the workflow hard-codes no host. The
project's published identity is `https://vitalyvorobyev.github.io/scorequant/`, which
`scorequant 0.1.0` advertises on PyPI as both Homepage and Documentation; a version number on PyPI
cannot be reissued, so that URL has to keep working for as long as that release exists. A future
move to a custom domain is therefore a redirect *from* github.io, never a replacement of it.

## Consequences

The URL the package advertises now serves the portal, and the 53 pre-cut MkDocs URLs in
`website/redirects.json` become checkable against a live host for the first time — a check no local
run can perform, and the one that matters immediately after the first deployment.

A pull request pays the full cost once: the reference build, the portal build, and the browser
suites in a single job whose artifact is exactly what would be published. What CI proves and what
gets deployed are the same tree, which is the property the three-workflow arrangement never had.

The documentation badge in `README.md` moves from `docs.yml` to `site.yml`, because the workflow it
named no longer exists.

Rollback is a revert of the workflow, not of the site: Pages keeps serving the last successful
deployment, so a bad publish is corrected by pushing a fixed `main` rather than by restoring a
previous mechanism.
