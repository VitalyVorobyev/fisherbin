# S02 — Manuscript reconciliation + novelty ledger

**Workstream:** W1 · **Needs:** S1 · **Parallel with:** S3 · **Status:** queued

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

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
