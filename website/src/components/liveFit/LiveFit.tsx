import {useEffect, useRef, useState} from "react";
import type {ComponentType} from "react";

import {useLiveFit} from "./LiveFitProvider";
import type {LiveFitProblemLoader, LiveFitResult, LiveFitRunnerProps} from "./types";

const BLOCKED_MESSAGE = "Only one live demo can run at a time on this page. Finish or reset the active one first.";

export interface LiveFitProps {
  /** Short prose shown above the button, explaining what activation does. */
  activationHint?: string;
  /** Accessible name of the activation button. */
  activationLabel: string;
  /** Human label for what the committed number measures. */
  committedLabel: string;
  /** The number already published on the page. */
  committedRetention: number;
  /** How to render a retention value as text, matching the page's own convention. */
  formatRetention: (value: number) => string;
  /** A stable id, unique on the page, this demo claims from `LiveFitProvider`. */
  id: string;
  /** Human label for what the reader's own run measures. */
  liveLabel: string;
  /**
   * Which number to show as "your browser's run", read from the result.
   * Forwarded to `LiveFitRunner` unchanged; see `LiveFitRunnerProps`.
   */
  liveValue?: (result: LiveFitResult) => number;
  /** Resolve the problem to actually run, once activated. */
  problem: LiveFitProblemLoader;
  /**
   * Render extra content below the two result cards, once a result exists.
   * Forwarded to `LiveFitRunner` unchanged; see `LiveFitRunnerProps`.
   */
  renderResult?: (result: LiveFitResult) => React.ReactNode;
}

/**
 * The committed result, plus one button that reruns the fit in the reader's
 * own browser.
 *
 * Always in the route chunk it is used from: this component imports only
 * React, `LiveFitProvider` (a plain context, no runtime) and presentational
 * markup. It must never import `runtimeClient`, `useLabRunner`, or anything
 * else that reaches the browser runtime -- `website/tests/e2e/portal.spec.ts`
 * asserts that an ordinary route issues zero requests matching
 * `/pyodide|marimo|scorequant-.*\.whl/`, and importing the runtime here,
 * rather than behind the click, would break that.
 *
 * `LiveFitRunner` -- the component that actually talks to the runtime -- is
 * reached only through `await import("./LiveFitRunner")` inside the click
 * handler below, which is what keeps it out of this chunk. Before that click
 * this renders the committed result and exactly one `<button>`; after it,
 * this hands off entirely to the runner, which owns its own status,
 * cancel/reset control, and side-by-side results.
 */
export function LiveFit(props: LiveFitProps): React.JSX.Element {
  const {
    activationHint,
    activationLabel,
    committedLabel,
    committedRetention,
    formatRetention,
    id,
    liveLabel,
    liveValue,
    problem,
    renderResult
  } = props;
  const {isBlocked, release, requestActivation} = useLiveFit(id);
  const [Runner, setRunner] = useState<ComponentType<LiveFitRunnerProps> | null>(null);
  const [loading, setLoading] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);

  // `useLiveFit` returns a fresh `release` closure on every render (it is not
  // memoized), so depending on it directly would fire this effect's cleanup
  // on every render rather than only on unmount -- which would release this
  // demo's just-granted claim the moment `handleClick` below causes its own
  // next render. The ref keeps the effect itself mount/unmount-only while
  // still calling whatever `release` is current when that actually happens.
  const releaseRef = useRef(release);
  releaseRef.current = release;

  // Release this demo's claim on the site-wide activation slot whenever it
  // leaves the page (a client-side route change), regardless of whether it
  // was ever granted -- `release` is a no-op for an id that does not hold it.
  useEffect(() => () => releaseRef.current(), []);

  const handleClick = (): void => {
    if (!requestActivation()) return; // `isBlocked` already renders the explanation below.
    setImportError(null);
    setLoading(true);
    void import("./LiveFitRunner")
      .then((module) => setRunner(() => module.LiveFitRunner))
      .catch((cause: unknown) => {
        release();
        setImportError(cause instanceof Error ? cause.message : String(cause));
      })
      .finally(() => setLoading(false));
  };

  if (Runner !== null) {
    const runnerProps: LiveFitRunnerProps = {
      committedLabel,
      committedRetention,
      formatRetention,
      liveLabel,
      onRelease: () => {
        release();
        setRunner(null);
      },
      problem
    };
    // Under `exactOptionalPropertyTypes`, assigning only when defined keeps
    // an absent optional prop absent rather than explicitly `undefined`.
    if (liveValue !== undefined) runnerProps.liveValue = liveValue;
    if (renderResult !== undefined) runnerProps.renderResult = renderResult;
    return <Runner {...runnerProps} />;
  }

  return (
    <div className="live-fit">
      <div className="live-fit__committed" aria-live="polite">
        <span className="live-fit__badge">Committed result</span>
        <span className="live-fit__value">{formatRetention(committedRetention)}</span>
        <span className="live-fit__caption">{committedLabel}</span>
      </div>
      {activationHint !== undefined && <p className="live-fit__description">{activationHint}</p>}
      <button
        className="live-fit__button"
        type="button"
        onClick={handleClick}
        disabled={loading || isBlocked}
        aria-busy={loading}
      >
        {loading ? "Loading the browser runtime…" : activationLabel}
      </button>
      {isBlocked && (
        <p className="live-fit__refusal" role="alert">
          {BLOCKED_MESSAGE}
        </p>
      )}
      {importError !== null && (
        <p className="live-fit__refusal" role="alert">
          {importError}
        </p>
      )}
    </div>
  );
}
