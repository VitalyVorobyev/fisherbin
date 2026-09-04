import type {ComponentProps} from "react";

import MDXComponents from "@theme-original/MDXComponents";

/**
 * A Markdown table that a keyboard can reach.
 *
 * The portal renders wide tables as their own horizontal scroll container
 * (`.doc-article .markdown table { overflow-x: auto }`), which is what keeps a
 * wide comparison readable on a phone. A region that scrolls must be reachable
 * by keyboard, or its off-screen columns exist only for pointer users; the
 * accessibility scan reports it as a serious violation on the Pixel 7 viewport.
 * A tab stop on the table itself is the smallest fix that restores it.
 */
function Table(props: ComponentProps<"table">): React.JSX.Element {
  return <table {...props} tabIndex={0} />;
}

export default {...MDXComponents, table: Table};
