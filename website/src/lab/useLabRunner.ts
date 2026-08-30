import {useCallback, useEffect, useRef, useState} from "react";

import {PROTOCOL_VERSION, createRunRequest, isLabEvent, validateProblem} from "./protocol";
import type {LabEvent, LabProblem, LabResult, LabRunRequest} from "./protocol";

export type LabState = "idle" | "loading" | "running" | "complete" | "error" | "cancelled";

export interface LabRunner {
  cancel: () => void;
  error: string | null;
  progress: number;
  result: LabResult | null;
  run: (problem: LabProblem, runner: LabRunRequest["runner"]) => void;
  stage: string;
  state: LabState;
  /** Whether a warmed runtime is held, so the next run skips the cold start. */
  warm: boolean;
}

export function useLabRunner(): LabRunner {
  const workerRef = useRef<Worker | null>(null);
  const runIdRef = useRef<string | null>(null);
  const [state, setState] = useState<LabState>("idle");
  const [stage, setStage] = useState("Ready to run");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<LabResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [warm, setWarm] = useState(false);

  const terminate = useCallback((): void => {
    workerRef.current?.terminate();
    workerRef.current = null;
    runIdRef.current = null;
  }, []);

  useEffect(() => terminate, [terminate]);

  const cancel = useCallback((): void => {
    if (workerRef.current === null) return;
    terminate();
    setWarm(false);
    setState("cancelled");
    setStage("Run cancelled; the isolated worker was terminated");
    setProgress(0);
  }, [terminate]);

  const run = useCallback((problem: LabProblem, runner: LabRunRequest["runner"]): void => {
    const validationError = validateProblem(problem);
    if (validationError !== null) {
      setError(validationError);
      setState("error");
      return;
    }
    setResult(null);
    setError(null);
    setProgress(0.02);
    const request = createRunRequest(problem, runner);
    runIdRef.current = request.runId;
    if (runner === "fixture") {
      terminate();
      setState("complete");
      setStage("Loaded verified native NumPy fixture");
      return;
    }
    if (runner !== "pyodide-numpy") {
      terminate();
      setError(`${runner} is admitted by the protocol but has no approved runner in v${String(PROTOCOL_VERSION)}.`);
      setState("error");
      return;
    }
    setState("loading");
    const existing = workerRef.current;
    if (existing !== null) {
      setStage("Reusing the warm browser runtime");
      existing.postMessage(request);
      return;
    }
    setStage("Starting isolated browser worker");
    const worker = new Worker(new URL("./lab.worker.ts", import.meta.url), {type: "module"});
    workerRef.current = worker;
    worker.onmessage = (message: MessageEvent<unknown>): void => {
      if (!isLabEvent(message.data) || message.data.runId !== runIdRef.current) return;
      const event: LabEvent = message.data;
      if (event.stage !== undefined) setStage(event.stage);
      if (event.progress !== undefined) setProgress(event.progress);
      if (event.type === "ready" || event.type === "progress") setState(event.type === "ready" || (event.progress ?? 0) >= .65 ? "running" : "loading");
      if (event.type === "result" && event.result !== undefined) {
        setResult(event.result);
        setProgress(1);
        setState("complete");
        // The worker is deliberately kept alive: it holds the warmed Pyodide
        // runtime, and re-running with a different bin budget is the normal
        // interaction. Cancelling still terminates it.
        setWarm(true);
      }
      if (event.type === "error") {
        setError(event.message ?? "The browser runtime failed without a diagnostic.");
        setState("error");
        setWarm(false);
        terminate();
      }
    };
    worker.onerror = (): void => {
      setError("The local runtime could not start. The verified fixture remains available.");
      setState("error");
      terminate();
    };
    worker.postMessage(request);
  }, [terminate]);

  return {cancel, error, progress, result, run, stage, state, warm};
}
