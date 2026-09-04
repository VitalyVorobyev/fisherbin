import {readdirSync, readFileSync, statSync} from "node:fs";
import {dirname, join, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

// Spec T7: SITE_BASE in ../src/lib/site is the one place the portal's base
// path is allowed to live. This walks the whole `src` tree (never
// `node_modules` or `build`) and fails the moment the deployed prefix is
// written anywhere else.
const websiteRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const srcRoot = join(websiteRoot, "src");

function listFiles(dir: string): string[] {
  const entries = readdirSync(dir);
  const files: string[] = [];
  for (const entry of entries) {
    const path = join(dir, entry);
    const stat = statSync(path);
    if (stat.isDirectory()) {
      files.push(...listFiles(path));
    } else if (stat.isFile()) {
      files.push(path);
    }
  }
  return files;
}

describe("SITE_BASE is the only place the portal base path lives", () => {
  it("finds the portal prefix in src/lib/site.ts and nowhere else under website/src", () => {
    const offenders = listFiles(srcRoot)
      .filter((path) => readFileSync(path, "utf8").includes("scorequant/portal"))
      .map((path) => path.slice(websiteRoot.length + 1));
    expect(offenders).toEqual(["src/lib/site.ts"]);
  });
});
