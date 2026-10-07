import {useCallback, useEffect, useMemo, useSyncExternalStore} from 'react';
import type {Catalog, GraphDocument, OperatorClient} from '../../api/index.ts';
import {useRead} from '../../ui/index.ts';
import type {ReadResult} from '../../ui/index.ts';
import {EventTracker} from './event-tracker.ts';
import type {EventsState} from './event-tracker.ts';

/** The run's events, read page by page and polled while the run is active. */
export function useEvents(client: OperatorClient, runId: string): EventsState {
  const tracker = useMemo(
    () => new EventTracker(async (after, signal) => client.events(runId, after, signal)),
    [client, runId],
  );
  useEffect(() => {
    tracker.start();
    return () => {
      tracker.stop();
    };
  }, [tracker]);
  return useSyncExternalStore(tracker.subscribe, tracker.snapshot);
}

export interface ActivityContext {
  readonly catalog: Catalog;
  readonly document: GraphDocument;
}

/** The catalog and the saved version the run executed, for readable names. */
export function useActivityContext(
  client: OperatorClient,
  runId: string,
): ReadResult<ActivityContext> {
  const read = useCallback(
    async (signal: AbortSignal): Promise<ActivityContext> => {
      const [catalog, run] = await Promise.all([client.catalog(signal), client.run(runId, signal)]);
      return {catalog, document: await client.runDocument(run, signal)};
    },
    [client, runId],
  );
  return useRead(read);
}
