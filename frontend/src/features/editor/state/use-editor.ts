import {useReducer, useState} from 'react';
import type {Dispatch} from 'react';
import type {OperatorClient} from '../../../api/index.ts';
import {editorReducer, initialEditorState} from './editor-state.ts';
import type {EditorAction, EditorState} from './editor-state.ts';
import type {EditorSource} from './load.ts';
import {usePersistence} from './use-persistence.ts';
import type {Persistence} from './use-persistence.ts';
import {useUndo} from './use-undo.ts';
import type {UndoModel} from './use-undo.ts';
import {useValidation} from './use-validation.ts';

/**
 * What the application may ask of an open editor. Edits are saved as they are made, so only
 * a failed save leaves anything behind; `save` tries again.
 */
export interface DraftModel {
  readonly dirty: boolean;
  save(): Promise<'saved' | 'failed'>;
  discard(): void;
}
export interface EditorModel {
  readonly state: EditorState;
  readonly dispatch: Dispatch<EditorAction>;
  readonly persistence: Persistence;
  readonly recheck: () => void;
  readonly draft: DraftModel;
  /** Undo and Redo over the branch's history, and the status bar's notice. */
  readonly history: UndoModel;
}

/** The working copy with undo, debounced validation and autosave. */
export function useEditor(client: OperatorClient, source: EditorSource): EditorModel {
  const [state, dispatch] = useReducer(editorReducer, source.document, initialEditorState);
  const [attempt, setAttempt] = useState(0);
  useValidation(client, state, dispatch, attempt);
  const persistence = usePersistence(client, source, state.document, state.revision);
  const history = useUndo(client, source, state, dispatch);
  const draft: DraftModel = {
    dirty: persistence.status.kind === 'failed',
    save: async () => ((await persistence.flush()) ? 'saved' : 'failed'),
    discard: () => undefined,
  };
  const recheck = (): void => {
    setAttempt((value) => value + 1);
  };
  return {state, dispatch, persistence, recheck, draft, history};
}
