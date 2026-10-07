import {useCallback, useMemo, useState} from 'react';
import {applyNodeChanges} from '@xyflow/react';
import type {NodeChange} from '@xyflow/react';
import type {CardNode} from './types.ts';

type Retained = ReadonlyMap<string, CardNode>;
export interface FlowCallbacks {
  readonly onSelect?: ((nodeId: string | null) => void) | undefined;
  readonly onMove?: ((nodeId: string, position: [number, number]) => void) | undefined;
}

function merge(node: CardNode, kept: CardNode | undefined): CardNode {
  if (kept === undefined) return node;
  const measured = kept.measured === undefined ? {} : {measured: kept.measured};
  const dragging = kept.dragging === true ? {position: kept.position, dragging: true} : {};
  return {...node, ...measured, ...dragging};
}

/** Finished moves: the end of a drag, or a move with the arrow keys. */
function reportMoves(
  changes: readonly NodeChange<CardNode>[],
  onMove: FlowCallbacks['onMove'],
): void {
  for (const change of changes)
    if (change.type === 'position' && change.dragging !== true && change.position !== undefined)
      onMove?.(change.id, [change.position.x, change.position.y]);
}

/** Selections made on the canvas, with the mouse or with Enter and Escape. */
function reportSelection(
  changes: readonly NodeChange<CardNode>[],
  onSelect: FlowCallbacks['onSelect'],
): void {
  const selections = changes.filter((change) => change.type === 'select');
  if (selections.length > 0)
    onSelect?.(selections.findLast((change) => change.selected)?.id ?? null);
}

/**
 * Nodes come from the document; React Flow's measurements and in-progress drags are kept
 * locally so that controlled nodes stay measured and follow the pointer.
 */
export function useFlowNodes(
  nodes: CardNode[],
  callbacks: FlowCallbacks,
): {nodes: CardNode[]; onNodesChange: (changes: NodeChange<CardNode>[]) => void} {
  const [retained, setRetained] = useState<Retained>(new Map());
  const merged = useMemo(
    () => nodes.map((node) => merge(node, retained.get(node.id))),
    [nodes, retained],
  );
  const {onSelect, onMove} = callbacks;
  const onNodesChange = useCallback(
    (changes: NodeChange<CardNode>[]) => {
      reportMoves(changes, onMove);
      reportSelection(changes, onSelect);
      const kept = changes.filter(
        (change) => change.type === 'dimensions' || change.type === 'position',
      );
      if (kept.length === 0) return;
      setRetained((previous) => {
        const current = nodes.map((node) => merge(node, previous.get(node.id)));
        return new Map(applyNodeChanges(kept, current).map((node) => [node.id, node]));
      });
    },
    [nodes, onSelect, onMove],
  );
  return {nodes: merged, onNodesChange};
}
