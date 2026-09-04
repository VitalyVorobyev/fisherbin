# ADR 0027: A landing page at the root, the documentation at `/docs/`, the portal at `/portal/`

**Status:** Accepted

**Supersedes:** [ADR 0025](0025-portal-at-the-site-root.md); keeps
[ADR 0026](0026-one-workflow-publishes-the-site.md) unchanged

## Context

ADR 0025 promoted the React portal to the site root and demoted the MkDocs site to `/reference/`.
The owner reviewed the published result on 4 September 2026 and rejected the front door: to the
scientists and engineers the site is for, the home page read as assertion rather than instruction,
the live score-space demo and its dashed bisector lines were unexplained, the Benchmarks page
showed scenario codenames and elapsed times with no statement of the task, the blog was a single
post without context, and the MkDocs site had no link back to the root. The three narrative pages
the portal had absorbed — *Why ScoreQuant*, *Three doors*, *Choosing your workflow* — were the
pages a first reader most needed, and they no longer existed as pages.

Two things are true at once. The MkDocs site is the complete written account of the library —
the theory book, the runnable examples, the evidence studies, the API — and it was the
documentation readers arrived at before ADR 0025. The portal holds work that is worth keeping and
continuing: a *Get started* whose printed outputs are captured from a run, four walkthroughs with
every number traced to a committed evidence file, and a Lab that runs the real wheel in the
browser. Neither should own the other's URL space, and the owner's decision is that neither owns
the root.

## Decision

Three surfaces, one assembled tree, one workflow:

| URL under `https://vitalyvorobyev.github.io/scorequant/` | Serves | Source |
| --- | --- | --- |
| `/` | the landing page | `landing/` |
| `/docs/…` | the MkDocs documentation and book | `docs/`, `mkdocs.yml` |
| `/portal/…` | the Docusaurus learning portal | `website/` |

**The landing page only links; it never explains twice.** It is one hand-written HTML file with
inline CSS, no JavaScript, no web fonts and no build step. It states what the library is, the
one identity the method rests on, the install line, and then the two destinations side by side
with a concrete list of what each contains and direct links into it. Its only code block is
byte-for-byte the first Python fence of `docs/index.md`, so it is executed by the docs snippet
harness rather than trusted; its prose carries no measured number; every link into `docs/` is
resolved against the MkDocs source by `tests/test_landing.py`, and every site-relative link is
resolved against the assembled tree by `website/scripts/assemble-site.mjs`, which fails the build
otherwise.

**The MkDocs site is the documentation again.** `docs/motivation.md`, `docs/three-doors.md` and
`docs/user-workflow.md` are restored from the last pre-ADR-0025 commit with their nav entries and
their twenty-two executed fences; the front page is the pre-promotion one. Its header title links
to the landing page (`extra.homepage`) and its nav carries an external *Portal* entry, so the link
back that ADR 0025 lacked exists in both directions.

**The portal moves to `/portal/`, unchanged in content.** That is the URL ADR 0019 originally
staged it at. `baseUrl` and `SITE_BASE` change in lockstep, the base-path guard test now requires
the prefix to appear in `src/lib/site.ts` and nowhere else, and the footer link to the
documentation reads *Documentation*. The owner's review of the portal's own pages — the home
page, the Lab, Benchmarks, the blog — is future portal work and is not decided here.

**Redirects.** Every pre-cut MkDocs URL in `website/redirects.json` now targets `docs/…`; the
three formerly portal-targeted entries target the restored pages; `reference/` and `api/` are
stubbed to `docs/` and `docs/api/`. The site root remains the one unstubbed path. The portal's
one day at the root is not stubbed: the only links to those URLs were in the README, which this
decision re-points.

## Consequences

- `pyproject.toml` advertises the root as Homepage and `/docs/` as Documentation. No release is
  cut for a metadata change.
- Three places state the topology and must move together: `landing/index.html`'s links,
  `mkdocs.yml`'s `site_url`, and `website/src/lib/site.ts`. The assemble script's link check is
  what catches a mismatch.
- The portal's e2e and unit suites, `pnpm validate`, and `site.yml` run exactly as before; the
  only change to CI is the tree the assemble step writes.
- ADR 0025's reasoning for giving the root to explanation still stands. This decision moves the
  explanation to a page that is short enough to be read in full and honest enough to be trusted,
  and leaves the two larger surfaces to explain themselves.
