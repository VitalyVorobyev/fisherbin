import {cp, mkdir, readFile, rm, stat, writeFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

const website = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const project = resolve(website, "..");
const portalBuild = resolve(website, "build");
const referenceSite = resolve(project, "site");
const landing = resolve(project, "landing");
const assembled = resolve(project, ".pages-preview");
const redirectsManifestPath = resolve(website, "redirects.json");

// Three surfaces, one tree (ADR 0027): the landing page owns the site root,
// the MkDocs documentation is mounted at /docs/, and the Docusaurus portal at
// /portal/. The landing page is a directory of static files with no build
// step; the other two are the outputs of `mkdocs build --strict` and
// `docusaurus build` (whose `baseUrl` must match the mount point).
await rm(assembled, {recursive: true, force: true});
await mkdir(assembled, {recursive: true});
await cp(landing, assembled, {recursive: true});
await cp(referenceSite, resolve(assembled, "docs"), {recursive: true});
await cp(portalBuild, resolve(assembled, "portal"), {recursive: true});

/**
 * The redirect stub template (spec T3).
 *
 * `noindex` keeps the stub out of search results so the canonical target is
 * what gets indexed. The visible link is for a reader whose browser blocks
 * the refresh.
 */
function stubHtml(toAbsolute, toFull) {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Moved — ScoreQuant</title>
    <link rel="canonical" href="${toFull}" />
    <meta http-equiv="refresh" content="0; url=${toAbsolute}" />
    <meta name="robots" content="noindex" />
  </head>
  <body>
    <p>This page moved to <a href="${toAbsolute}">${toAbsolute}</a>.</p>
  </body>
</html>
`;
}

async function fileExists(path) {
  try {
    const info = await stat(path);
    return info.isFile();
  } catch {
    return false;
  }
}

const manifest = JSON.parse(await readFile(redirectsManifestPath, "utf8"));

/**
 * A stub must never overwrite real content (ADR 0025, kept by ADR 0027).
 *
 * Today nothing but the landing page lives at the root beside the stubs, so
 * a collision would mean a landing file, a new top-level mount, or a manifest
 * entry that names one of them. This check turns that into a loud build
 * failure instead of a silently replaced page.
 */
for (const {from, to} of manifest.redirects) {
  const toAbsolute = `/scorequant/${to}`;
  const toFull = `https://vitalyvorobyev.github.io/scorequant/${to}`;
  const stubPath = resolve(assembled, from, "index.html");
  if (await fileExists(stubPath)) {
    process.stderr.write(
      `assemble:site: refusing to write a redirect stub over real content.\n` +
        `  "${from}" already exists in the assembled tree at ${stubPath}.\n` +
        `  Either drop "${from}" from website/redirects.json (recording it under\n` +
        `  "unstubbed" with the reason), or rename the route it collides with.\n`,
    );
    process.exit(1);
  }
  await mkdir(dirname(stubPath), {recursive: true});
  await writeFile(stubPath, stubHtml(toAbsolute, toFull));
}

/**
 * Self-verification (spec item 4).
 *
 * `website/tests/redirects.test.ts` cannot check that every stub exists and
 * every stub's target resolves to a real page, because Vitest never builds
 * the assembled tree. This is that same parity check, run here instead,
 * right after the tree it needs exists. CI gets the parity evidence from
 * `pnpm assemble:site` failing loudly; the Vitest suite only checks the
 * manifest's own shape.
 */
const failures = [];

for (const {from} of manifest.redirects) {
  const stubPath = resolve(assembled, from, "index.html");
  if (!(await fileExists(stubPath))) {
    failures.push(`missing stub for "${from}": expected ${stubPath}`);
  }
}

for (const {from, to} of manifest.redirects) {
  const targetPath = resolve(assembled, to, "index.html");
  if (!(await fileExists(targetPath))) {
    failures.push(`redirect "${from}" -> "${to}" does not resolve: expected ${targetPath}`);
  }
}

/**
 * The landing page may only link to pages that exist (ADR 0027).
 *
 * It is hand-written HTML with no build step and no link checker of its own,
 * so this resolves every site-relative `href` it carries against the tree
 * just assembled. A directory URL must hold an `index.html`; anything else
 * must be a file. External links and fragments are not checked here.
 */
const landingHtml = await readFile(resolve(assembled, "index.html"), "utf8");
const landingHrefs = [...landingHtml.matchAll(/href="([^"#?]+)"/g)].map((match) => match[1]);
for (const href of landingHrefs) {
  if (/^[a-z]+:/.test(href) || href.startsWith("//")) continue;
  const target = href.endsWith("/") ? resolve(assembled, href, "index.html") : resolve(assembled, href);
  if (!(await fileExists(target))) {
    failures.push(`landing link "${href}" does not resolve: expected ${target}`);
  }
}

if (failures.length > 0) {
  process.stderr.write("assemble:site: redirect and landing-link parity check failed:\n");
  for (const failure of failures) process.stderr.write(`  - ${failure}\n`);
  process.exit(1);
}

process.stdout.write(`Assembled site at ${assembled} (landing page at the root, MkDocs under docs/, portal under portal/, ${manifest.redirects.length} redirect stubs and ${landingHrefs.length} landing links verified).\n`);
