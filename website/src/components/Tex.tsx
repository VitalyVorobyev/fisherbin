import katex from "katex";

export interface TexProps {
  /** A TeX expression, without dollar delimiters. */
  children: string;
  /** Render as a centred block rather than inline. */
  display?: boolean;
}

/**
 * KaTeX for React pages that are not MDX.
 *
 * The walkthroughs get TeX through `remark-math`; a `src/pages` component
 * does not. `renderToString` is a pure function of its input, so the server
 * render and the client's first render agree and there is nothing to hydrate
 * differently. `throwOnError` turns a typo in an expression into a build
 * failure rather than red text on the published page.
 */
export function Tex({children, display = false}: TexProps): React.JSX.Element {
  const html = katex.renderToString(children, {displayMode: display, throwOnError: true});
  return display ? (
    <div className="tex-display" dangerouslySetInnerHTML={{__html: html}} />
  ) : (
    <span className="tex-inline" dangerouslySetInnerHTML={{__html: html}} />
  );
}
