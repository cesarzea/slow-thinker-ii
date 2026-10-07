import {createContext, useContext} from 'react';

/** What an editable canvas can do to a card from the card itself or its menu. */
export interface NodeActions {
  readonly edit: (nodeId: string) => void;
  readonly remove: (nodeId: string) => void;
  readonly removeComponent: (nodeId: string) => void;
}

/** Provided only by an editable canvas. */
export const NodeActionsContext = createContext<NodeActions | null>(null);

export function useNodeActions(): NodeActions | null {
  return useContext(NodeActionsContext);
}
