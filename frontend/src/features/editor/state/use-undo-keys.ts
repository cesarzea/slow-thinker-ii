import {useEffect, useRef} from 'react';
import {inDialog, typing} from './keys.ts';
import type {UndoModel} from './use-undo.ts';

function undoAction(event: KeyboardEvent): 'undo' | 'redo' | null {
  if (!(event.ctrlKey || event.metaKey)) return null;
  const key = event.key.toLowerCase();
  if (key === 'y') return 'redo';
  if (key !== 'z') return null;
  return event.shiftKey ? 'redo' : 'undo';
}

/** Ctrl or ⌘ with Z undoes, with Shift and Z or with Y redoes; never in fields or dialogs. */
export function useUndoKeys(history: UndoModel): void {
  const latest = useRef(history);
  useEffect(() => {
    latest.current = history;
  });
  useEffect(() => {
    const keyDown = (event: KeyboardEvent): void => {
      const action = undoAction(event);
      if (action === null || typing(event.target) || inDialog(event.target)) return;
      event.preventDefault();
      latest.current[action]();
    };
    document.addEventListener('keydown', keyDown);
    return () => {
      document.removeEventListener('keydown', keyDown);
    };
  }, []);
}
