import {editorReducer, initialEditorState} from '../../src/features/editor/state/editor-state.ts';
import type {EditorAction, EditorState} from '../../src/features/editor/state/editor-state.ts';
import {renameNode} from '../../src/features/editor/state/document.ts';
import type {Diagnostic} from '../../src/api/index.ts';
import {j1} from './contract.ts';

export const error: Diagnostic = {
  severity: 'error',
  code: 'service_not_selected',
  message: 'Select a model.',
  path: '/nodes/1/config/model',
  node_id: 'proposer',
};
export const warning: Diagnostic = {
  ...error,
  severity: 'warning',
  code: 'no_output_node',
  node_id: null,
};

export const run = (state: EditorState, ...actions: EditorAction[]): EditorState =>
  actions.reduce(editorReducer, state);
export const saved = (): EditorState => initialEditorState(j1);
export const keep: EditorAction = {type: 'change', update: (document) => document};
export const rename = (name: string): EditorAction => ({
  type: 'change',
  update: (document) => renameNode(document, 'story', name),
});
export const checked = (revision: number, diagnostics: Diagnostic[] = []): EditorAction => ({
  type: 'checked',
  revision,
  diagnostics,
});
