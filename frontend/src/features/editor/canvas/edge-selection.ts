import {createContext, useContext, useEffect, useState} from 'react';
import {inDialog, typing} from '../state/keys.ts';
import type {RouteEdgeType} from './types.ts';

type Remove = (edgeId: string) => void;
type Disconnect = ((from: string, to: string) => void) | undefined;

/** Removes a connection by its edge; only an editable canvas provides it. */
export const EdgeRemoval = createContext<Remove | null>(null);

export function useEdgeRemoval(): Remove | null {
  return useContext(EdgeRemoval);
}

export interface EdgeSelection {
  readonly selected: string | null;
  readonly select: (edgeId: string | null) => void;
  readonly remove: Remove;
}

/** Keys act on the selected connection from the canvas or the page, never from a field. */
export function fromCanvas(event: KeyboardEvent): boolean {
  const {target} = event;
  if (typing(target) || inDialog(target)) return false;
  return (
    target === document.body ||
    (target instanceof Element && target.closest('.graph-canvas') !== null)
  );
}

function useSelectionKeys(selected: string | null, remove: Remove, clear: () => void): void {
  useEffect(() => {
    if (selected === null) return;
    const keyDown = (event: KeyboardEvent): void => {
      if (!fromCanvas(event)) return;
      if (event.key === 'Escape') clear();
      if (event.key !== 'Delete' && event.key !== 'Backspace') return;
      event.preventDefault();
      remove(selected);
    };
    document.addEventListener('keydown', keyDown);
    return () => {
      document.removeEventListener('keydown', keyDown);
    };
  }, [selected, remove, clear]);
}

/**
 * The selected connection of an editable canvas: chosen with a click, removed with its ×
 * button, Delete or Backspace, and cleared with Escape. A removed connection is no longer
 * selected.
 */
export function useEdgeSelection(
  edges: readonly RouteEdgeType[],
  onDisconnect: Disconnect,
): EdgeSelection {
  const [chosen, setChosen] = useState<string | null>(null);
  const selected = edges.some((edge) => edge.id === chosen) ? chosen : null;
  const clear = (): void => {
    setChosen(null);
  };
  const remove = (edgeId: string): void => {
    const data = edges.find((edge) => edge.id === edgeId)?.data;
    if (data !== undefined) onDisconnect?.(data.from, data.to);
    clear();
  };
  useSelectionKeys(selected, remove, clear);
  return {selected, select: setChosen, remove};
}
