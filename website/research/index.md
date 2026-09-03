---
title: Research
sidebar_label: Overview
sidebar_position: 1
---

# Research

*Who this is for: a reader deciding how much of ScoreQuant's mathematics to trust, and for what.*

This section explains the research question behind the library, what the literature had settled
before the project started, which results the project proved itself, and — at the same length —
which parts are not proved and are recorded as open, or as numerical observation only.

Every statement in this section is drawn from two documents and nothing else: the internal
novelty ledger, which assigns each result a label from *known* / *direct corollary* /
*adaptation* / *apparently new* / *unresolved* together with the sources it must cite, and the
<a href="pathname:///reference/related-work/" target="_self">related-work survey</a>, which maps
the four research traditions this problem sits in. Where a page states a result it names the
registry claim id and links to [the claim record](/research/claim-record), so you can read the
exact statement, its assumptions and its dependencies instead of trusting a paraphrase.

Two conventions are worth knowing before you read further.

**A search gap is not a novelty proof.** Several results below carry the ledger label *apparently
new*. That label means a targeted literature search found no direct precedent — not that none
exists. Those results are written here as "no direct precedent was found", with the nearest prior
art named beside them, and every one of them is scheduled for an adversarial literature review
that can demote it.

**A counterexample is a boundary, not a defeat.** The most useful entries in the record are the
exact rational examples that show where a theorem stops holding. Four of them are wired into the
library as refusal messages, so a user who meets one is being told which counterexample forbids
the thing they asked for.

## The pages

| Page | What it answers |
| --- | --- |
| [The problem](/research/the-problem) | What quantity is being preserved, and what "losing information" means exactly |
| [What was already known](/research/what-was-already-known) | Which parts of this problem the literature had solved before the project began |
| [What ScoreQuant adds](/research/what-scorequant-adds) | The results the ledger marks as new, and what each one buys a user |
| [What cannot be certified](/research/what-cannot-be-certified) | Where the proofs stop: the counterexamples, the refusals, and the priced negatives |
| [What is still open](/research/what-is-still-open) | Questions with no answer yet, and what would count as answering them |
| [How the API names each result](/research/api-and-theorems) | Which theorem or counterexample each public object and each refusal message corresponds to |
| [The book, chapter by chapter](/research/book-contents) | The fourteen-chapter derivation in the reference, and who should read which chapter |
| [Reading the claim record](/research/reading-the-claim-record) | How the claim registry works, and how to read one entry |
| [The claim record](/research/claim-record) | The published claims themselves, one anchored entry each |

## Where to start

If you are deciding whether the method fits your problem, read
[the problem](/research/the-problem) and then
[what cannot be certified](/research/what-cannot-be-certified). The second page is the one that
decides the question.

If you met an error message and want to know where it comes from, go straight to
[how the API names each result](/research/api-and-theorems).

If you want the derivations rather than the summaries, the fourteen book chapters are listed in
[the book, chapter by chapter](/research/book-contents).
