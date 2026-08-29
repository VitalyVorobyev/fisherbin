import {execFile} from "node:child_process";
import {copyFile, mkdir, mkdtemp, readdir, readFile, rm, writeFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import {basename, dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {promisify} from "node:util";

const execute = promisify(execFile);
const website = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const project = resolve(website, "..");
const runtime = resolve(website, "static/runtime");
const manifest = JSON.parse(await readFile(resolve(runtime, "manifest.json"), "utf8"));
const temporary = await mkdtemp(resolve(tmpdir(), "scorequant-pyodide-"));

try {
  const archive = resolve(temporary, `pyodide-${manifest.pyodideVersion}.tar.bz2`);
  const release = `https://github.com/pyodide/pyodide/releases/download/${manifest.pyodideVersion}/pyodide-${manifest.pyodideVersion}.tar.bz2`;
  const response = await fetch(release);
  if (!response.ok) throw new Error(`Unable to download pinned Pyodide release: ${response.status}`);
  await writeFile(archive, Buffer.from(await response.arrayBuffer()));
  const pyodide = resolve(runtime, "pyodide");
  await rm(pyodide, {recursive: true, force: true});
  await mkdir(pyodide, {recursive: true});
  await execute("tar", ["-xjf", archive, "-C", pyodide, "--strip-components=1"]);

  const lock = JSON.parse(await readFile(resolve(pyodide, "pyodide-lock.json"), "utf8"));
  const retainedRuntimeFiles = new Set([
    "pyodide.mjs",
    "pyodide.asm.js",
    "pyodide.asm.wasm",
    "python_stdlib.zip",
    "pyodide-lock.json",
    lock.packages.micropip.file_name,
    lock.packages.numpy.file_name
  ]);
  for (const entry of await readdir(pyodide)) {
    if (!retainedRuntimeFiles.has(entry)) await rm(resolve(pyodide, entry), {recursive: true, force: true});
  }

  const wheelOutput = resolve(temporary, "wheels");
  await mkdir(wheelOutput, {recursive: true});
  await execute("uv", ["build", "--wheel", "--out-dir", wheelOutput], {cwd: project});
  const wheelName = basename(manifest.scorequantWheel);
  await mkdir(resolve(runtime, "wheels"), {recursive: true});
  await copyFile(resolve(wheelOutput, wheelName), resolve(runtime, "wheels", wheelName));
  process.stdout.write(`Prepared pinned Pyodide ${manifest.pyodideVersion} and ${wheelName}.\n`);
} finally {
  await rm(temporary, {recursive: true, force: true});
}
