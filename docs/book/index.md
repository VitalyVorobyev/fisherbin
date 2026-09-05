# Information-preserving hard quantization

This book develops score-space quantization as a statistical subject in its own right,
independently of the ScoreQuant package interface. It asks a single question in a growing
number of settings: given a statistical model and a budget of \(K\) hard labels, which
partition of the data keeps the most Fisher information about the parameters you care
about, and how do you find it? The package is one answer to that question; the book is
the argument for why that answer is correct.

## Who it is for

You do not need to be running the ScoreQuant library to read this. The book stands on its
own as an account of hard quantization for parameter estimation, connecting classical
optimal-design and quantization theory to modern simulation-based inference. If you do use
the package, the book is also the reference for what each criterion, solver, and
diagnostic actually computes and under which assumptions. Executable examples accompany
the mathematics; the API reference carries the complete interface contracts.

## A gradual, 1D-first structure

The book is built to be climbable rather than merely readable. It opens with the smallest
version of the problem — one parameter, one score coordinate, a handful of cells — solved
by hand and then by exact dynamic programming, before any matrix, criterion, or
optimization algorithm appears. Only once that case is completely understood does the book
generalize: to vector scores and the three ways an observation can become one, to the
exact information identity that every later chapter depends on, to the two tasks
(population design and finite assignment) that the rest of the machinery is built to
serve, and finally to the criteria (trace, D, profiled \(D_s\), E) and algorithms (whitened
k-means, exact exchange, guarded Lloyd, soft rules) that solve them. The last two chapters
turn to what happens when scores themselves are estimated rather than known, and to how to
choose among everything that came before.

Every substantive statement is tagged as one of:

- **Theorem** — a mathematical claim with stated assumptions and a proof or proof sketch;
- **Proposition** — a narrower derived claim;
- **Numerical evidence** — a reproducible computation, not a proof;
- **Open problem** — a question for which this project does not claim a result.

Small analytic or rational laboratories illustrate exact claims throughout. The FlowCyt
cytometry study in the [evidence section](../usecases/flowcyt/index.md) is a capstone
application and never serves as proof of a theorem.

## Chapters

1. [Why bin at all](ch01-why-bin.md) — what hard binning costs and buys, and where the
   idea already appears across statistics, engineering, and physics.
2. [One dimension by hand](ch02-one-dimension.md) — the two-cell and \(K\)-cell Gaussian
   problem solved by symmetry and a fixed-point midpoint condition.
3. [Exact 1D binning by dynamic programming](ch03-exact-1d.md) — replacing symmetry
   arguments with an exact algorithm that works for any 1D law.
4. [Scores, score laws, and the three doors](ch04-scores-and-doors.md) — what a score
   vector is, and the three routes (analytic, sampled, learned) by which one arrives.
5. [Information after hard labels](ch05-information-after-binning.md) — the exact identity
   giving the Fisher information of any hard rule from its cell masses and score means.
6. [Two tasks and three optimization levels](ch06-two-tasks.md) — separating population
   design from finite assignment, and the criteria that rank a partition's information.
7. [The trace criterion and whitened k-means](ch07-trace-kmeans.md) — the cheapest scalar
   summary of retained information, and the weighted k-means problem it reduces to.
8. [D-optimality and exact exchange](ch08-d-optimality.md) — maximizing the determinant of
   retained information, and the exact-gain relocation algorithm that finds an exchange-stable
   partition.
9. [Mahalanobis geometry and guarded Lloyd](ch09-mahalanobis-lloyd.md) — the Voronoi
   structure a terminal D partition must have, and a faster batch algorithm that respects it.
10. [Nuisance parameters and profiled Ds](ch10-profiled-ds.md) — quantizing well for one
    parameter of interest while nuisance parameters are estimated alongside it.
11. [E-optimality, why not](ch11-e-optimality.md) — the classical worst-direction criterion,
    and the deterministic counterexample that keeps it out of the library.
12. [Soft rules, purification, and consistency](ch12-soft-rules.md) — making the finite
    objective differentiable, and the assumptions behind purification and consistency. These
    results do not guarantee that hardening a fitted soft rule preserves its objective.
13. [Estimated density ratios and scores](ch13-estimated-scores.md) — what changes
    when the score vectors themselves come from a trained classifier rather than a known law.
14. [Diagnostics and choosing a method](ch14-choosing-a-method.md) — a decision guide from
    problem shape to criterion, solver, and the checks that should accompany the answer.

## Suggested reading paths

**Practitioner fast path.** If you have a dataset, a parameter, and a bin budget, and you
want the shortest route to a defensible choice: Chapters 1, 4, 6, 8, and 14. That sequence
motivates hard binning, explains where scores come from, separates the two tasks you might
actually have, gives the default D-optimal criterion and algorithm, and ends at the
decision guide that routes you to everything else on demand.

**Full theory path.** Read in order, 1 through 14. Chapters 2 and 3 build intuition and an
exact algorithm on the 1D case that every later generalization specializes back to; Chapter
5 is the identity the rest of the book never re-derives; Chapters 7 through 12 are best read
together, since each criterion is introduced by contrast with the one before it. Chapters 13
and 14 assume everything earlier and are best read last.
