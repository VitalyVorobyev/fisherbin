import {cp, mkdir, rm} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

const website = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const project = resolve(website, "..");
const referenceSite = resolve(project, "site");
const portalSite = resolve(website, "build");
const preview = resolve(project, ".pages-preview");

// The preview mirrors the first migration stage: existing MkDocs URLs stay at
// the root while the learning portal is mounted at /portal/.
await rm(preview, {recursive: true, force: true});
await mkdir(preview, {recursive: true});
await cp(referenceSite, preview, {recursive: true});
await cp(portalSite, resolve(preview, "portal"), {recursive: true});

process.stdout.write(`Assembled dual-site preview at ${preview}.\n`);
