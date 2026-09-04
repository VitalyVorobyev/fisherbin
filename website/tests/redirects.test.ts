import {readFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

/**
 * The parity evidence ADR 0019 requires (spec T2/T3, done criteria).
 *
 * This checks only the manifest's own shape — that it is internally
 * consistent and covers the pre-cut sitemap count. It cannot check that
 * every stub actually exists in the assembled tree, or that every stub's
 * target resolves to a real page there, because Vitest never builds that
 * tree. `website/scripts/assemble-site.mjs` runs that half of the parity
 * check itself, right after it writes the tree, and fails the build loudly
 * if a stub is missing or a target does not resolve.
 */

interface RedirectEntry {
  from: string;
  to: string;
}

interface UnstubbedEntry {
  path: string;
  // Optional in the type, required in the file: this is parsed from disk, so the
  // type is an assertion about JSON that nothing has checked yet. The last test in
  // this file is what actually enforces that the field is present and substantive.
  reason?: string;
}

interface RedirectsManifest {
  redirects: RedirectEntry[];
  schemaVersion: number;
  sourceSitemapCount: number;
  unstubbed: UnstubbedEntry[];
}

const websiteRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const manifest = JSON.parse(readFileSync(resolve(websiteRoot, "redirects.json"), "utf8")) as RedirectsManifest;

describe("website/redirects.json", () => {
  it("covers exactly the pre-cut sitemap count", () => {
    expect(manifest.sourceSitemapCount).toBe(manifest.unstubbed.length + manifest.redirects.length);
  });

  it("has no duplicate `from`, and no `from` collides with an unstubbed path", () => {
    const froms = manifest.redirects.map((entry) => entry.from);
    expect(new Set(froms).size).toBe(froms.length);

    const unstubbedPaths = new Set(manifest.unstubbed.map((entry) => entry.path));
    const collisions = froms.filter((from) => unstubbedPaths.has(from));
    expect(collisions).toEqual([]);
  });

  it("every `from` ends with a trailing slash", () => {
    const offenders = manifest.redirects.filter((entry) => !entry.from.endsWith("/"));
    expect(offenders).toEqual([]);
  });

  it("every `to` ends with a trailing slash", () => {
    const offenders = manifest.redirects.filter((entry) => !entry.to.endsWith("/"));
    expect(offenders).toEqual([]);
  });

  it("every unstubbed path is either the empty string or ends with a trailing slash", () => {
    const offenders = manifest.unstubbed.filter((entry) => entry.path !== "" && !entry.path.endsWith("/"));
    expect(offenders).toEqual([]);
  });

  // Every stub points into the MkDocs reference, because that is where the
  // pre-cut content went — with one deliberate exception. `three-doors.md` was
  // retired in S8 rather than moved, and the four walkthroughs are what replaced
  // it, so its URL is the one stub whose target is a portal route. Listing the
  // exception here rather than relaxing the rule keeps the next one deliberate too.
  const PORTAL_TARGETED = new Map([["three-doors/", "walkthroughs/ratios/"]]);

  it("every `to` starts with reference/, except the deliberately listed portal targets", () => {
    const offenders = manifest.redirects.filter(
      (entry) => !entry.to.startsWith("reference/") && PORTAL_TARGETED.get(entry.from) !== entry.to
    );
    expect(offenders).toEqual([]);
  });

  it("every deliberately portal-targeted redirect is still in the manifest", () => {
    // Guards the exception from outliving its reason: if the entry is deleted or
    // re-pointed, this fails and the allowance above must be revisited.
    const byFrom = new Map(manifest.redirects.map((entry) => [entry.from, entry.to]));
    for (const [from, to] of PORTAL_TARGETED) {
      expect(byFrom.get(from)).toBe(to);
    }
  });

  // An unstubbed entry is a URL that silently stops redirecting, so the reason it
  // is safe has to travel with it. Four are excluded today: the site root and
  // reference/, api/ and examples/ — each because a portal route now occupies the
  // URL and answers the same question. A one-word reason would defeat the point.
  it("every unstubbed path carries a substantive reason", () => {
    const offenders = manifest.unstubbed.filter((entry) => (entry.reason ?? "").trim().length < 40);
    expect(offenders).toEqual([]);
  });
});
