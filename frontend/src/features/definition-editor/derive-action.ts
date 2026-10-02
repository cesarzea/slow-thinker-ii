import type {DefinitionClient, GraphReference} from '../../api/index.ts';
import {changeSource, locked, MAX_SOURCE_BYTES, rejected, sourceSize} from './draft.ts';
import type {DraftState, EditorModel, Requests, UpdateDraft} from './types.ts';

interface Context {
  readonly client: DefinitionClient;
  readonly reference: GraphReference;
  readonly requests: Requests;
  readonly update: UpdateDraft;
}

export function deriveAction(state: DraftState, context: Context): EditorModel['derive'] {
  return async (graphId, revision) => {
    if (locked(state) || state.source !== state.baseline) return;
    await generateDraft({graph_id: graphId, revision}, context);
  };
}

async function generateDraft(target: GraphReference, context: Context): Promise<void> {
  const {client, reference, requests, update} = context;
  const controller = requests.begin();
  update((state) => ({...state, pending: 'draft', validation: null, message: null, issues: []}));
  try {
    const source = await client.draft(
      {graph_id: reference.graph_id, revision: reference.revision},
      target,
      controller.signal,
    );
    if (!controller.signal.aborted) receive(source, update);
  } catch (error) {
    if (!controller.signal.aborted)
      update((state) => rejected(state, error, 'Could not create the revision draft. Try again.'));
  }
}

function receive(source: string, update: UpdateDraft): void {
  if (sourceSize(source) > MAX_SOURCE_BYTES) {
    update((state) => ({
      ...state,
      pending: null,
      message: 'The revision draft exceeds the editor’s 1 MiB UTF-8 limit.',
    }));
    return;
  }
  update((state) => changeSource(state, source));
}
