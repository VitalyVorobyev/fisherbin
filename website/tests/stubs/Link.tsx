import type {AnchorHTMLAttributes, ReactNode} from "react";

/** `@docusaurus/Link` for vitest: a plain anchor with `to` mapped to `href`. */
export default function Link({to, children, ...rest}: AnchorHTMLAttributes<HTMLAnchorElement> & {to?: string; children?: ReactNode}): React.JSX.Element {
  return (
    <a href={to ?? rest.href} {...rest}>
      {children}
    </a>
  );
}
