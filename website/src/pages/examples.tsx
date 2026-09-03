import {useMemo, useState} from "react";

import {AppShell} from "../components/AppShell";
import {PageIntro} from "../components/PageIntro";
import {portalData} from "../data/portal";
import {REFERENCE_BASE, siteUrl} from "../lib/site";

const filters = ["all", "scores", "densities", "ratios", "browser", "theory", "benchmark", "certificate"] as const;

export default function Examples(): React.JSX.Element {
  const [filter, setFilter] = useState<(typeof filters)[number]>("all");
  const [query, setQuery] = useState("");
  const examples = useMemo(() => portalData.content.examples.filter((example) => {
    const matchesTag = filter === "all" || (example.tags?.includes(filter) ?? false);
    const matchesQuery = `${example.title} ${example.excerpt} ${example.tags?.join(" ") ?? ""}`.toLowerCase().includes(query.trim().toLowerCase());
    return matchesTag && matchesQuery;
  }), [filter, query]);
  return (
    <AppShell title="Examples" description="Reproducible ScoreQuant workflows indexed by task and representation.">
      <PageIntro eyebrow="Executable learning paths" title="One honest workflow at a time." lead="Examples are selected from the maintained Python documentation and indexed by input door, criterion, solver, and browser compatibility." />
      <section className="section-wrap">
        <div className="filter-row">
          <input className="filter-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search workflows" aria-label="Search examples"/>
          {filters.map((value) => <button key={value} className={`filter-chip ${filter === value ? "is-active" : ""}`} onClick={() => setFilter(value)}>{value}</button>)}
        </div>
        <div className="provenance-note"><span aria-hidden="true">◇</span><span>Each card links to the canonical page in the reference. The reference&rsquo;s own <a href={`${REFERENCE_BASE}examples/`}>examples overview</a> lists every one of them in reading order.</span></div>
        <div className="example-grid">
          {examples.map((example) => (
            <a className="example-card" key={example.slug} href={siteUrl(example.reference)}>
              <div className="example-card__tags">{example.tags?.map((tag) => <span className="tag" key={tag}>{tag}</span>)}</div>
              <h2>{example.title}</h2><p>{example.excerpt}…</p><span>Read canonical example →</span>
            </a>
          ))}
          {examples.length === 0 && <p className="empty-state">No maintained workflow matches both filters.</p>}
        </div>
      </section>
    </AppShell>
  );
}
