import type {ComponentDeclaration, Diagnostic, GraphDocument} from '../../../api/index.ts';
import {freePosition} from './defaults.ts';
import {addNode, uniqueNodeId} from './document.ts';

/** The working copy being edited, its diagnostics and this session's undo history. */
export interface EditorState {
  readonly document: GraphDocument;
  /** Counts document changes; validation and autosave follow it. */
  readonly revision: number;
  readonly diagnostics: readonly Diagnostic[];
  readonly checked: number;
  readonly checkFailure: string | null;
  readonly selected: string | null;
  /** Earlier documents of this session, most recent last, and the documents undone. */
  readonly past: readonly GraphDocument[];
  readonly future: readonly GraphDocument[];
  /** The branch's changes before this session, oldest first: undo reaches them after `past`. */
  readonly saved: readonly number[];
}
type Update = (document: GraphDocument) => GraphDocument;
export type EditorAction =
  | {readonly type: 'change'; readonly update: Update; readonly select?: string | null}
  | {
      readonly type: 'add';
      readonly declaration: ComponentDeclaration;
      readonly position?: readonly [number, number];
    }
  | {
      readonly type: 'applied';
      readonly document: GraphDocument;
      readonly diagnostics: readonly Diagnostic[];
    }
  | {
      readonly type: 'checked';
      readonly revision: number;
      readonly diagnostics: readonly Diagnostic[];
    }
  | {readonly type: 'check-failed'; readonly revision: number; readonly message: string}
  | {readonly type: 'select'; readonly nodeId: string | null}
  | {readonly type: 'replace'; readonly document: GraphDocument}
  | {readonly type: 'undo'}
  | {readonly type: 'redo'}
  | {readonly type: 'seed'; readonly changes: readonly number[]}
  | {readonly type: 'undo-saved'; readonly change: number; readonly document: GraphDocument};
type Handler<A> = (state: EditorState, action: A) => EditorState;
type Handlers = {readonly [K in EditorAction['type']]: Handler<Extract<EditorAction, {type: K}>>};

/** Undo reaches this many changes back. */
const HISTORY_LIMIT = 100;

export function initialEditorState(document: GraphDocument): EditorState {
  return {
    document,
    revision: 0,
    diagnostics: [],
    checked: -1,
    checkFailure: null,
    selected: null,
    past: [],
    future: [],
    saved: [],
  };
}

const existing = (document: GraphDocument, id: string | null): string | null =>
  document.nodes.some((node) => node.id === id) ? id : null;

/** Show another document without touching the undo history. */
function shown(state: EditorState, document: GraphDocument): EditorState {
  return {
    ...state,
    document,
    revision: state.revision + 1,
    checkFailure: null,
    selected: existing(document, state.selected),
  };
}

function changed(state: EditorState, document: GraphDocument, select?: string | null): EditorState {
  if (document === state.document && select === undefined) return state;
  const next =
    document === state.document
      ? state
      : {
          ...shown(state, document),
          past: [...state.past, state.document].slice(-HISTORY_LIMIT),
          future: [],
        };
  return {...next, selected: existing(document, select === undefined ? state.selected : select)};
}

function added(state: EditorState, action: Extract<EditorAction, {type: 'add'}>): EditorState {
  const id = uniqueNodeId(state.document, action.declaration.type);
  const position = action.position ?? freePosition(state.document);
  const document = addNode(state.document, action.declaration, [position[0], position[1]], id);
  return changed(state, document, id);
}

const handlers: Handlers = {
  change: (state, action) => changed(state, action.update(state.document), action.select),
  add: added,
  applied: (state, action) => ({
    ...changed(state, action.document),
    diagnostics: action.diagnostics,
    checked: state.revision + 1,
  }),
  checked: (state, action) =>
    action.revision === state.revision
      ? {...state, diagnostics: action.diagnostics, checked: action.revision, checkFailure: null}
      : state,
  'check-failed': (state, action) =>
    action.revision === state.revision ? {...state, checkFailure: action.message} : state,
  select: (state, action) => ({...state, selected: action.nodeId}),
  replace: (state, action) => changed(state, action.document),
  undo: (state) => {
    const previous = state.past.at(-1);
    if (previous === undefined) return state;
    const future = [state.document, ...state.future];
    return {...shown(state, previous), past: state.past.slice(0, -1), future};
  },
  seed: (state, action) => ({...state, saved: action.changes.slice(-HISTORY_LIMIT)}),
  'undo-saved': (state, action) => {
    if (state.past.length > 0 || state.saved.at(-1) !== action.change) return state;
    const future = [state.document, ...state.future];
    return {...shown(state, action.document), saved: state.saved.slice(0, -1), future};
  },
  redo: (state) => {
    const [next, ...future] = state.future;
    if (next === undefined) return state;
    return {...shown(state, next), past: [...state.past, state.document], future};
  },
};

export function editorReducer(state: EditorState, action: EditorAction): EditorState {
  const handler = handlers[action.type] as Handler<EditorAction>;
  return handler(state, action);
}
