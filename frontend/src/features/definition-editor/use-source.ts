import {useEffect, useState} from 'react';
import type {DefinitionClient, GraphReference} from '../../api/index.ts';
import {initialDraft, MAX_SOURCE_BYTES, rejected, sourceSize} from './draft.ts';
import type {UpdateDraft} from './types.ts';

export function useSource(
  client: DefinitionClient,
  reference: GraphReference,
  update: UpdateDraft,
): () => void {
  const {graph_id, revision} = reference;
  const [generation, reload] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    void load(client, {graph_id, revision}, controller.signal, update);
    return () => {
      controller.abort();
    };
  }, [client, graph_id, revision, generation, update]);
  return () => {
    update(initialDraft());
    reload((value) => value + 1);
  };
}

async function load(
  client: DefinitionClient,
  reference: GraphReference,
  signal: AbortSignal,
  update: UpdateDraft,
): Promise<void> {
  try {
    const source = await client.source(reference, signal);
    if (!signal.aborted) receive(source, update);
  } catch (error) {
    if (!signal.aborted)
      update((state) =>
        rejected(state, error, 'Could not load the saved definition. Retry loading to continue.'),
      );
  }
}

function receive(source: string, update: UpdateDraft): void {
  if (sourceSize(source) > MAX_SOURCE_BYTES) {
    update((state) => ({
      ...state,
      pending: null,
      message: 'The saved definition exceeds the editor’s 1 MiB limit.',
    }));
    return;
  }
  update((state) => ({
    ...state,
    source,
    baseline: source,
    selectedSource: source,
    loaded: true,
    pending: null,
  }));
}
