import {useEffect, useState} from 'react';
import {errorMessage} from '../../api/index.ts';
import type {OperatorClient, RunSummary} from '../../api/index.ts';
import {isActive} from './run-rows.ts';

export const POLL_INTERVAL_MS = 5000;

interface RunList {
  readonly runs: readonly RunSummary[] | null;
  readonly error: string | null;
}
type Read = (signal: AbortSignal) => Promise<readonly RunSummary[]>;
type Update = (change: (list: RunList) => RunList) => void;

/**
 * Reads the runs now and again after each interval while any run read last is active.
 * A failed read keeps the runs read before. Returns the function that stops it.
 */
function poll(read: Read, update: Update): () => void {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  let active = false;
  const next = async (): Promise<void> => {
    try {
      const runs = await read(controller.signal);
      active = runs.some(isActive);
      if (!controller.signal.aborted) update(() => ({runs, error: null}));
    } catch (error) {
      if (!controller.signal.aborted) update((list) => ({...list, error: errorMessage(error)}));
    }
    if (active && !controller.signal.aborted)
      timer = setTimeout(() => {
        void next();
      }, POLL_INTERVAL_MS);
  };
  void next();
  return () => {
    controller.abort();
    clearTimeout(timer);
  };
}

/** The runs of one graph or of all graphs, newest first, polled while any is active. */
export function useRunList(
  client: OperatorClient,
  graphId: string | null,
): RunList & {readonly retry: () => void} {
  const [list, setList] = useState<RunList>({runs: null, error: null});
  const [attempt, setAttempt] = useState(0);
  useEffect(
    () => poll(async (signal) => client.runs(graphId ?? undefined, signal), setList),
    [client, graphId, attempt],
  );
  const retry = (): void => {
    setList((current) => ({...current, error: null}));
    setAttempt((value) => value + 1);
  };
  return {...list, retry};
}
