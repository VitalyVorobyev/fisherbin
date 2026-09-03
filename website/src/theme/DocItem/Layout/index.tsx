import {useDoc} from "@docusaurus/plugin-content-docs/client";
import ContentVisibility from "@theme/ContentVisibility";
import DocItemContent from "@theme/DocItem/Content";
import DocItemPaginator from "@theme/DocItem/Paginator";
import type {Props} from "@theme/DocItem/Layout";
import type {ReactNode} from "react";

/**
 * The article frame for the two docs-plugin routes, `/walkthroughs` and `/research`.
 *
 * The stock `DocItem/Layout` cannot run inside the ScoreQuant shell. Its table of
 * contents calls `useTOCHighlight`, which reads
 * `document.querySelector(".navbar").clientHeight` to offset anchors against the
 * Docusaurus navbar. This portal renders its own header from `AppShell` and has no
 * `.navbar` element, so that query returns `null` and every docs page with headings
 * throws `Cannot read properties of null (reading 'clientHeight')` during hydration —
 * the page renders correctly on the server and then crashes to Docusaurus's error
 * boundary in the browser.
 *
 * So the contents list below is built directly from `useDoc().toc` instead: plain
 * anchor links, no scroll-spy, no dependency on a navbar that does not exist. The
 * stock Infima `row`/`col` grid, breadcrumbs, version banners and the edit/tags
 * footer are dropped with it — neither instance is versioned and neither sets
 * `editUrl`.
 *
 * `ContentVisibility` is kept: it is what warns a reader that a page is a draft or
 * unlisted, which is a correctness signal rather than theming.
 */
export default function DocItemLayout({children}: Props): ReactNode {
  const {metadata, frontMatter, toc} = useDoc();
  const showToc = frontMatter.hide_table_of_contents !== true && toc.length > 1;
  return (
    <div className={showToc ? "doc-article doc-article--with-toc" : "doc-article"}>
      <article className="doc-article__body">
        <ContentVisibility metadata={metadata} />
        <DocItemContent>{children}</DocItemContent>
        <DocItemPaginator />
      </article>
      {showToc && (
        <nav className="doc-article__toc" aria-label="On this page">
          <span className="doc-article__toc-title">On this page</span>
          <ul>
            {toc.map((heading) => (
              <li key={heading.id} data-level={heading.level}>
                <a href={`#${heading.id}`}>{heading.value}</a>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </div>
  );
}
