import {DefinitionError} from '../../api/index.ts';
import type {DefinitionClient, GraphReference, SaveResult} from '../../api/index.ts';
import {locked, rejected} from './draft.ts';
import type {DraftState, EditorModel, Requests, UpdateDraft} from './types.ts';

interface Context {
  readonly client: DefinitionClient;
  readonly requests: Requests;
  readonly update: UpdateDraft;
  readonly onSaved: (reference: GraphReference) => void;
}

export function writeActions(
  state: DraftState,
  context: Context,
): Pick<EditorModel, 'validate' | 'save' | 'retry'> {
  return {
    validate: async () => {
      if (!locked(state)) await validateSource(state.source, context);
    },
    save: async () => {
      if (!locked(state) && state.validation !== null && state.pending === null)
        await saveSource(state.source, context);
    },
    retry: async () => {
      if (state.uncertain && state.frozenSource !== null && state.pending === null)
        await saveSource(state.frozenSource, context);
    },
  };
}

async function validateSource(source: string, context: Context): Promise<void> {
  const {client, requests, update} = context;
  const controller = requests.begin();
  update((state) => ({...state, pending: 'validate', validation: null, message: null, issues: []}));
  try {
    const validation = await client.validate(source, controller.signal);
    if (!controller.signal.aborted) update((state) => ({...state, validation, pending: null}));
  } catch (error) {
    if (!controller.signal.aborted)
      update((state) => rejected(state, error, 'Could not validate the definition. Try again.'));
  }
}

async function saveSource(source: string, context: Context): Promise<void> {
  const {client, requests, update, onSaved} = context;
  const controller = requests.begin();
  update((state) => ({
    ...state,
    pending: 'save',
    frozenSource: source,
    uncertain: false,
    message: null,
    issues: [],
  }));
  let saved: SaveResult;
  try {
    saved = await client.save(source, controller.signal);
  } catch (error) {
    if (!controller.signal.aborted) update((state) => failedSave(state, error));
    return;
  }
  if (controller.signal.aborted) return;
  update((state) => confirmedSave(state, saved));
  onSaved(saved);
}

function confirmedSave(state: DraftState, saved: SaveResult): DraftState {
  return {
    ...state,
    source: state.selectedSource,
    baseline: state.selectedSource,
    pending: null,
    frozenSource: null,
    uncertain: false,
    validation: null,
    message: `${saved.created ? 'Definition saved' : 'Identical saved definition confirmed'}: ${saved.graph_id} · ${saved.revision}.`,
  };
}

function failedSave(state: DraftState, error: unknown): DraftState {
  if (error instanceof DefinitionError) {
    return {
      ...rejected(state, error, 'Could not save the definition.'),
      frozenSource: null,
      uncertain: false,
    };
  }
  return {
    ...state,
    pending: null,
    uncertain: true,
    issues: [],
    message: 'Save unconfirmed. It may already be saved. Retry the unchanged source to confirm.',
  };
}
