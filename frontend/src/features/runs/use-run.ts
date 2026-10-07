import {useEffect, useMemo, useSyncExternalStore} from 'react';
import type {OperatorClient} from '../../api/index.ts';
import {RunTracker} from './run-tracker.ts';
import type {RunState} from './run-tracker.ts';

/** The run, polled every second until it ends. */
export function useRun(client: OperatorClient, runId: string): RunState & {refresh: () => void} {
  const tracker = useMemo(
    () => new RunTracker(async (signal) => client.run(runId, signal)),
    [client, runId],
  );
  useEffect(() => {
    tracker.start();
    return () => {
      tracker.stop();
    };
  }, [tracker]);
  const state = useSyncExternalStore(tracker.subscribe, tracker.snapshot);
  return {
    ...state,
    refresh: () => {
      tracker.refresh();
    },
  };
}
