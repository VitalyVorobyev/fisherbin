import {cp, mkdir, readFile, rm, stat, writeFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

const website = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const project = resolve(website, "..");
const portalBuild = resolve(website, "build");
const referenceSite = resolve(project, "site");
const assembled = resolve(project, ".pages-preview");
const redirectsManifestPath = resolve(website, "redirects.json");

// The portal owns the site root; MkDocs is mounted under /reference/ beneath
// it (spec: docs/programme/S06-portal-topology-and-reference-cut.md, "Design
// decisions — topology"). This is the post-cut layout: it no longer mirrors
// a "first migration stage" where MkDocs held the root and the portal was a
// subdirectory under it.
await rm(assembled, {recursive: true, force: true});
await mkdir(assembled, {recursive: true});
await cp(portalBuild, assembled, {recursive: true});
await cp(referenceSite, resolve(assembled, "reference"), {recursive: true});

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
 * A stub must never overwrite real content (ADR 0025).
 *
 * Several old MkDocs URLs share a name with a portal route: `/api/` and
 * `/examples/` are both. They do not collide on disk today only because
 * `trailingSlash: false` makes the portal emit `api.html` rather than
 * `api/index.html`. That is a property of one config line, not of the design,
 * so flipping `trailingSlash` would silently replace portal pages with
 * redirect stubs. This check turns that into a loud build failure instead.
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

if (failures.length > 0) {
  process.stderr.write("assemble:site: redirect parity check failed:\n");
  for (const failure of failures) process.stderr.write(`  - ${failure}\n`);
  process.exit(1);
}

process.stdout.write(`Assembled site at ${assembled} (portal at the root, MkDocs under reference/, ${manifest.redirects.length} redirect stubs verified).\n`);
