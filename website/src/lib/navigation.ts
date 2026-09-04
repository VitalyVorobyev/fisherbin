/**
 * Route predicates shared by the shell and the blog frame.
 *
 * Both take a `pathname` straight from the router, which carries the site
 * `baseUrl` (see `SITE_BASE` in `./site`). Neither may assume a fixed prefix,
 * so both match on the trailing segments instead.
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

/** Whether a route is the blog index or one of its numbered pages. */
export function isBlogPostList(pathname: string): boolean {
  const normalized = withoutTrailingSlash(pathname);
  return normalized.endsWith("/blog") || /\/blog\/page\/\d+$/.test(normalized);
}

/**
 * Whether a route is the Lab page.
 *
 * Matches only the route's final path segment, so it is unaffected by the
 * site's base path and by `trailingSlash: true` alike — `/scorequant/lab/`
 * and `/scorequant/lab` both match, `/scorequant/` does not, and a route that
 * merely contains "lab" as a substring of a different segment (e.g.
 * `/scorequant/collab/`) does not either.
 */
export function isLabRoute(pathname: string): boolean {
  const segments = withoutTrailingSlash(pathname).split("/");
  return segments[segments.length - 1] === "lab";
}
