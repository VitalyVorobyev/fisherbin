import {createContext, useContext, useMemo, useState} from "react";

interface LiveFitContextValue {
  activeId: string | null;
  release: (id: string) => void;
  requestActivation: (id: string) => boolean;
}

const LiveFitContext = createContext<LiveFitContextValue | null>(null);

export interface LiveFitProviderProps {
  children: React.ReactNode;
}

/**
 * Governs how many browser-runtime demos may be activated at once, site-wide.
 *
 * Mounted once in `AppShell.tsx`. The Lab's shared worker
 * (`website/src/lab/runtimeClient.ts`) already refuses to hold two Pyodide
 * heaps for one tab; this is the same rule one layer up, before a second
 * `LiveFit` ever gets to ask the runtime for anything. A second activation
 * while one demo is active is refused outright rather than queued -- there is
 * no place on any of these pages where waiting silently for a turn would make
 * sense to a reader who just clicked a button.
 */
export function LiveFitProvider({children}: LiveFitProviderProps): React.JSX.Element {
  const [activeId, setActiveId] = useState<string | null>(null);

  const value = useMemo<LiveFitContextValue>(
    () => ({
      activeId,
      release: (id: string) => setActiveId((current) => (current === id ? null : current)),
      requestActivation: (id: string) => {
        if (activeId !== null && activeId !== id) return false;
        setActiveId(id);
        return true;
      }
    }),
    [activeId]
  );

  return <LiveFitContext.Provider value={value}>{children}</LiveFitContext.Provider>;
}

export interface LiveFitSlot {
  /** Whether another demo (not this one) currently holds the slot. */
  isBlocked: boolean;
  /** Release this id's claim, if it holds one. Safe to call unconditionally. */
  release: () => void;
  /** Claim the slot for `id`. Returns whether the claim was granted. */
  requestActivation: () => boolean;
}

/**
 * One `LiveFit` instance's view of the site-wide activation slot.
 *
 * Throws outside a `LiveFitProvider` rather than degrading silently: a demo
 * that cannot coordinate with the rest of the page must not pretend it can.
 */
export function useLiveFit(id: string): LiveFitSlot {
  const context = useContext(LiveFitContext);
  if (context === null) throw new Error("useLiveFit must be used within a LiveFitProvider.");
  return {
    isBlocked: context.activeId !== null && context.activeId !== id,
    release: () => context.release(id),
    requestActivation: () => context.requestActivation(id)
  };
}
