import ErrorBoundary from "@docusaurus/ErrorBoundary";
import ErrorPageContent from "@theme/ErrorPageContent";
import type {Props} from "@theme/Layout";
import LayoutProvider from "@theme/Layout/Provider";
import type {ReactNode} from "react";

import {AppShell} from "../../components/AppShell";

/**
 * Renders every Docusaurus-routed page — the blog and the error pages — in the
 * same ScoreQuant shell as the hand-written routes.
 *
 * Only plugin-routed pages reach this component: everything under `src/pages`
 * mounts `AppShell` itself, so there is no second header or footer to collide
 * with. Metadata stays with Docusaurus, because `BlogPostPage`, `BlogListPage`
 * and `NotFound` each emit their own `PageMetadata`; `manageHead` is off so the
 * shell does not race them for the document title.
 */
export default function Layout({children, title, description}: Props): ReactNode {
  return (
    <LayoutProvider>
      <AppShell
        title={title ?? "ScoreQuant"}
        description={description ?? "Information-optimal score-space quantization."}
        manageHead={false}
      >
        <ErrorBoundary fallback={(params) => <ErrorPageContent {...params} />}>
          {children}
        </ErrorBoundary>
      </AppShell>
    </LayoutProvider>
  );
}
