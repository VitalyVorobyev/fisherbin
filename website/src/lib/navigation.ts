/**
 * Route predicates shared by the shell.
 *
 * Takes a `pathname` straight from the router, which carries the site
 * `baseUrl` (see `SITE_BASE` in `./site`). It may not assume a fixed prefix,
 * so it matches on the trailing segments instead.
 */

function withoutTrailingSlash(pathname: string): string {
  return pathname.replace(/\/$/, "");
}

/**
 * Whether a primary navigation entry owns the current route.
 *
 * Posts, tag listings, and paginated indexes all live below their nav entry, so
 * a plain equality test would leave the tab unhighlighted on exactly the pages
 * that most need to say where the reader is.
 */
export function isActiveNavEntry(pathname: string, href: string): boolean {
  const normalized = withoutTrailingSlash(pathname);
  return normalized.endsWith(href) || normalized.includes(`${href}/`);
}
