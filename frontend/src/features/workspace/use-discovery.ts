import {useEffect, useMemo, useState} from 'react';
import type {Dispatch, SetStateAction} from 'react';
import {ConfigurationClient} from '../../api/index.ts';
import type {ConfigurationCatalog} from '../../api/index.ts';
export interface DiscoveryState {
  readonly catalog: ConfigurationCatalog | null;
  readonly error: string | null;
  readonly loading: boolean;
  readonly refresh: () => void;
}
type DiscoveryValue = Omit<DiscoveryState, 'refresh'>;
export function useDiscovery(credential: string | undefined): DiscoveryState {
  const [state, update] = useState<DiscoveryValue>({
    catalog: null,
    error: null,
    loading: credential !== undefined,
  });
  const [generation, setGeneration] = useState(0);
  const client = useMemo(
    () => (credential === undefined ? null : new ConfigurationClient(credential)),
    [credential],
  );
  useEffect(() => {
    if (client === null) return;
    const controller = new AbortController();
    void loadDiscovery(client, controller, update);
    return () => {
      controller.abort();
    };
  }, [client, generation]);
  return {
    ...state,
    refresh: () => {
      update((previous) => ({...previous, loading: true, error: null}));
      setGeneration((value) => value + 1);
    },
  };
}
async function loadDiscovery(
  client: ConfigurationClient,
  controller: AbortController,
  update: Dispatch<SetStateAction<DiscoveryValue>>,
): Promise<void> {
  try {
    const catalog = await client.catalog(controller.signal);
    if (!controller.signal.aborted) update({catalog, error: null, loading: false});
  } catch {
    if (!controller.signal.aborted)
      update((previous) => ({
        ...previous,
        error: 'Could not load configuration discovery. Refresh to try again.',
        loading: false,
      }));
  }
}
