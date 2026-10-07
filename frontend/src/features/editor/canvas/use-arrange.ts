import {useState} from 'react';
import {useReactFlow, useStoreApi} from '@xyflow/react';
import type {Catalog, GraphDocument} from '../../../api/index.ts';
import type {CardGeometry} from '../state/elk-graph.ts';
import {arrangement} from '../state/layouts.ts';
import type {LayoutChoice} from '../state/layouts.ts';
import {FIT_VIEW} from './canvas-interaction.tsx';
import type {CardNode, RouteEdgeType} from './types.ts';

type Flow = ReturnType<typeof useReactFlow<CardNode, RouteEdgeType>>;
type Geometry = (id: string) => CardGeometry | undefined;
/** The cards' new positions by node. */
export type Placement = Record<string, [number, number]>;
type Handles = readonly {id?: string | null; x: number; y: number; width: number; height: number}[];

function centres(handles: Handles | null | undefined): Map<string, {x: number; y: number}> {
  return new Map(
    (handles ?? []).flatMap((handle) =>
      typeof handle.id === 'string'
        ? [[handle.id, {x: handle.x + handle.width / 2, y: handle.y + handle.height / 2}] as const]
        : [],
    ),
  );
}

/** Each card's measured size and the centres of its handles, as React Flow measured them. */
function geometryOf(flow: Flow): Geometry {
  return (id) => {
    const node = flow.getInternalNode(id);
    const {width, height} = node?.measured ?? {};
    if (node === undefined || width === undefined || height === undefined) return undefined;
    const bounds = node.internals.handleBounds;
    return {width, height, inputs: centres(bounds?.target), outputs: centres(bounds?.source)};
  };
}

/**
 * Arrange the graph with the chosen layout for the canvas's current shape, hand the cards'
 * new positions to `apply`, then frame it; ports keep their sides.
 */
export function useArrange(
  document: GraphDocument,
  catalog: Catalog,
  apply: (placed: Placement) => void,
): {readonly busy: boolean; readonly arrange: (mode: LayoutChoice) => Promise<void>} {
  const flow = useReactFlow<CardNode, RouteEdgeType>();
  const store = useStoreApi<CardNode, RouteEdgeType>();
  const [busy, setBusy] = useState(false);
  const arrange = async (mode: LayoutChoice): Promise<void> => {
    setBusy(true);
    const {width, height} = store.getState();
    apply(await arrangement(document, catalog, geometryOf(flow), mode, width / height));
    setBusy(false);
    void flow.fitView(FIT_VIEW);
  };
  return {busy, arrange};
}
