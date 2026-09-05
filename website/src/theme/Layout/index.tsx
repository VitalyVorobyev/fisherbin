import ErrorBoundary from "@docusaurus/ErrorBoundary";
import {PageMetadata} from "@docusaurus/theme-common";
import ErrorPageContent from "@theme/ErrorPageContent";
import type {Props} from "@theme/Layout";
import LayoutProvider from "@theme/Layout/Provider";
import type {ReactNode} from "react";

import {AppShell} from "../../components/AppShell";

/**
 * Renders every route in the portal — the hand-written `src/pages` routes as
 * well as the Docusaurus-plugin-routed pages (the error pages) — through the
 * same `LayoutProvider` and the same ScoreQuant shell. This is the one seam
 * every route passes through, which is what makes `useColorMode()` callable
 * everywhere.
 *
 * `PageMetadata` is rendered first, exactly as stock
 * `@docusaurus/theme-classic`'s own `Layout` does: `NotFound` nests its own
 * `PageMetadata` further inside, and React Helmet's last-wins semantics make
 * that nesting resolve correctly with no toggle needed here.
 */
export default function Layout({children, title, description}: Props): ReactNode {
  const resolvedTitle = title ?? "ScoreQuant";
  const resolvedDescription = description ?? "Information-optimal score-space quantization.";
  return (
    <LayoutProvider>
      <PageMetadata title={resolvedTitle} description={resolvedDescription} />
      <AppShell>
        <ErrorBoundary fallback={(params) => <ErrorPageContent {...params} />}>
          {children}
        </ErrorBoundary>
      </AppShell>
    </LayoutProvider>
  );
}
