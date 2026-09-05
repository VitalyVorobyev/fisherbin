import type {ReactNode} from "react";

/** `@theme/Layout` for vitest: the page body with no site chrome. */
export default function Layout({children}: {children?: ReactNode; description?: string; title?: string}): React.JSX.Element {
  return <div data-testid="layout">{children}</div>;
}
