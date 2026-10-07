import type {Catalog, GraphDocument} from '../../../api/index.ts';
import {arrangedLayout} from './arrange.ts';
import {dagreLayout, loadDagre} from './dagre-graph.ts';
import {elkGraph, elkPositions} from './elk-graph.ts';
import type {CardGeometry} from './elk-graph.ts';
import {loadElk} from './elk-loader.ts';
import {elkTreeGraph} from './elk-tree.ts';

/**
 * Port-aware ELK (to fit the screen, compactly, or by flow); ELK's tree from left to right
 * or from top to bottom; or dagre's tree in the same two directions.
 */
export type LayoutChoice =
  'fit' | 'compact' | 'flow' | 'elk-right' | 'elk-down' | 'dagre-right' | 'dagre-down';
type Geometry = (nodeId: string) => CardGeometry | undefined;
type Layout = Record<string, [number, number]>;

async function laidOut(
  document: GraphDocument,
  catalog: Catalog,
  geometry: Geometry,
  choice: LayoutChoice,
  aspectRatio: number,
): Promise<Layout> {
  if (choice === 'dagre-right' || choice === 'dagre-down') {
    const rankdir = choice === 'dagre-right' ? 'LR' : 'TB';
    return dagreLayout(await loadDagre(), document, catalog, geometry, rankdir);
  }
  const elk = await loadElk();
  if (choice === 'elk-right' || choice === 'elk-down') {
    const direction = choice === 'elk-right' ? 'RIGHT' : 'DOWN';
    return elkPositions(await elk.layout(elkTreeGraph(document, catalog, geometry, direction)));
  }
  return elkPositions(await elk.layout(elkGraph(document, catalog, geometry, choice, aspectRatio)));
}

/** The chosen layout, or the editor's own left-to-right layout when it cannot be loaded. */
export async function arrangement(
  document: GraphDocument,
  catalog: Catalog,
  geometry: Geometry,
  choice: LayoutChoice,
  aspectRatio: number,
): Promise<Layout> {
  try {
    return await laidOut(document, catalog, geometry, choice, aspectRatio);
  } catch {
    const heights = new Map(
      document.nodes.map((node) => [node.id, geometry(node.id)?.height ?? 150]),
    );
    return arrangedLayout(document, catalog, heights);
  }
}
