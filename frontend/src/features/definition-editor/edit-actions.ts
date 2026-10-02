import {
  changeSource,
  DraftError,
  importSource,
  locked,
  MAX_SOURCE_BYTES,
  sourceSize,
} from './draft.ts';
import type {DraftState, EditorModel, Requests, UpdateDraft} from './types.ts';

type Editing = Pick<EditorModel, 'edit' | 'importFile' | 'discard'>;

export function editActions(state: DraftState, update: UpdateDraft, requests: Requests): Editing {
  return {
    edit: (source) => {
      if (!locked(state)) replaceSource(source, update, requests);
    },
    importFile: async (file) => {
      if (locked(state)) return;
      await readImport(file, update, requests);
    },
    discard: () => {
      discard(state, update, requests);
    },
  };
}

function discard(state: DraftState, update: UpdateDraft, requests: Requests): void {
  if (
    !state.loaded ||
    state.pending === 'save' ||
    state.pending === 'import' ||
    state.pending === 'draft'
  )
    return;
  requests.cancel();
  update({
    ...changeSource(state, state.selectedSource),
    baseline: state.selectedSource,
    uncertain: false,
    frozenSource: null,
    message: state.uncertain
      ? 'Draft discarded. The previous save may have succeeded; refresh the library to inspect it.'
      : 'Draft discarded.',
  });
}

function replaceSource(source: string, update: UpdateDraft, requests: Requests): void {
  requests.cancel();
  if (sourceSize(source) > MAX_SOURCE_BYTES) {
    update((state) => ({
      ...state,
      pending: null,
      validation: null,
      issues: [],
      message: 'JSON text exceeds the 1 MiB UTF-8 limit.',
    }));
    return;
  }
  update((state) => changeSource(state, source));
}

async function readImport(file: File, update: UpdateDraft, requests: Requests): Promise<void> {
  const controller = requests.begin();
  update((state) => ({...state, pending: 'import', validation: null, message: null, issues: []}));
  try {
    const source = await importSource(file);
    if (!controller.signal.aborted) update((state) => changeSource(state, source));
  } catch (error) {
    if (!controller.signal.aborted)
      update((state) => ({
        ...state,
        pending: null,
        message: error instanceof DraftError ? error.message : 'Could not read the JSON file.',
      }));
  }
}
