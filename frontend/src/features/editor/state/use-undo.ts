import {useEffect, useRef, useState} from 'react';
import type {Dispatch} from 'react';
import type {OperatorClient} from '../../../api/index.ts';
import {describeChange} from '../../../ui/index.ts';
import type {EditorAction, EditorState} from './editor-state.ts';
import type {EditorSource} from './load.ts';

/** A short message in the status bar, with Undo when what it reports can be undone. */
interface Notice {
  readonly text: string;
  readonly undo: boolean;
}
export interface UndoModel {
  readonly canUndo: boolean;
  readonly canRedo: boolean;
  readonly undo: () => void;
  readonly redo: () => void;
  readonly notice: Notice | null;
  readonly notify: (text: string, undo?: boolean) => void;
}

const SHOWN_MS = 5000;
/** How many of the branch's earlier changes undo reaches. */
const SAVED = 100;

/** The branch's changes before the one opened, oldest first, for undo after a reload. */
function useSavedChanges(
  client: OperatorClient,
  source: EditorSource,
  dispatch: Dispatch<EditorAction>,
): void {
  useEffect(() => {
    const opened = source.stored?.change;
    if (opened === undefined) return;
    const controller = new AbortController();
    const {graphId, branch} = source.target;
    client
      .changes(graphId, {branch, limit: SAVED}, controller.signal)
      .then((changes) => {
        const earlier = changes.map((item) => item.change).filter((change) => change < opened);
        dispatch({type: 'seed', changes: earlier.toReversed()});
      })
      .catch(() => undefined);
    return () => {
      controller.abort();
    };
  }, [client, source, dispatch]);
}

function useNotice(): {readonly notice: Notice | null; readonly notify: UndoModel['notify']} {
  const [notice, setNotice] = useState<Notice | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(
    () => () => {
      if (timer.current !== null) clearTimeout(timer.current);
    },
    [],
  );
  const notify = (text: string, undo = false): void => {
    if (timer.current !== null) clearTimeout(timer.current);
    setNotice({text, undo});
    timer.current = setTimeout(() => {
      setNotice(null);
    }, SHOWN_MS);
  };
  return {notice, notify};
}

type Told = (before: EditorState['document'], after: EditorState['document']) => string;

/** Undo one step: this session's edit, or the saved change read first. */
function undoing(
  client: OperatorClient,
  source: EditorSource,
  state: EditorState,
  dispatch: Dispatch<EditorAction>,
  tell: (text: string) => void,
  told: Told,
): () => void {
  const undoSaved = (change: number): void => {
    client
      .change(source.target.graphId, change)
      .then((record) => {
        dispatch({type: 'undo-saved', change, document: record.document});
        tell(`Undone: ${told(record.document, state.document)}`);
      })
      .catch(() => {
        tell('Could not read the earlier change to undo it');
      });
  };
  return () => {
    const previous = state.past.at(-1);
    const change = state.saved.at(-1);
    if (previous !== undefined) {
      dispatch({type: 'undo'});
      tell(`Undone: ${told(previous, state.document)}`);
    } else if (change !== undefined) undoSaved(change);
  };
}

/**
 * Undo and Redo along the branch's history: this session's edits first, then the changes
 * saved before it, read when reached. Each step is saved as a new change.
 */
export function useUndo(
  client: OperatorClient,
  source: EditorSource,
  state: EditorState,
  dispatch: Dispatch<EditorAction>,
): UndoModel {
  useSavedChanges(client, source, dispatch);
  const {notice, notify} = useNotice();
  const told: Told = (before, after) => describeChange(before, after, source.catalog);
  const undo = undoing(client, source, state, dispatch, notify, told);
  const redo = (): void => {
    const next = state.future[0];
    if (next === undefined) return;
    dispatch({type: 'redo'});
    notify(`Redone: ${told(state.document, next)}`);
  };
  const canUndo = state.past.length > 0 || state.saved.length > 0;
  return {canUndo, canRedo: state.future.length > 0, undo, redo, notice, notify};
}
