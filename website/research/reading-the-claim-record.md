---
title: Reading the claim record
sidebar_label: Reading the claim record
sidebar_position: 9
---

# Reading the claim record

*Who this is for: a reader who would rather check the project's work than take it on trust.*

Everything on the preceding pages is a paraphrase. The unparaphrased version is a registry of
claims: one record per statement, each carrying its own status, its assumptions, what it depends
on, and — where one exists — the exact example that marks its boundary. This page explains how to
read one, so that a paraphrase you doubt can be checked against the thing it paraphrases.

## What a claim record is, and is not

A record is a **statement plus its bookkeeping**. It is not a proof: the proof lives elsewhere and
the record points at it. It is not an attribution ruling either — the novelty ledger holds the
labels and the sources, and says of itself that it "records labels and attribution; it proves
nothing".

The registry is the canonical object. The ledger and these pages are both derived from it, and
where any of them disagree with the registry, the registry wins.

## The four fields that matter most

**`status` — what kind of statement this is.** This is the single most important field, because it
tells you who is responsible for the claim.

| Status | Meaning |
| --- | --- |
| `literature` | Established in the published literature. Cited here, not claimed |
| `bridge` | A short derivation from published results into this setting. Routine, and labelled routine |
| `project_proved` | Proved inside the project. The proof location and, usually, an audit record are named |
| `counterexample` | An exact example showing a plausible statement is false. Verified, usually in exact rational arithmetic, and usually with a regression test |
| `measured` | A numerical census. Evidence about what happens, never authority about what must happen |
| `open` | A question with no answer in either direction, stated precisely enough to be attacked |

**`level` — which of the three questions it answers.** The
[three questions](/research/the-problem) — labelling a fixed sample, learning a reusable rule,
designing against a population — are different problems, and a result about one is not a result
about another. The level field says which: `finite_assignment`, `empirical_inductive_quantizer`,
`empirical_to_population`, `population_quantizer`, plus `universal` for statements that hold at
every level, `information_accounting` for the retention diagnostics, and `score_oracle` for
statements about where the scores come from.

**`assumptions` — the conditions the statement needs.** These are load-bearing and they are the
usual reason a theorem "does not apply". The central structural theorem, for example, assumes
merged duplicate atoms, a positive-definite information matrix, exactly the requested number of
nonempty cells, no move restriction beyond keeping cells nonempty, and a zero gain tolerance. Drop
the first assumption and there is an exact counterexample; keep a positive solver tolerance instead
of zero and the guarantee weakens in a stated way. Both of those facts are recorded, not discovered
by the reader.

**`dependencies` — what it is built on.** Reading the dependency chain backwards is how you find
out whether a result rests on published mathematics or on the project's own work. On
[the claim record](/research/claim-record) each entry lists the dependencies that are themselves
published here.

## The fields that record limits

Three more fields exist precisely to stop over-reading.

`warning` carries what an audit insisted be said alongside the statement — that a targeted search
found no equivalent but that this is not a priority claim; that a scope was hardened after review;
that a registered generality was refuted.

`boundary_counterexamples` names the exact examples that mark where the statement stops. These are
the entries wired into the library's refusal messages.

`converse_failures` names statements that look like the reverse implication and are false.

## What publishing here means

Presence in the registry does **not** publish a claim. This site renders a claim only when its id
appears on an explicit allowlist, and adding an id is a deliberate decision rather than
bookkeeping. The build fails if an allowlisted id has no registry record or does not match it, so a
statement shown here cannot drift away from the statement in the registry.

The consequence worth stating plainly: the record on this site is a **subset**. Claims not listed
are not thereby refuted, retracted, or secret — they are simply not published yet.

## Two vocabulary traps

**"Apparently new" is about searching, not about mathematics.** A result carries that label when a
targeted literature search found no direct precedent. The ledger's own rule is that a search gap is
not a novelty proof; every such result is scheduled for an adversarial review that can demote it,
and the nearest prior art is recorded beside it. That is why nothing in this section is described
as first.

**"Unresolved" is about attribution, not about correctness.** Several exact, verified
counterexamples with regression tests carry that label, because no prior-art search has been
recorded for them.
They are presented as witnesses and diagnostics rather than as claims of priority.

## How to check one yourself

Every statement on these pages names its claim id and links to the entry. If you have the
repository, the same record and its proof are reachable from the claim id directly, and the
dependency and proof views are what the ledger itself cites as evidence for each of its rows.

## Next

[The claim record](/research/claim-record) is the record itself.
