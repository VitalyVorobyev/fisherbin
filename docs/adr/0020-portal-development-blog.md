# ADR 0020: Keep the plain-English development blog in the portal

**Status:** Accepted

**Extends:** [ADR 0019](0019-react-learning-portal.md)

## Context

ScoreQuant's research programme produces its results as a claim graph, audits, counterexample
fixtures, and proofs. That record is complete and machine-checkable, and it is unreadable to
anyone who is not already inside it. Nothing in the repository states, in ordinary language, what
was decided, what it changed, or why a reader should care. The published MkDocs site documents the
finished library rather than the work: `roadmap.md`, `system-design.md`, `development.md`, and
`adr/**` are excluded from it, and `agenticresearch/` is not published at all.

The two web properties have different audiences. MkDocs is the exhaustive developer and
advanced-user reference. The React portal is the public landing surface: narratives, interactive
labs, and the research projection. A development blog belongs with the public audience, which
means the portal and not a `material/blog` section bolted onto the reference site.

## Decision

Enable the Docusaurus blog plugin in `website/` at `/blog`. Docusaurus owns routing, MDX, tags,
authors, reading time, and the RSS/Atom feeds; `src/theme/Layout` and `src/theme/BlogLayout`
render every blog route through the ScoreQuant shell, so the blog is not visually a second site.
`Layout` leaves document metadata to Docusaurus, because the blog pages emit their own; the
`AppShell` `manageHead` flag exists for exactly that handover. `BlogLayout` replaces the Infima
grid rather than nesting a second `<main>` inside the shell's.

Three editorial rules are enforced at build time rather than by review: `onInlineAuthors`,
`onInlineTags`, and `onUntruncatedBlogPosts` all throw, so every post declares a known author,
carries only declared tags, and states its own summary above the fold.

One post accompanies each merged research or feature arc, written at merge time, 400–700 words,
answering what was done, why it matters, and what is next. Negative results are posted on the same
terms as positive ones — a result that forecloses a design direction is the kind of finding this
record exists to carry, and omitting those would make the blog marketing rather than a log.

## Consequences

The project gains a non-specialist entry point that is maintained as a by-product of merging
rather than as a separate documentation effort. The blog is a build-time gate: a malformed author,
an undeclared tag, or a missing truncation marker fails `pnpm build`, so posts cannot rot silently.

The blog is published only in the preview artifact until the portal is promoted to the site root,
which remains the separately authorized migration step ADR 0019 defines. `blogSidebarCount` is 0:
navigation comes from the index and the post paginator, so no recent-posts rail arrives with
foreign styling. Backfilling posts for already-merged arcs is a one-time task and is deliberately
selective — the arcs that changed direction, not all 21 merged pull requests.
