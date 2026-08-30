interface PageIntroProps {
  eyebrow: string;
  lead: string;
  title: string;
}

export function PageIntro({eyebrow, lead, title}: PageIntroProps): React.JSX.Element {
  return (
    <header className="page-intro">
      <span className="eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p>{lead}</p>
    </header>
  );
}
