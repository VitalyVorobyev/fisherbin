import Link from "@docusaurus/Link";

import {TAG_KIND_LABELS, WALKTHROUGHS, type TagKind, type WalkthroughCard} from "../data/walkthroughs";

const TAG_ORDER: readonly TagKind[] = ["task", "input", "criterion", "solver", "data"];

function Card({card}: {card: WalkthroughCard}): React.JSX.Element {
  return (
    <article className="walkthrough-card" aria-labelledby={`walkthrough-${card.slug}`}>
      <h2 id={`walkthrough-${card.slug}`}>
        <Link to={card.href}>{card.title}</Link>
      </h2>
      <p>{card.summary}</p>
      <dl className="walkthrough-card__tags">
        {TAG_ORDER.map((kind) => {
          const tags = card.tags.filter((tag) => tag.kind === kind);
          if (tags.length === 0) return null;
          return (
            <div key={kind}>
              <dt>{TAG_KIND_LABELS[kind]}</dt>
              {tags.map((tag) => (
                <dd key={tag.label}>{kind === "data" ? tag.label : <code>{tag.label}</code>}</dd>
              ))}
            </div>
          );
        })}
      </dl>
    </article>
  );
}

/** The card grid on the walkthroughs index. */
export function WalkthroughCards(): React.JSX.Element {
  return (
    <div className="walkthrough-cards">
      {WALKTHROUGHS.map((card) => (
        <Card key={card.slug} card={card} />
      ))}
    </div>
  );
}
