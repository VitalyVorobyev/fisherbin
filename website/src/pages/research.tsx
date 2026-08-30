import {AppShell} from "../components/AppShell";
import {PageIntro} from "../components/PageIntro";
import {portalData} from "../data/portal";

const positions = [[7, 8], [54, 9], [10, 39], [56, 39], [32, 72]] as const;

export default function Research(): React.JSX.Element {
  return (
    <AppShell title="Research" description="Curated ScoreQuant research history and public claim graph.">
      <PageIntro eyebrow="Field history and claim provenance" title="A map of what is known—and at what level." lead="Literature results, project bridges, proved claims, numerical evidence, and counterexamples remain distinguishable. Only explicitly approved registry entries appear here." />
      <section className="section-wrap research-layout">
        <div>
          <span className="mono-label">A short lineage</span>
          <div className="timeline" style={{marginTop: 24}}>
            <article><time>1935</time><h2>Fisher information</h2><p>A local metric for the information carried by observations about model parameters.</p></article>
            <article><time>1950s–1980s</time><h2>Quantization and optimal design</h2><p>Separate traditions develop rate-distortion, Lloyd geometry, and determinant criteria.</p></article>
            <article><time>Modern likelihood-free inference</time><h2>Scores become learnable interfaces</h2><p>Classifiers and differentiable simulators make score-like representations available in richer models.</p></article>
            <article><time>ScoreQuant</time><h2>The task boundary is made explicit</h2><p>Finite assignment, reusable quantization, exact certificates, and estimated-score caveats live in one contract.</p></article>
          </div>
        </div>
        <div>
          <div className="section-heading"><div><span className="mono-label">Public claim preview</span><h2>Dependencies before conclusions.</h2></div></div>
          <div className="claim-graph" aria-label="Curated research claim dependency graph">
            {portalData.research.slice(1).map((claim, index) => {
              const start = positions[0];
              const end = positions[index + 1];
              if (end === undefined) return null;
              const dx = (end[0] - start[0]) * 5.7;
              const dy = (end[1] - start[1]) * 5.8;
              return <i key={`edge-${claim.id}`} className="claim-edge" style={{left: `${start[0] + 13}%`, top: `${start[1] + 5}%`, width: Math.hypot(dx, dy), transform: `rotate(${Math.atan2(dy, dx)}rad)`}} />;
            })}
            {portalData.research.map((claim, index) => {
              const position = positions[index] ?? [10, 10];
              return <article className="claim-node" id={claim.id.toLowerCase()} key={claim.id} style={{left: `${position[0]}%`, top: `${position[1]}%`}}><small>{claim.status.replace("_", " ")} · {claim.level.replace("_", " ")}</small><strong>{claim.title}</strong></article>;
            })}
          </div>
          <p className="provenance-note" style={{marginTop: 20}}><span aria-hidden="true">◇</span><span>This graph contains {portalData.research.length} allowlisted claims. Presence in the internal research registry alone never publishes a claim.</span></p>
        </div>
      </section>
    </AppShell>
  );
}
