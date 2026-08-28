Yes, but I would weaken “easily establish the full list” to:

> **We can establish a very strong, auditable approximation to the full relevant literature by systematic citation-graph traversal.**

For this project, citation tracing should probably be the **main literature-discovery mechanism**, with keyword search as a secondary safety net.

The reason is that our topic sits at the intersection of several mature literatures:

* optimal quantization for estimation / Fisher information;
* optimal experimental design;
* vector quantization and clustering;
* determinant-based clustering;
* distributed estimation;
* inference-aware categorization in HEP;
* computational geometry / affine partitions;
* local-search and exchange algorithms.

Within each of these communities, the citation graph is usually much more reliable than guessing modern terminology.

### I would use bidirectional snowballing

Start from perhaps 10–20 highly relevant “anchor papers.” For each one:

$$
\text{paper}
\rightarrow
\begin{cases}
\text{references} & \text{backward search}\\
\text{papers citing it} & \text{forward search}
\end{cases}
$$

Then recursively inspect anything that appears mathematically relevant.

For example, if Barnes–Han–Özgür cites earlier Fisher-information quantization work, follow that chain backward. Then inspect everything citing Barnes–Han–Özgür for later multivariate extensions.

Similarly, start a separate graph around determinant clustering, another around Kiefer–Wolfowitz/Whittle optimal-design theory, another around score quantization, etc. The graphs will eventually begin connecting.

### The useful stopping criterion

I would not stop after some arbitrary number of papers. Stop when we reach **citation saturation**:

> After another traversal round, newly discovered papers are overwhelmingly duplicates, tangential works, or applications containing no new relevant theorem.

That is much stronger evidence of coverage than “we searched Google Scholar for five phrases.”

We can even make this measurable:

```text
round 1: 42 candidate papers, 18 relevant
round 2: 31 new candidates, 9 relevant
round 3: 17 new candidates, 3 relevant
round 4: 8 new candidates, 0 relevant
```

At that point our claim of literature coverage becomes defensible.

## But citation tracing alone is not enough

There are a few important failure modes.

**Terminology islands.** Two communities can solve essentially the same problem without citing one another. This is particularly dangerous for us because something we call “D-optimal score quantization” may appear elsewhere as determinant clustering, categorical experiment design, finite-alphabet estimation, information-preserving partitioning, etc.

**Old books and proceedings.** Important results may live in monographs or conference proceedings that have incomplete citation indexing.

**Independent rediscovery.** A paper can derive something relevant without knowing the older literature and therefore give us no citation path into it.

**Very recent work.** Forward citation graphs lag for recent preprints.

So I would combine citation traversal with a second procedure:

$$
\boxed{
\text{citation graph}
+
\text{concept search}
+
\text{author/venue search}
}
$$

Concept search is not just searching our terminology. For every theorem, generate several alternative mathematical descriptions.

For `D-EXCHANGE-IMPLIES-VORONOI`, for example, searches should involve concepts such as:

* determinant criterion clustering;
* one-point relocation determinant;
* exchange-stable partition;
* Mahalanobis Voronoi determinant;
* between-cluster scatter determinant;
* local optimum determinant partition;
* Hartigan determinant clustering;
* D-optimal quantization.

That catches disconnected terminology.

## I would make literature discovery itself a project artifact

Something like:

```text
LITERATURE/
    seeds.md
    graph.json
    reviewed.md
    rejected.md
    gaps.md
```

And for every paper record:

```text
id
title
year
authors
source_of_discovery
cites_relevant
cited_by_relevant
research_area
relevant_claims
status:
    unread
    screened
    deeply_reviewed
    irrelevant
```

Then the literature graph becomes reproducible rather than residing in agent context.

Most importantly, a paper should be linked to **claim IDs** rather than merely being labelled “relevant to ScoreQuant.”

For example:

```text
D-EXCHANGE-EXACT
    paper A: possibly prior
    paper B: analogous objective
    paper C: different scatter matrix

D-EXCHANGE-IMPLIES-VORONOI
    no direct antecedent found
    paper D: related Hartigan result
    paper E: Voronoi characterization under trace objective
```

This makes novelty auditing dramatically cleaner.

### One subtle point

There are really two literature searches:

**Field coverage search**

> Have we found essentially all important papers around the problem?

and

**Novelty search**

> Has anybody previously proved this exact theorem, perhaps under another formulation?

The first can converge through citation saturation.

The second is harder and should be repeated **after we know exactly what our theorem says**. Otherwise we are searching for a moving target.

So I would put a major citation-graph reconstruction fairly early in the roadmap, but retain a final adversarial claim-by-claim novelty search near publication.

For ScoreQuant, this should be quite tractable because we already have several excellent anchor nodes—Fisher-information quantization papers, Barnes–Han–Özgür, Dülek, classical determinant clustering, Kiefer–Wolfowitz/Whittle, Hartigan-style clustering, and HEP inference-aware binning. Starting from those and recursively snowballing should give us a much stronger literature map than our current ad-hoc bibliography.
