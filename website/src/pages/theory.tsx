import {useEffect, useMemo, useState} from "react";

import {AppShell} from "../components/AppShell";
import {portalData} from "../data/portal";

export default function Theory(): React.JSX.Element {
  const [chapter, setChapter] = useState(0);
  const [progress, setProgress] = useState(0);
  const selected = portalData.content.chapters[chapter] ?? portalData.content.chapters[0];
  const sourceHref = `/scorequant${selected?.reference ?? "/book/"}`;
  useEffect(() => {
    const update = (): void => {
      const range = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(range > 0 ? Math.min(100, (window.scrollY / range) * 100) : 0);
    };
    update();
    window.addEventListener("scroll", update, {passive: true});
    return () => window.removeEventListener("scroll", update);
  }, []);
  const readingMinutes = useMemo(() => Math.max(4, Math.round((selected?.excerpt.length ?? 0) / 45)), [selected]);
  return (
    <AppShell title="Theory" description="A guided mathematical account of information-preserving hard binning.">
      <div className="reading-progress" style={{width: `${progress}%`}} aria-hidden="true" />
      <header className="page-intro"><span className="eyebrow">Score-space monograph</span><h1>Theory with the failure modes left in.</h1><p>Read the structure from first principles, then follow theorem dependencies, counterexamples, and implementation consequences into the research record.</p></header>
      <div className="theory-layout">
        <nav className="chapter-list" aria-label="Book chapters">
          {portalData.content.chapters.map((item, index) => <a key={item.slug} className={chapter === index ? "is-active" : ""} href={`#${item.slug}`} onClick={(event) => {event.preventDefault(); setChapter(index); window.scrollTo({top: 420, behavior: "smooth"});}}>{item.title}</a>)}
        </nav>
        <article className="theory-reader" id={selected?.slug}>
          <span className="eyebrow">Chapter {chapter + 1} of {portalData.content.chapters.length}</span>
          <h1>{selected?.title}</h1>
          <p className="lede">{selected?.excerpt}…</p>
          <h2>The object we preserve</h2>
          <p>A hard label is useful precisely because it is cheap to store, transmit, count, and explain. Its cost is the variation of the score that remains inside each cell. Conditional expectation makes that accounting exact.</p>
          <div className="math-display">I<sub>q</sub> = Var(E[s | q(s)]) = Σ<sub>b</sub> W<sub>b</sub> μ<sub>b</sub> μ<sub>b</sub><sup>T</sup></div>
          <aside className="callout"><span>Theorem · information accounting</span><strong>Hard quantization cannot add Fisher information.</strong><p>The gap is the expected within-cell score covariance. It is positive semidefinite, not a metaphorical “loss”.</p></aside>
          <h2>Geometry is a consequence, not the starting point</h2>
          <p>In whitened score coordinates, the trace criterion becomes weighted k-means. D-optimality uses a metric that depends on the retained information itself. This difference is why the library keeps criteria and their admissible solver behavior explicit.</p>
          <aside className="callout callout--counterexample"><span>Counterexample boundary</span><strong>A fixed-point geometry need not certify a global optimum.</strong><p>ScoreQuant records the exact stability or certification statement it can support; attractive pictures do not silently strengthen it.</p></aside>
          <p><a className="plain-link" href={sourceHref}>Continue in the complete canonical chapter →</a></p>
        </article>
        <aside className="reading-meta"><strong>Reading notes</strong><p>{readingMinutes} min portal introduction</p><p>Complete derivation and citations are linked from the canonical chapter.</p><p><button className="filter-chip" onClick={() => window.print()}>Print chapter</button></p></aside>
      </div>
    </AppShell>
  );
}
