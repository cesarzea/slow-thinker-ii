import {useEffect, useRef} from 'react';
import {removeNode} from '../state/node-removal.ts';
import type {EditorModel} from '../state/use-editor.ts';
import {fromCanvas} from './edge-selection.ts';

/**
 * Delete or Backspace delete the selected node with its connections, from the canvas or the
 * page, never while typing in a field or with a dialog open; Undo brings it back.
 */
export function useNodeDeleteKeys(editor: EditorModel): void {
  const latest = useRef(editor);
  useEffect(() => {
    latest.current = editor;
  });
  useEffect(() => {
    const keyDown = (event: KeyboardEvent): void => {
      if (event.key !== 'Delete' && event.key !== 'Backspace') return;
      const selected = latest.current.state.selected;
      if (selected === null || event.defaultPrevented || !fromCanvas(event)) return;
      event.preventDefault();
      removeNode(latest.current, selected);
    };
    document.addEventListener('keydown', keyDown);
    return () => {
      document.removeEventListener('keydown', keyDown);
    };
  }, []);
}
