import type {ReactNode} from "react";

import {REFERENCE_BASE} from "../lib/site";

export interface ReferenceLinkProps {
  /** Path inside the MkDocs reference, without a leading slash: `examples/michelson-phase/`. */
  to: string;
  children: ReactNode;
}

/**
 * A link from a portal page into the MkDocs reference.
 *
 * The reference is a separately built site mounted beside the portal
 * (`REFERENCE_BASE`, ADR 0027), so this is a plain full-page anchor rather
 * than a router `Link`. Pages used to write `href="pathname:///reference/…"`
 * by hand; a raw MDX anchor is not routed through Docusaurus's link
 * handling, so that string reached the browser verbatim and was not a URL.
 */
export function ReferenceLink({to, children}: ReferenceLinkProps): React.JSX.Element {
  return (
    <a href={`${REFERENCE_BASE}${to.replace(/^\//, "")}`} target="_self">
      {children}
    </a>
  );
}
