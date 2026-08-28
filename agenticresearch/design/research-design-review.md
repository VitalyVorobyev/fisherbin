Yes. Your concern is valid. The **artifact granularity is useful; the task granularity should be substantially coarser**.

The distinction I would make is:

> **Claims should be atomic. Work should not be.**

That is the main adjustment I would make to the current ScoreQuant setup.

### Why I proposed the current structure

The workspace currently separates several things that are dangerously easy for an LLM to blur together:

| Artifact                | Purpose                                                 |
| ----------------------- | ------------------------------------------------------- |
| `PROBLEM.md`            | What problem are we actually solving?                   |
| `KNOWN_RESULTS.md`      | What is already established?                            |
| `CLAIMS.json`           | Exact theorem/claim graph, assumptions and dependencies |
| `COUNTEREXAMPLES/`      | Permanent falsification evidence                        |
| `OPEN_PROBLEMS.md`      | What remains unresolved                                 |
| `LITERATURE.md`         | What belongs to prior art                               |
| `NUMERICAL_EVIDENCE.md` | What has only empirical support                         |
| `AGENT.md`              | How research should be conducted                        |
| `START_HERE.md`         | Cold-start protection for a new agent                   |

That structure is explicitly encoded in the current README. 

The motivation was primarily **epistemic safety**, not project management. For mathematical research, LLMs have several recurring failure modes:

* rediscovering something already proved three sessions ago;
* turning numerical evidence into a theorem;
* transferring a theorem from a superficially similar feasible set;
* forgetting assumptions;
* silently strengthening `A ⇒ B` into `A ⇔ B`;
* losing counterexamples after the conversation where they were found;
* mixing finite assignment, inductive quantization and population claims;
* confusing "we didn't find prior art" with novelty.

Your current `AGENT.md` is deliberately adversarial about exactly these things: dependency lookup, prior-art triangulation, falsification before proof, explicit proof, then adversarial audit. 

And the research dossier explicitly describes the underlying idea as a **two-layer scientific memory**: human-readable conceptual structure plus a machine-readable claim graph. 

I still think that part is correct.

## Where I now think we over-engineered it

There are two places where the structure has started turning into process overhead.

First, `AGENT.md` currently says a theorem investigation should effectively go through a 16-item output contract—target, dependencies, literature, counterexamples, algebra, proof, audit, algorithmic consequence, deployability, information loss, registry patch, next question, etc.  That is excellent as a **checklist for publication-critical work**, but excessive as the mandatory format for every investigation.

Second, `START_HERE.md` requires a substantial scope recital before a new agent can do anything.  That's useful for cold starts, but it should not become a ritual repeated for every agent invocation.

There is a broader agent-engineering lesson here. OpenAI describes a similar evolution in its own agent-first repositories: the "one giant AGENTS.md" approach became counterproductive, so `AGENTS.md` became a **map**, while structured repository documents became the actual system of record. Their explicit rule is essentially "give the agent a map, not a 1,000-page manual." ([OpenAI][1]) OpenAI also reports that agents work well on coherent, issue-sized units of work rather than arbitrary tiny fragments. ([OpenAI][2])

That applies particularly strongly to mathematics because the expensive operation is **reconstructing the conceptual state**.

## The important separation: storage granularity vs execution granularity

I would keep something like

```text
D-EXCHANGE-EXACT
D-LEVERAGE-BOUND
D-EXCHANGE-IMPLIES-VORONOI
D-VORONOI-NOT-IMPLIES-EXCHANGE
D-GLOBAL-GEOMETRIC
DS-GLOBAL-NONGEOMETRIC
...
```

as separate nodes in `CLAIMS.json`.

That is good granularity because another theorem may depend on exactly one of them.

But I would **not** normally create five separate agent tasks to investigate those five nodes.

Instead, a work packet might be:

```text
AUDIT-D-EXCHANGE-VORONOI

Goal:
Determine whether the finite D exchange→Voronoi theorem
survives a publication-grade adversarial audit.

Relevant claim nodes:
- D-EXCHANGE-EXACT
- D-LEVERAGE-BOUND
- D-EXCHANGE-IMPLIES-VORONOI
- D-DUPLICATE-DEGENERACY
- D-SINGLETON-DEGENERACY

Agent may:
- repair lemmas;
- search counterexamples;
- search prior art;
- update all affected claims.

Done when:
the theorem is proved, disproved, or reduced to explicitly
listed unresolved assumptions.
```

That is almost exactly the right scale of the `AUDIT-D-EXCHANGE-VORONOI` task you started yesterday.

So I would formalize the principle as:

> `CLAIMS.json` = **normalized database**
> `OPEN_PROBLEMS.md` = **research roadmap**
> agent tasks = **transactions over several claim nodes**

This is analogous to software engineering: nobody creates one GitHub issue per function even though functions are individually represented in the codebase.

## I would simplify ScoreQuant to three operational layers

### 1. Small orientation layer

Keep:

```text
README.md
PROBLEM.md
AGENT.md
```

But make `AGENT.md` much shorter.

It should contain only invariants such as:

* use the claim graph;
* distinguish finite / empirical inductive / population;
* distinguish D / in-bin \(D_s\) / projected efficient-score D;
* falsify before making strong claims;
* `measured != proved`;
* search gap != novelty;
* persist exact counterexamples;
* report deployment semantics.

The current detailed recipes can move into something like:

```text
protocols/
    theorem.md
    literature-audit.md
    numerical-falsification.md
    algorithm.md
    publication-audit.md
```

The agent reads one when relevant.

### 2. Fine-grained scientific memory

Keep essentially unchanged:

```text
CLAIMS.json
KNOWN_RESULTS.md
COUNTEREXAMPLES/
LITERATURE.md
NUMERICAL_EVIDENCE.md
```

This fine granularity is **valuable**.

For example, your numerical ledger already correctly distinguishes theorem regression tests from performance benchmarks and says numerical evidence is not proof.  That is exactly the kind of durable research memory agents need.

### 3. Coarse work packets

This is the piece I would add explicitly:

```text
WORK/
    active/
        AUDIT-D-EXCHANGE-VORONOI.md
        DS-POPULATION-BRIDGE.md
    completed/
        ...
```

Each packet should be short:

```text
Goal
Why it matters
Relevant claims
Known blockers
Recommended starting points
Required deliverables
Stop conditions
```

Crucially, **do not prescribe the internal decomposition** unless there is a reason.

Let the agent decide that it needs Lemma A, numerical search B and literature search C.

That gives it room to reason.

## When should a task actually be split?

I would split only when one of these occurs:

1. **Independent work can happen in parallel.**
   Example: a difficult prior-art search can proceed independently from an exact counterexample search.

2. **Different tools/context are required.**
   One agent needs 20 PDFs; another needs a Python exhaustive search.

3. **There is a useful verification boundary.**
   A proof is complete enough that an independent adversarial auditor should now see it without the original agent's reasoning context.

4. **The task has branched scientifically.**
   During `DS-POPULATION-BRIDGE`, you discover two genuinely independent conjectures.

5. **The context becomes too large.**

I would **not** split just because a proof has seven lemmas.

The same theorem agent should normally derive all seven.

## I would also soften the multi-agent-role model

The dossier proposed literature agent → theorem agent → counterexample agent → proof auditor → integrator. 

That is a good **publication-critical pipeline**, but I would not run five agents for every OP.

For normal research, one strong agent should be allowed to do:

```text
understand
   ↓
literature check
   ↓
try to falsify
   ↓
derive
   ↓
test
   ↓
update artifacts
```

Then use an **independent second agent only when the result becomes important**.

For example:

* exploratory lemma: one agent;
* promising theorem: one researcher + one auditor;
* central paper theorem such as `D-EXCHANGE-IMPLIES-VORONOI`: researcher + adversarial auditor + independent prior-art check.

This avoids enormous duplication of context reconstruction.

## I would change one more thing: don't force every OP to be tiny

Your `OPEN_PROBLEMS.md` already has reasonably broad problems such as "canonical parameterization for linear mixtures", "count + shape information", "parameter-mismatch degradation", and "atomic randomization gap." 

I would keep them broad.

In fact I would probably make the top-level queue **even smaller**—roughly 8–15 active research programmes, not 30–50 micro-questions.

Under each one, `CLAIMS.json` can contain all of the precise subclaims.

For example:

```text
OP: D_s FINITE→POPULATION THEORY
    ├── claim: finite O(K/N) violation bound
    ├── claim: balanced-cell condition
    ├── conjecture: population stationary geometry
    ├── claim: efficient-score domination
    ├── question: equality conditions
    └── counterexample: exact finite non-geometric optimum
```

An agent gets the **whole branch**, not one leaf.

That lets it notice connections that overly narrow prompts would hide.

## So the revised architecture I recommend is

```text
README.md                    # very short map
PROBLEM.md                   # canonical scientific target
AGENT.md                     # ~1–2 pages of non-negotiable rules

KNOWN_RESULTS.md             # human-readable current state
CLAIMS.json                  # fine-grained theorem graph

OPEN_PROBLEMS.md             # coarse scientific roadmap

WORK/
  active/                    # coarse agent work packets
  completed/

COUNTEREXAMPLES/             # immutable exact witnesses
LITERATURE.md                # curated theorem-level bibliography
NUMERICAL_EVIDENCE.md        # empirical/regression ledger

protocols/
  theorem.md
  audit.md
  literature.md
  numerical.md
  algorithm.md

archive/
```

And `START_HERE.md` becomes optional or extremely short: basically "read README, identify the relevant branch of `CLAIMS.json`, then read only the documents needed for your task."

### The rule I would put at the top of the workspace

> **Decompose knowledge finely; decompose work only at natural scientific boundaries.**

That gives us both things we want: a precise, non-lossy scientific memory **without turning the research process into bureaucracy**.

For ScoreQuant specifically, I think the current artifact *model* is strong, but the **agent protocol is about 30–40% too procedural**. I would simplify `AGENT.md`, introduce coarse `WORK/` packets, and treat `CLAIMS.json` nodes as bookkeeping rather than as individual tasks. The recent `AUDIT-D-EXCHANGE-VORONOI` is actually close to the task size I would aim for, rather than something I would decompose further.

[1]: https://openai.com/index/harness-engineering/?utm_source=chatgpt.com "Harness engineering: leveraging Codex in an agent-first world | OpenAI"
[2]: https://openai.com/business/guides-and-resources/how-openai-uses-codex/?utm_source=chatgpt.com "How OpenAI uses Codex | OpenAI"
