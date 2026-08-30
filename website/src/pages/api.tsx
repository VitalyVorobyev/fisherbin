import {useMemo, useState} from "react";

import {AppShell} from "../components/AppShell";
import {PageIntro} from "../components/PageIntro";
import {portalData} from "../data/portal";

type Kind = "all" | "class" | "function";

export default function Api(): React.JSX.Element {
  const [kind, setKind] = useState<Kind>("all");
  const [query, setQuery] = useState("");
  const symbols = useMemo(() => {
    const search = query.trim().toLowerCase();
    return portalData.api.filter((symbol) => (kind === "all" || symbol.kind === kind) && `${symbol.name} ${symbol.summary}`.toLowerCase().includes(search));
  }, [kind, query]);
  return (
    <AppShell title="API" description="Generated ScoreQuant public API catalogue.">
      <PageIntro eyebrow="Generated public surface" title="An API you can inspect, not memorize." lead="Signatures and summaries are generated from the installed Python source with Griffe. The engineering reference remains canonical for complete field-level documentation." />
      <div className="content-grid">
        <aside className="side-index"><span>Symbol kind</span>{(["all", "class", "function"] as Kind[]).map((value) => <button key={value} className={kind === value ? "is-active" : ""} onClick={() => setKind(value)}>{value === "all" ? "All public symbols" : value === "class" ? "Classes" : "Functions"}</button>)}</aside>
        <section className="editorial-panel">
          <div className="filter-row"><input className="filter-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Filter by name or contract" aria-label="Filter API symbols"/><span className="tag">{symbols.length} symbols</span></div>
          <div className="provenance-note"><span aria-hidden="true">◇</span><span>Generated at build time from <code>scorequant.__all__</code>, Python signatures, NumPy-style docstrings, and source line locations.</span></div>
          <div className="api-list">
            {symbols.map((symbol) => (
              <article className="api-symbol" id={symbol.name.toLowerCase()} key={symbol.name}>
                <div className="api-symbol__top"><h2>{symbol.name}</h2><div className="api-symbol__links"><a href={symbol.source}>source ↗</a><a href={`/scorequant${symbol.reference}`}>full reference ↗</a></div></div>
                <code>{symbol.signature}</code><p>{symbol.summary || "Public contract documented in the canonical reference."}</p>
              </article>
            ))}
            {symbols.length === 0 && <p className="empty-state">No public symbol matches that filter.</p>}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
