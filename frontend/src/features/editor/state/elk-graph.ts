import type {ElkExtendedEdge, ElkNode, LayoutOptions} from 'elkjs/lib/elk-api.js';
import type {Catalog, GraphDocument, GraphNode} from '../../../api/index.ts';
import {DEFAULT_SIZE, elkPorts, portId} from './elk-ports.ts';
import type {CardGeometry} from './elk-ports.ts';
import {nodePorts, splitRef} from './ports.ts';

/** By flow in one row of layers; wrapped to fit the screen; or wrapped and tight. */
export type ArrangeMode = 'flow' | 'fit' | 'compact';
export type {CardGeometry} from './elk-ports.ts';
type Geometry = (nodeId: string) => CardGeometry | undefined;
type Layout = Record<string, [number, number]>;

const MARGIN = 40;

const COMMON: LayoutOptions = {
  'elk.algorithm': 'layered',
  'elk.direction': 'RIGHT',
  'elk.edgeRouting': 'ORTHOGONAL',
  'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
  'elk.layered.nodePlacement.strategy': 'NETWORK_SIMPLEX',
  'elk.layered.considerModelOrder.strategy': 'NODES_AND_EDGES',
  /** Loops are broken where they lead back, found depth first from the Triggers. */
  'elk.layered.cycleBreaking.strategy': 'DEPTH_FIRST',
};
/** Room between cards for a route to pass, clear of both. */
const ROOMY: LayoutOptions = {
  'elk.spacing.nodeNode': '56',
  'elk.layered.spacing.nodeNodeBetweenLayers': '90',
};
const fit = (ratio: string): LayoutOptions => ({
  ...COMMON,
  ...ROOMY,
  'elk.layered.wrapping.strategy': 'MULTI_EDGE',
  'elk.aspectRatio': ratio,
});
const MODES: Readonly<Record<ArrangeMode, (ratio: string) => LayoutOptions>> = {
  flow: () => ({...COMMON, ...ROOMY, 'elk.layered.wrapping.strategy': 'OFF'}),
  fit,
  compact: (ratio) => ({
    ...COMMON,
    'elk.spacing.nodeNode': '24',
    'elk.layered.spacing.nodeNodeBetweenLayers': '48',
    'elk.layered.spacing.edgeNodeBetweenLayers': '16',
    'elk.layered.wrapping.strategy': 'MULTI_EDGE',
    'elk.layered.wrapping.cutting.strategy': 'MSD',
    'elk.layered.compaction.postCompaction.strategy': 'EDGE_LENGTH',
    'elk.aspectRatio': ratio,
  }),
};

/** The layered options of a mode; wrapping modes aim at the canvas's width ÷ height. */
export function arrangeOptions(mode: ArrangeMode, aspectRatio: number): LayoutOptions {
  const ratio = Number.isFinite(aspectRatio) && aspectRatio > 0 ? aspectRatio : 1.6;
  return MODES[mode](ratio.toFixed(2));
}

function card(
  document: GraphDocument,
  node: GraphNode,
  catalog: Catalog,
  geometry: CardGeometry | undefined,
): ElkNode {
  const trigger = node.component.split('@')[0] === 'trigger';
  return {
    id: node.id,
    width: geometry?.width ?? DEFAULT_SIZE.width,
    height: geometry?.height ?? DEFAULT_SIZE.height,
    ports: elkPorts(document, node, catalog, geometry),
    layoutOptions: {
      'elk.portConstraints': 'FIXED_POS',
      ...(trigger ? {'elk.layered.layering.layerConstraint': 'FIRST'} : {}),
    },
  };
}

/** One edge per connection between ports that exist. */
function edges(document: GraphDocument, catalog: Catalog): ElkExtendedEdge[] {
  const nodes = new Map(document.nodes.map((node) => [node.id, nodePorts(node, catalog)]));
  return document.connections.flatMap((connection) => {
    const [source, output] = splitRef(connection.from);
    const [target, input] = splitRef(connection.to);
    const exists =
      nodes.get(source)?.outputs.includes(output) === true &&
      nodes.get(target)?.inputs.includes(input) === true;
    if (!exists) return [];
    const id = `${connection.from}->${connection.to}`;
    return [
      {id, sources: [portId(source, 'output', output)], targets: [portId(target, 'input', input)]},
    ];
  });
}

/** The graph for ELK's layered algorithm: cards with their ports, and their connections. */
export function elkGraph(
  document: GraphDocument,
  catalog: Catalog,
  geometry: Geometry,
  mode: ArrangeMode,
  aspectRatio: number,
): ElkNode {
  return {
    id: 'graph',
    layoutOptions: arrangeOptions(mode, aspectRatio),
    children: document.nodes.map((node) => card(document, node, catalog, geometry(node.id))),
    edges: edges(document, catalog),
  };
}

/** The cards' positions from ELK's result, moved to start at the canvas margin. */
export function elkPositions(result: ElkNode): Layout {
  const placed = (result.children ?? []).flatMap((child) =>
    child.x === undefined || child.y === undefined ? [] : [[child.id, child.x, child.y] as const],
  );
  return atMargin(placed);
}

/** Top left corners moved so that the leftmost and topmost start at the canvas margin. */
export function atMargin(placed: readonly (readonly [string, number, number])[]): Layout {
  const left = Math.min(...placed.map(([, x]) => x));
  const top = Math.min(...placed.map(([, , y]) => y));
  return Object.fromEntries(
    placed.map(([id, x, y]) => [id, [Math.round(x - left + MARGIN), Math.round(y - top + MARGIN)]]),
  );
}
