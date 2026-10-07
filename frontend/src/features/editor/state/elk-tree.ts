import type {ElkNode} from 'elkjs/lib/elk-api.js';
import type {Catalog, GraphDocument} from '../../../api/index.ts';
import {DEFAULT_SIZE} from './elk-ports.ts';
import type {CardGeometry} from './elk-ports.ts';
import {linkedNodes} from './ports.ts';

export type TreeDirection = 'RIGHT' | 'DOWN';

/**
 * The graph as React Flow's elkjs example gives it to ELK: layered, in one direction, with
 * the measured cards connected node to node, without ports.
 */
export function elkTreeGraph(
  document: GraphDocument,
  catalog: Catalog,
  geometry: (nodeId: string) => CardGeometry | undefined,
  direction: TreeDirection,
): ElkNode {
  return {
    id: 'graph',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': direction,
      'elk.layered.spacing.nodeNodeBetweenLayers': '100',
      'elk.spacing.nodeNode': '80',
    },
    children: document.nodes.map((node) => {
      const {width, height} = geometry(node.id) ?? DEFAULT_SIZE;
      return {id: node.id, width, height};
    }),
    edges: linkedNodes(document, catalog).map(([source, target]) => ({
      id: `${source}->${target}`,
      sources: [source],
      targets: [target],
    })),
  };
}
