import Link from "@docusaurus/Link";

import {siteUrl} from "../lib/site";

interface LogoProps {
  compact?: boolean;
}

export function Logo({compact = false}: LogoProps): React.JSX.Element {
  return (
    <Link className="brand" to="/" aria-label="ScoreQuant home">
      <img src={siteUrl("img/mark.svg")} width="34" height="34" alt="" />
      {!compact && (
        <span className="brand__word">
          Score<span>Quant</span>
        </span>
      )}
    </Link>
  );
}
