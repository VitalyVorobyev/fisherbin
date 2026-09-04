# MANUSCRIPT-V9-AUDIT — Independent fresh-context audit of manuscript v9

**Programme:** P6 (D-CORE-COMPLETION; manuscript by-product) · **Opened:** 4 September 2026 · **Status:** completed 4 September 2026

## Goal

Audit `manuscripts/score_space_quantization_article_v9.md` against
`manuscripts/NOVELTY_LEDGER.md` from a fresh context, following the independence requirement of
`protocols/audit.md`, and record a verdict per statement. Done is decidable: every ledger row has
a verdict, every verdict that demands a change is either applied or recorded as debt with the
reason it cannot be applied, and `registry.py validate` is green.

## Why it matters

Attribution is publication-critical. The failure this audit exists to catch is a novelty claim
made for a result that is `known`, a `direct corollary`, an `adaptation` or `unresolved` — a
category-1 failure. A manuscript that overstates its own priority is not correctable after
publication, and the novelty ledger is only worth as much as an independent read of it.

## Relevant claims

All 103 rows of `NOVELTY_LEDGER.md` (V8-*, DS11–DS19, A1–A4, I1–I3), and the registry claims they
reference.

## Method and independence

The audit was performed by a separate agent with no access to the drafting session's reasoning,
reading v9 and the ledger only. The orchestrating session then **verified every decisive finding
directly before acting on it**, rather than applying the report as given. That step changed the
outcome three times, in both directions, and is the reason it is recorded here as method rather
than as ceremony:

- The audit reported three duplicate reference pairs. An earlier check of my own had found only
  one, using a 60-character prefix comparison. Direct inspection confirmed **the audit was right
  and my check was wrong**: the pairs differ in punctuation ("Ritov, and" against "Ritov and"),
  which a prefix comparison hides.
- The audit reported three missing precedent hedges. Enumerating every `apparently new` label and
  testing each for a hedge found **five**, not three.
- The audit reported six missing bibliography keys. Under the criterion "cited inside a sentence
  that argues precedent", the verifiable number is **two**; 24 of v9's 72 references have no
  registry key, but the bibliography indexes annotated registry sources rather than the
  manuscript's reference list, so a textbook citation needs none. The audit's six could not be
  reproduced, and the criterion used here is stated so the next reader can re-derive the number.

## Verdicts

The audit returned **90 confirmed, 11 needs revision, 2 disputed, 0 absent**, with:

- all 103 ledger rows placed in v9 and one row per ledger row in Appendix H — re-verified: 103
  placed, none unplaced, none placed that is not a ledger row;
- all 103 inline `[novelty: …; ledger …]` marks matching their ledger row's Novelty cell exactly
  — re-verified after this session's edits: 198 inline mark/row pairs, **zero mismatches**, every
  ledger row cited at least once;
- **no category-1 failure**: no novelty is claimed anywhere for a `known`, `direct corollary`,
  `adaptation` or `unresolved` row;
- no priority or marketing language anywhere in the manuscript ("we are the first", "for the first
  time", "novel", "state of the art"): **zero occurrences**.

## Applied this session

1. **§9.2 stated a falsehood.** "The list matches the open entries of the project's claim
   registry" — the registry holds 32 open entries and v9 names 19. Replaced with what is true, and
   the thirteen out-of-scope entries characterised (applied modelling, asymptotic rate, solver
   engineering).
2. **Three duplicate reference entries** merged ([50] into [42], [65] into [45], [73] into [24]);
   75 entries become 72, 519 inline citations remapped, two citation groups deduplicated where the
   merge would otherwise have cited one work twice.
3. **Five missing precedent hedges** added, at §5.7 (two witnesses), §5.9, and three appendix
   fixture boxes. Theorem 2's statement box was deliberately left alone: its hedge sits with the
   proof in Appendix B.3, which is the manuscript's convention for boxed theorems.
4. **All nine of Appendix H's equation pointers were stale**, four of them dangling — (6.6),
   (10.4), (12.1) and (12.2) are never defined. They are v8 section numbers that survived the
   renumbering. Each is re-resolved against where the row's provenance mark actually sits in v9;
   the manuscript now contains **no undefined equation reference**.
5. **Category error in the ledger.** DS14-2 and DS15-6 are audit records carrying the label
   `unresolved`, which the vocabulary defines as "open claim" — and which the ledger's own Open
   section already contradicted by saying no novelty label applies. Both become `n/a — audit
   record`, added as a sixth vocabulary term, in the ledger and at all four inline marks. The
   open-claim count drops from 31 to 29.

## Recorded as debt, deliberately not applied

Each of these requires reading a source. The protocol requires that a bibliography key name the
place where the source was read and annotated; writing one without the read would assert a read
that did not happen, so these are left open rather than fabricated.

- **V8-10** — the "standard hat-matrix leverage inequality" (Lemma 2, §4.1 and Appendix B.1) is
  proved without citation. The ledger row already says "v9 should cite a regression-leverage
  source; the registry bibliography has none."
- **V8-30** — the λ_min superdifferential structure (§7.1, Appendix E.2) cites [15] for
  equivalence theory only. The ledger row already says "v9 should cite a subdifferential source;
  none in the registry bib."
- **Two load-bearing references without a registry bibliography key**: [7] Hartigan (1975), cited
  in the prior-art sentence at Appendix B.3 and in the ledger crosswalk, and [55] Haynsworth
  (1968), cited in the prior-art sentence at §5.6. Both need a `LITERATURE/topics/*.md` read-and-
  annotate pass before `py/registry.py reindex` can emit a key.

Neither V8-10 nor V8-30 is a novelty overstatement: both rows are labelled `known`, so the
manuscript claims nothing for them. The debt is a missing citation, not a false claim.

## Recommended, not built

A committed guard that re-derives the inline-mark/ledger correspondence — every
`[novelty: X; ledger Y]` against row Y's Novelty cell, every row placed in Appendix H, every
equation reference defined — would make this session's headline checks executable rather than
re-performed by hand each time. It was written as a throwaway script here and deliberately not
committed, because M12 is closing and a new guard belongs to whoever owns the manuscript next.

## Stop conditions

Reached. Every ledger row has a verdict; every applied revision is verified independently of the
report that proposed it; every unapplied revision is recorded above with the reason. The registry
validates clean.

## Next dependency-blocking question

**Can [7] Hartigan (1975) and [55] Haynsworth (1968) be annotated into
`LITERATURE/topics/*.md`, and do they carry the leverage inequality (V8-10, claim `D-LEVERAGE`)
and the λ_min superdifferential (V8-30, claim `E-SUPERGRADIENT`) that v9 currently asserts
without a source?** Both are `known`-labelled, so nothing in the novelty account moves; what moves
is whether v9 can be submitted with two uncited standard results.
