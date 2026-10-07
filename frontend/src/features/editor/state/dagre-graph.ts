import type {Graph, layout} from '@dagrejs/dagre';
import type {Catalog, GraphDocument} from '../../../api/index.ts';
import {DEFAULT_SIZE} from './elk-ports.ts';
import {atMargin} from './elk-graph.ts';
import type {CardGeometry} from './elk-ports.ts';
import {linkedNodes} from './ports.ts';

/** The part of `@dagrejs/dagre` used here, so that it can be loaded lazily. */
export interface Dagre {
  readonly Graph: typeof Graph;
  readonly layout: typeof layout;
}
export type DagreDirection = 'LR' | 'TB';
type Layout = Record<string, [number, number]>;

const NODE_SEPARATION = 40;
const RANK_SEPARATION = 80;

/**
 * The cards' positions as React Flow's dagre example lays them out: a tree from left to
 * right or from top to bottom with the measured card sizes, moved to start at the margin.
 */
export function dagreLayout(
  dagre: Dagre,
  document: GraphDocument,
  catalog: Catalog,
  geometry: (nodeId: string) => CardGeometry | undefined,
  rankdir: DagreDirection,
): Layout {
  const graph = new dagre.Graph();
  graph.setGraph({rankdir, nodesep: NODE_SEPARATION, ranksep: RANK_SEPARATION});
  graph.setDefaultEdgeLabel(() => ({}));
  for (const node of document.nodes) {
    const {width, height} = geometry(node.id) ?? DEFAULT_SIZE;
    graph.setNode(node.id, {width, height});
  }
  for (const [source, target] of linkedNodes(document, catalog)) graph.setEdge(source, target);
  dagre.layout(graph);
  const placed = document.nodes.map((node) => {
    const {x, y, width, height} = graph.node(node.id) as Record<string, number>;
    return [node.id, (x ?? 0) - (width ?? 0) / 2, (y ?? 0) - (height ?? 0) / 2] as const;
  });
  return atMargin(placed);
}

let loading: Promise<Dagre> | null = null;

/** Dagre, loaded on first use as its own chunk. */
export async function loadDagre(): Promise<Dagre> {
  loading ??= import('@dagrejs/dagre');
  try {
    return await loading;
  } catch (error) {
    loading = null;
    throw error;
  }
}
