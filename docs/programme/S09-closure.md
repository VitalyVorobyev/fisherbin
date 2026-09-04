# S09 — Closure: independent v9 audit, exit gate, teardown

**Workstream:** all · **Needs:** S5, S8, S11 · **Parallel with:** — · **Status:** active

## Goal

Close the programme. Perform a fresh-context audit read of manuscript v9 against the novelty
ledger, following `agenticresearch/protocols/audit.md`'s independence requirement, and record a
verdict per statement; this read is publication-critical and is not optional, per the plan's own
risk note that attribution is publication-critical. Then verify all four workstream gates hold,
flip every session row in the M12 table to `done` or `cut`, retire the session prompt in
`docs/programme/README.md`, and add the post-M12 CHANGELOG entry. Done means M12 reads `done` in
`docs/roadmap.md` and the full handoff gate plus `pnpm validate` are green on `main`.

## Inputs

- `docs/programme/README.md`: orchestrator contract; the session prompt this session retires.
- `docs/programme/S08-the-four-walkthroughs.md`: S8 closing report; confirms the walkthrough
  half of the W3 and W4 gates.
- `docs/programme/S10-portal-front-door.md`: S10 closing report; confirms the front door, the
  captured-output contract and the two MkDocs page retirements.
- `docs/programme/S11-portal-design-and-launch.md`: S11 closing report; confirms the design pass,
  the inline demos, the redirect parity spot-check and the live deployment URL.
- `docs/programme/S05-manuscript-v9-draft.md`: S5 closing report; confirms v9 exists and what it
  covers.
- `agenticresearch/manuscripts/score_space_quantization_article_v9.md`: the document being
  audited.
- `agenticresearch/manuscripts/NOVELTY_LEDGER.md`: the ledger the audit checks v9 against.
- `agenticresearch/protocols/audit.md`: the independence and verdict-per-statement procedure this
  session must follow.
- `docs/roadmap.md`: M12 table and exit gate; this session flips the table and evaluates the gate.
- `CHANGELOG.md`: the post-M12 entry is added at session end.
- `agenticresearch/py/registry.py`: `validate` for the final registry check.

Companion research packet: `agenticresearch/WORK/active/MANUSCRIPT-V9-AUDIT.md`. It does not exist
yet; this session drafts it from `agenticresearch/WORK/TEMPLATE.md` at session start. This
programme packet points at it and does not duplicate its content.

## Deliverables

- A fresh-context audit read of v9 against `NOVELTY_LEDGER.md`, per `protocols/audit.md`, with a
  verdict recorded per statement (confirmed, needs revision, or disputed, per the protocol's own
  vocabulary).
- `agenticresearch/WORK/completed/MANUSCRIPT-V9-AUDIT.md`: the closed companion packet, carrying
  the audit verdicts.
- `docs/roadmap.md`: M12 exit gate evaluated; every session row (S1-S11) flipped to `done` or
  `cut`; M12 status line changed to `done`.
- `docs/programme/README.md`: the copy-paste session prompt retired (marked no longer active, or
  removed per the session's judgment, with the reason recorded).
- `CHANGELOG.md`: an entry for the release that follows M12, summarizing the programme's changes.
  The `0.1.0` entry is closed and dated 2026-08-30 (the release shipped before M12 began; S4
  corrected the stale `unreleased` heading), so this session adds the next entry rather than
  editing that one.

## Done criteria

- Every statement in v9 that the ledger tags has a recorded audit verdict.
- All four M12 workstream gates (W1-W4) hold, verified against their stated gate text in
  `docs/roadmap.md`, not assumed from session closing reports alone.
- Every session row S1-S11 in the M12 table reads `done` or `cut`.
- `docs/roadmap.md` M12 status line reads `done`.
- The full handoff gate, `pnpm validate`, and `python agenticresearch/py/registry.py validate` are
  all green on `main`.
- roadmap M12 table shows S09 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Perform the independent audit read of v9 against the ledger, verdict per statement | opus, must not have drafted v9 in S5; never `fable` | verdict table |
| Check every S1-S8, S10 and S11 packet for a written closing report and its done criteria met | haiku | coverage checklist |
| Draft and close the companion audit packet | haiku | `WORK/completed/MANUSCRIPT-V9-AUDIT.md` |
| Run the full handoff gate, `pnpm validate`, and `registry.py validate` | haiku | gate output |
| Update `docs/roadmap.md` (session rows, M12 status, exit gate), retire the README session prompt, add the CHANGELOG entry | orchestrator | roadmap, README, CHANGELOG diff |

## Verification

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
cd website && pnpm validate
python agenticresearch/py/registry.py validate
```

## Open decisions

- How to guarantee the audit reader is genuinely independent of the S5 drafting session (a new
  session with no shared context is the plan's intent; the exact mechanism, e.g. a fresh Claude
  Code session with no memory of S5, is left to whoever runs S9).
- Whether any session row ends up `cut` rather than `done` (for example if S7's HEP path was
  unreachable and only the fallback shipped, that is still `done`, not `cut`; `cut` is reserved
  for a session whose deliverable was dropped entirely). The plan does not name a `cut` candidate,
  so this session should not manufacture one.

## Closing report

M12 is closed. Eleven sessions over the programme; this one audited the manuscript, evaluated the
four workstream gates, and turned the lights off.

### The site is live, and the check nobody could run locally has now run

S11 merged and deployed on 4 September 2026. The deploying run reported `build: success` and
`deploy: success`, and the root of the published site now serves the portal's home page rather
than the reference index.

S11 could not verify its own deployment — the check only becomes possible after the branch is
merged, so S11 handed it to this session as an inherited obligation and explicitly told the reader
not to assume it had been discharged. It is discharged now: **all 53 pre-cut URLs resolve against
the live host, 0 failed.** The check is stronger than a status code. For each of the 50 redirect
stubs it confirms the stub answers, that the stub body actually names the target the committed
manifest promises, and that the target itself answers; the 3 deliberately unstubbed URLs are
required to serve real content rather than a near-empty page. The one baseline change predicted
before deployment is exactly what happened: `/reference/bibliography/` went from 404 to 200, while
`/bibliography/` kept working as a stub.

### The manuscript audit found six real defects, and checking it found more

An independent agent, with no access to the drafting session, read v9 against the novelty ledger
and returned **90 confirmed, 11 needs revision, 2 disputed, 0 absent**. The headline result is the
one that mattered: **no category-1 failure** — nowhere does v9 claim novelty for a result the
ledger calls `known`, a `direct corollary`, an `adaptation` or `unresolved`. All 103 ledger rows
are placed in the manuscript, all 103 inline marks match their ledger row exactly, and there is no
priority language anywhere in the text.

Every decisive finding was verified directly before being acted on, and that changed the answer
three times:

- The audit said three reference entries were duplicates. My own earlier check had found one, by
  comparing 60-character prefixes. **The audit was right and my check was wrong** — the pairs
  differ in punctuation ("Ritov, and" against "Ritov and"), which a prefix comparison hides.
- The audit said three `apparently new` statements were missing the required precedent hedge.
  Enumerating every such label and testing each found **five**.
- The audit said six bibliography keys were missing. That number could not be reproduced. Under a
  stated criterion — cited inside a sentence that argues precedent — the verifiable number is
  **two**.

What was fixed: §9.2 claimed the open-problem list "matches the open entries of the project's
claim registry", which is false (the registry has 32 open entries; v9 names 19), so it now says
what is true and names the thirteen that are out of scope. Three duplicate references were merged,
taking 75 entries to 72 and remapping all 519 citations. Five precedent hedges were added. All
nine of Appendix H's equation pointers were stale and four pointed at equations that do not exist
— they were v8 section numbers left behind by the renumbering — and every one is now resolved
against where the claim actually sits. And DS14-2 and DS15-6, which are audit records, carried the
label `unresolved`, which the vocabulary defines as "open claim"; the ledger's own Open section
already said no novelty label applies to them. They are now `n/a — audit record`, a sixth
vocabulary term, and the open-claim count drops from 31 to 29.

### What was deliberately not done

Two results in v9 are asserted without a citation: the standard hat-matrix leverage inequality
(V8-10) and the λ_min superdifferential structure (V8-30). Two further references that carry
prior-art arguments — Hartigan (1975) and Haynsworth (1968) — have no key in the registry
bibliography. All four are left open rather than filled in, because the bibliography is generated
and its schema requires each key to name the place where the source was read and annotated;
writing one without doing the read would assert a read that did not happen. None of the four is a
novelty overstatement: all the affected rows are labelled `known`, so the manuscript claims nothing
for them. The debt is a missing citation, not a false claim, and it is recorded in
`agenticresearch/WORK/completed/MANUSCRIPT-V9-AUDIT.md` with the question the next reader should
attack.

### A changelog defect that nobody obviously caused

`CHANGELOG.md` dated everything under `[0.1.0] — 2026-08-30`. But S1 and S3 had appended sections
while that heading still read `unreleased`, and S4 later dated the heading — which retroactively
asserted that their work had shipped in the release. Checked against the `v0.1.0` tag: `RefusalError`
does not exist anywhere in `src/` there, and `LinearProblem` is still exported, so the "Errors"
section and the "Removed" section both described work that had not shipped, and so did one bullet
under "Contracts". All three now sit under a real `[Unreleased]` heading, alongside the site entry
for the deployment. Nobody made a mistake at any single step; the defect emerged from the order the
steps happened in.

Five session packets also disagreed with the roadmap about their own status — S6, S7 and S8 still
read `queued` and S10 and S11 still read `active`, while the roadmap called all five `done`. The
roadmap was right; the packet headers are now synced.

### Verified

Green on this branch:

```
uv run ruff check .                                 All checks passed!
uv run ruff format --check .                        258 files already formatted
uv run ty check src                                 All checks passed!
JAX_ENABLE_X64=1 uv run pytest -n auto              553 passed in 151.35s
JAX_ENABLE_X64=0 uv run pytest tests/test_float32.py 4 passed in 3.61s
uv build                                            built sdist + wheel 0.1.0
uv run mkdocs build --strict                        built in 1.81s, --strict clean
cd website && pnpm validate                         15 files, 118 tests passed; build ok
registry.py validate                                registry clean
```

The four workstream gates were checked against their stated text rather than against the closing
reports that claim them. W1: 103 of 103 ledger rows placed, an independent audit read recorded with
a verdict per statement, registry clean. W2: `test_architecture.py`, `test_golden_engine.py` and
`test_execution_backends.py` all pass in the run above, ADR 0024 records the error hierarchy, and
the CHANGELOG now records the breaking change under the correct heading. W3: the snippet and fact
guards (`test_portal_snippets.py`, `test_walkthrough_facts.py`, `test_docs_snippets.py`) pass,
Playwright runs in CI through `site.yml`, and the root deployment is live with 53 of 53 URLs
resolving. W4: each showcase executes in both test tiers with its evidence JSON pinned, and the
roadmap names the provenance of every number it reports.

### The one thing the next session must know

**The programme's status lives in the M12 table in `docs/roadmap.md`, and that table is now closed.**
There is no S12. The copy-paste session prompt in `docs/programme/README.md` has been marked
retired rather than deleted — it is the record of how the programme was run, and a future
multi-session programme should copy and adapt it, not resume it.

The substantive thing left open is the four missing citations above. They need a literature read,
not an editing pass, and `MANUSCRIPT-V9-AUDIT.md` names the question that unblocks them. Worth
knowing too: this session wrote throwaway scripts to check the inline-mark/ledger correspondence,
the Appendix H placement, and that every equation reference resolves. Those checks caught real
defects and were deliberately not committed as a guard, because M12 was closing. Whoever owns the
manuscript next should consider making them executable — a stale cross-reference is exactly the
kind of thing that survives a careful human read.
