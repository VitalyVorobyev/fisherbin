import {useLocation} from "@docusaurus/router";
import type {Props} from "@theme/BlogLayout";
import Layout from "@theme/Layout";
import clsx from "clsx";
import type {ReactNode} from "react";

import {PageIntro} from "../../components/PageIntro";
import {isBlogPostList} from "../../lib/navigation";

/**
 * The blog's reading frame.
 *
 * Replaces the stock Infima `container/row/col` grid for two reasons: it keeps
 * the portal's own measure and spacing tokens, and the stock version nests a
 * second `<main>` inside the one `AppShell` already renders, which is both
 * invalid HTML and a duplicate-landmark failure in the accessibility scan.
 *
 * The index gets the same `PageIntro` header every other portal route leads
 * with — which is also the page's only `h1`, since Docusaurus renders post
 * titles as `h2` in a list.
 *
 * The `sidebar` prop is deliberately not rendered: `blogSidebarCount` is 0, and
 * the index page plus the post paginator carry navigation instead of a
 * recent-posts rail that would arrive with foreign styling. It rides along in
 * the rest, which `Layout` ignores.
 */
export default function BlogLayout({children, toc, ...layoutProps}: Props): ReactNode {
  const {pathname} = useLocation();
  return (
    <Layout {...layoutProps}>
      {isBlogPostList(pathname) && (
        <PageIntro
          eyebrow="Development blog"
          title="What changed, and why it matters"
          lead="Plain-English notes on the research and the library, written as each arc lands. Negative results get posts too — the things we proved impossible are what tell us which code to write next."
        />
      )}
      <div className={clsx("blog-frame", toc && "blog-frame--with-toc")}>
        <div className="blog-frame__content">{children}</div>
        {toc && <aside className="blog-frame__toc">{toc}</aside>}
      </div>
    </Layout>
  );
}
