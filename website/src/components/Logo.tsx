import Link from "@docusaurus/Link";

interface LogoProps {
  compact?: boolean;
}

export function Logo({compact = false}: LogoProps): React.JSX.Element {
  return (
    <Link className="brand" to="/" aria-label="ScoreQuant home">
      <img src="/scorequant/portal/img/mark.svg" width="34" height="34" alt="" />
      {!compact && (
        <span className="brand__word">
          Score<span>Quant</span>
        </span>
      )}
    </Link>
  );
}
