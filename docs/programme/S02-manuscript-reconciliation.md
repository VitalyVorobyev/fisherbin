# S02 — Manuscript reconciliation + novelty ledger

**Workstream:** W1 · **Needs:** S1 · **Parallel with:** S3 · **Status:** done

## Goal

Produce a novelty ledger that gives every central statement in manuscript v8, and every finding
proved since v8, a novelty label, an attribution, and a registry pointer, so that S5 can draft v9
without re-deriving anything. Absent from v8 today: DS11-DS14 (population bridge, with DS11's
classical identity Krein/Anderson/Li-Mathias), DS15 (margins dichotomy, scalar-nuisance only,
`O~(N^-3/4)`), DS16 (margin price and stability certify nothing), DS17 (disproved inhabitation on
class (L)), DS18 (exact off-(L) positive transfer), DS19 (certified scalar tilt-DP bracket, strong
duality false), the A-optimality results A1-A4, the information-efficiency results I1-I3, and 11
new counterexample fixtures. Attribution needs checking against Rakhlin-Caponnetto 2006 (DS16),
Kieffer 1983 / Mease-Nair 2006 (DS18), and Grønlund et al. 2017 / Toledo 1993 (DS19). Done means
every such item has a ledger row; there is no adversarial literature search in this session.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S01-scaffold-and-public-surface.md`: S1 closing report, confirms the
  memory scaffold this packet depends on.
- `agenticresearch/manuscripts/README.md`: the maintained staleness ledger, the primary revision
  input and the source of the stale-item list this session must resolve.
- `agenticresearch/manuscripts/score_space_quantization_article_v8.md`: the document being
  reconciled; subagents extract statements from it, the orchestrator never opens it.
- `agenticresearch/KNOWN_RESULTS/index.md`: currently lists only DS11-DS15; regenerated here to
  DS16-DS19.
- `agenticresearch/protocols/theorem.md`: packet-closure requirements (item 7: next
  dependency-blocking question).
- `agenticresearch/WORK/TEMPLATE.md`: section shape for the companion research packet.
- `agenticresearch/py/registry.py`: `show <ID> --deps --proof` is the per-row evidence pointer.
- `docs/roadmap.md`: M12 W1 gate block, defines what "every ledger row placed" means.

Companion research packet: `agenticresearch/WORK/active/MANUSCRIPT-V9-RECONCILIATION.md`. It does
not exist yet; this session drafts it from `agenticresearch/WORK/TEMPLATE.md` at session start.
This programme packet points at it and does not duplicate its content.

## Deliverables

- `agenticresearch/manuscripts/NOVELTY_LEDGER.md`: one row per central v8 statement and per
  absent finding, with claim ids, a `registry.py show <ID> --deps --proof` pointer, a novelty
  label (known / direct corollary / adaptation / apparently new / unresolved), attribution, and
  the v8 location or "new section".
- `agenticresearch/KNOWN_RESULTS/index.md`: regenerated to include DS16-DS19.
- `agenticresearch/WORK/completed/MANUSCRIPT-V9-RECONCILIATION.md`: the closed companion packet,
  moved from `active/` to `completed/` at session end.

## Done criteria

- Every v8 labelled result (theorem, lemma, proposition) has a ledger row.
- Every in-scope `project_proved` and `counterexample` claim proved since v8 has a ledger row.
- `python agenticresearch/py/registry.py validate` is green.
- The orchestrator never loaded a manuscript body into its own context; all extraction and
  labelling happened in subagents.
- roadmap M12 table shows S02 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Dump claim branches DS11-DS19 and related (A1-A4, I1-I3), one section per agent | haiku | claim dumps saved to scratch files |
| Extract v8 central statements and their locations (theorem/lemma list, section headers) | haiku | statement inventory with v8 location |
| Assign novelty label and attribution per row | fable | filled ledger rows |
| Regenerate `KNOWN_RESULTS/index.md` | haiku | updated index file |
| Draft and close the companion research packet | haiku | `WORK/completed/MANUSCRIPT-V9-RECONCILIATION.md` |
| Write the session closing report | orchestrator | this packet's Closing report section |

## Verification

```bash
python agenticresearch/py/registry.py validate
```

This session does not touch `src/`, `docs/`, or `examples/`, so the library/docs handoff gate
does not apply.

## Open decisions

- Row granularity: whether each absent finding (DS11-DS14, A1-A4, I1-I3) gets one row or is
  bundled by claim family. The plan lists them individually; default to one row per claim id
  unless that makes the ledger unreadable, in which case group and say so in the row.
- How to ledger claims that remain deferred to P8 (adversarial literature review): mark them
  "unresolved" with a one-line reason rather than omitting them.

## Closing report

Session S2 ran on 3 September 2026 on branch `consolidation-s2-manuscript-reconciliation` (one
Claude Code session; two haiku inventory agents, four fable labelling agents, one per ledger
section).

**Delivered.** `agenticresearch/manuscripts/NOVELTY_LEDGER.md`, 103 rows in four sections: the
42 central statements of v8 (its seven labelled results, thirty distinct unlabelled claims from
the abstract, contributions and conclusion, and the five fixtures v8 relies on), the 18 rows of
the DS11–DS15 bridge, the 30 rows of DS16–DS19, and the 13 rows of A1–A4 and I1–I3. Each row
carries a v8 location or "new section", the registry ids with their `KNOWN_RESULTS` labels, the
`registry.py show` pointer, one of the five novelty labels, an attribution, and the hardened
wording the v9 draft must carry. `KNOWN_RESULTS/index.md` now lists DS16–DS19 (version 3.1).
The companion packet `WORK/completed/MANUSCRIPT-V9-RECONCILIATION.md` is closed with its
next dependency-blocking question. `manuscripts/README.md` points at the ledger and records that
the staleness list is superseded by it.

**Verified.** `python agenticresearch/py/registry.py validate` reports "registry clean". A
coverage script checked that every claim id in scope (the eight v8 crosswalk ids, all DS11–DS19,
A1–A4 and I1–I3 ids, and all 20 `COUNTEREXAMPLES/CE-*` fixtures) appears in the ledger, and that
each of Proposition 1, Lemma 2, Theorem 3, Proposition 4 and Proposition 5 has a row. The
orchestrator opened no manuscript body and no claim file; extraction and labelling ran in
subagents from line-range excerpts and registry dumps. No `src/`, `docs/` (outside this
directory and the roadmap) or `examples/` file changed, so the library gate did not apply.

**Cut or left open.** Nothing cut. Row granularity: one row per claim id, with three sub-item
rows (DS11-2, DS15-2, DS15-3) for results that have a `KNOWN_RESULTS` label but no registry id
of their own, marked as such. Deferred to P8 by design: the 31 `unresolved` rows (open claims,
audit records, counterexamples with no recorded literature search), and the confirmation of the
8 `apparently new` rows, each of which rests on a `search_gap` alone. Four v8 statements have no
registry counterpart and are listed in the ledger's "Gaps" subsection as framing or measured
evidence.

**The one thing the next session must know.** S5 drafts v9 from the ledger, never from v8's
wording: rows labelled `known` are cited, not claimed (DS11's identity is Krein/Anderson/
Li–Mathias; DS18's scalar uniqueness is Kieffer 1983 and Mease–Nair 2006, never Liu–Pagès; I1 is
standard D-efficiency with Valassi 2020 as scalar prior art), and the highest-risk open
attribution is Theorem 3 itself against Späth's determinant-clustering exchange routines, which
P8 has not yet swept. S3 is independent of this session.
