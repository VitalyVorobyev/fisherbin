/// <reference lib="webworker" />

import {PROTOCOL_VERSION, isLabEvent} from "./protocol";
import type {LabEvent, LabRunRequest} from "./protocol";

interface RuntimeManifest {
  indexURL: string;
  pythonRunner: string;
  pyodideVersion: string;
  scorequantWheel: string;
}

interface PyodideRuntime {
  loadPackage: (packages: string | string[]) => Promise<void>;
  pyimport: (name: string) => {run_lab: (payload: string) => string};
  runPythonAsync: (code: string) => Promise<unknown>;
}

interface PyodideModule {
  loadPyodide: (options: {indexURL: string}) => Promise<PyodideRuntime>;
}

const scope = self as unknown as DedicatedWorkerGlobalScope;
const portalRoot = "/scorequant/portal/";

/**
 * The warmed runtime, kept across runs.
 *
 * Bootstrapping Pyodide, loading NumPy and installing the wheel costs seconds.
 * A playground is used by changing one control and running again, so paying
 * that on every run would make the interaction unusable. The worker is still
 * terminated to cancel -- that is what makes a cancel immediate -- and the next
 * run after a cancel pays the cold start again.
 */
let runtime: Promise<{run_lab: (payload: string) => string}> | null = null;

/**
 * Import a module the bundler must not look at.
 *
 * Pyodide is a pinned static asset of the assembled site, not a dependency of
 * this bundle, and it has to stay out of the module graph. No form of
 * `import()` expresses that here. `webpackIgnore` is honoured only on a string
 * literal, and the client compile does honour it - but the server compile then
 * tries to resolve that absolute path on disk and fails the build. Passing a
 * variable instead makes webpack build a context module, which compiles to
 * __webpack_require__ helpers; a worker chunk carries the webpack runtime only
 * while it happens to own a copy, which is a property of the whole graph and
 * not of this file. That is why it worked until the development blog was added
 * and the worker began dying on `__webpack_require__ is not defined` before
 * Pyodide was ever fetched.
 *
 * Constructing the importer puts the specifier beyond static reach, so nothing
 * is emitted, nothing is resolved on the server, and no runtime is required.
 * The rule this suppresses guards against evaluating attacker-influenced
 * strings; the evaluated string is the constant below, and the URL it receives
 * is built from this worker's own origin. Pyodide additionally cannot run in a
 * context that forbids eval, so no policy permitting Pyodide forbids this line.
 */
// eslint-disable-next-line @typescript-eslint/no-implied-eval -- constant code, same-origin URL; see above
const importAtRuntime = new Function("url", "return import(url);") as (
  url: string
) => Promise<unknown>;

function emit(event: LabEvent): void {
  if (!isLabEvent(event)) throw new Error("Worker attempted to emit an invalid event.");
  scope.postMessage(event);
}

async function bootstrap(runId: string): Promise<{run_lab: (payload: string) => string}> {
  const base = `${scope.location.origin}${portalRoot}`;
  const manifestResponse = await fetch(`${base}runtime/manifest.json`);
  if (!manifestResponse.ok) throw new Error("The pinned local runtime manifest is unavailable.");
  const manifest = (await manifestResponse.json()) as RuntimeManifest;
  emit({protocolVersion: PROTOCOL_VERSION, runId, type: "progress", stage: `Loading Pyodide ${manifest.pyodideVersion}`, progress: .12});
  const pyodideModule = (await importAtRuntime(
    `${base}runtime/pyodide/pyodide.mjs`
  )) as PyodideModule;
  const pyodide = await pyodideModule.loadPyodide({indexURL: new URL(manifest.indexURL, base).href});
  emit({protocolVersion: PROTOCOL_VERSION, runId, type: "progress", stage: "Installing the local ScoreQuant wheel", progress: .48});
  await pyodide.loadPackage(["micropip", "numpy"]);
  const wheelURL = new URL(manifest.scorequantWheel, base).href;
  await pyodide.runPythonAsync(`import micropip\nawait micropip.install(${JSON.stringify(wheelURL)}, deps=False)`);
  const runnerResponse = await fetch(new URL(manifest.pythonRunner, base));
  if (!runnerResponse.ok) throw new Error("The browser runner module is unavailable.");
  const runnerSource = await runnerResponse.text();
  await pyodide.runPythonAsync(
    "import sys, types\n" +
    "scorequant_browser_lab = types.ModuleType('scorequant_browser_lab')\n" +
    `exec(${JSON.stringify(runnerSource)}, scorequant_browser_lab.__dict__)\n` +
    "sys.modules['scorequant_browser_lab'] = scorequant_browser_lab"
  );
  return pyodide.pyimport("scorequant_browser_lab");
}

async function run(request: LabRunRequest): Promise<void> {
  const warm = runtime !== null;
  // Assigned before awaiting so two runs queued back to back share one
  // bootstrap rather than racing two Pyodide instances into the same worker.
  runtime ??= bootstrap(request.runId);
  let runner: {run_lab: (payload: string) => string};
  try {
    runner = await runtime;
  } catch (error) {
    runtime = null; // A failed bootstrap must not be cached as the warm runtime.
    throw error;
  }
  emit({
    protocolVersion: PROTOCOL_VERSION,
    runId: request.runId,
    type: "ready",
    stage: warm ? "Running on the warm browser runtime" : "Running ScoreQuant with the NumPy backend",
    progress: warm ? .35 : .7
  });
  const result = JSON.parse(runner.run_lab(JSON.stringify(request.problem))) as unknown;
  emit({
    protocolVersion: PROTOCOL_VERSION,
    runId: request.runId,
    type: "result",
    stage: warm ? "Warm browser run complete" : "Native browser run complete",
    progress: 1,
    result: result as NonNullable<LabEvent["result"]>
  });
}

scope.onmessage = (message: MessageEvent<LabRunRequest>): void => {
  const request = message.data;
  void run(request).catch((error: unknown) => {
    emit({protocolVersion: PROTOCOL_VERSION, runId: request.runId, type: "error", message: error instanceof Error ? error.message : String(error)});
  });
};
