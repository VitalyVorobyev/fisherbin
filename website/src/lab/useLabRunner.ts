import {useCallback, useEffect, useRef, useState} from "react";

import {createRunRequest, isLabEvent, validateProblem} from "./protocol";
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
}

export function useLabRunner(): LabRunner {
  const workerRef = useRef<Worker | null>(null);
  const runIdRef = useRef<string | null>(null);
  const [state, setState] = useState<LabState>("idle");
  const [stage, setStage] = useState("Ready to run");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<LabResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const terminate = useCallback((): void => {
    workerRef.current?.terminate();
    workerRef.current = null;
    runIdRef.current = null;
  }, []);

  useEffect(() => terminate, [terminate]);

  const cancel = useCallback((): void => {
    if (workerRef.current === null) return;
    terminate();
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
    terminate();
    setResult(null);
    setError(null);
    setProgress(0.02);
    const request = createRunRequest(problem, runner);
    runIdRef.current = request.runId;
    if (runner === "fixture") {
      setState("complete");
      setStage("Loaded verified native NumPy fixture");
      return;
    }
    if (runner !== "pyodide-numpy") {
      setError(`${runner} is admitted by the protocol but has no approved runner in v1.`);
      setState("error");
      return;
    }
    setState("loading");
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
        terminate();
      }
      if (event.type === "error") {
        setError(event.message ?? "The browser runtime failed without a diagnostic.");
        setState("error");
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

  return {cancel, error, progress, result, run, stage, state};
}
