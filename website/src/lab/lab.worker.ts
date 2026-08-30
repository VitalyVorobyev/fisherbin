/// <reference lib="webworker" />

import {isLabEvent} from "./protocol";
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

function emit(event: LabEvent): void {
  if (!isLabEvent(event)) throw new Error("Worker attempted to emit an invalid event.");
  scope.postMessage(event);
}

async function run(request: LabRunRequest): Promise<void> {
  const base = `${scope.location.origin}${portalRoot}`;
  const manifestResponse = await fetch(`${base}runtime/manifest.json`);
  if (!manifestResponse.ok) throw new Error("The pinned local runtime manifest is unavailable.");
  const manifest = await manifestResponse.json() as RuntimeManifest;
  emit({protocolVersion: 1, runId: request.runId, type: "progress", stage: `Loading Pyodide ${manifest.pyodideVersion}`, progress: .12});
  const pyodideModuleURL = "/scorequant/portal/runtime/pyodide/pyodide.mjs";
  const pyodideModule = await import(/* webpackIgnore: true */ pyodideModuleURL) as PyodideModule;
  const pyodide = await pyodideModule.loadPyodide({indexURL: new URL(manifest.indexURL, base).href});
  emit({protocolVersion: 1, runId: request.runId, type: "progress", stage: "Installing the local ScoreQuant wheel", progress: .48});
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
  emit({protocolVersion: 1, runId: request.runId, type: "ready", stage: "Running ScoreQuant with the NumPy backend", progress: .7});
  const runner = pyodide.pyimport("scorequant_browser_lab");
  const result = JSON.parse(runner.run_lab(JSON.stringify(request.problem))) as unknown;
  const event: LabEvent = {protocolVersion: 1, runId: request.runId, type: "result", stage: "Native browser run complete", progress: 1, result: result as NonNullable<LabEvent["result"]>};
  emit(event);
}

scope.onmessage = (message: MessageEvent<LabRunRequest>): void => {
  const request = message.data;
  void run(request).catch((error: unknown) => {
    emit({protocolVersion: 1, runId: request.runId, type: "error", message: error instanceof Error ? error.message : String(error)});
  });
};
