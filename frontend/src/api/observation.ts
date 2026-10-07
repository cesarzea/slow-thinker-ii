import type {Catalog} from './schemas/catalog.ts';
import type {GraphDocument, GraphNode} from './schemas/graph.ts';
import type {RunEvent, RunEventKind} from './schemas/events.ts';

/**
 * An observation point: a place in the graph where a run's events are recorded. The run
 * itself (`run`), one facet of a node (`node:<id>/<facet>`) or a connection
 * (`connection:<from>-><to>`, with `node.port` references). A node's group of facets is
 * `node:<id>`.
 */
export type PointId = 'run' | `node:${string}` | `connection:${string}`;

/**
 * What a node records, from the recording contract alone: its activations, the calls to its
 * component, its LLM calls, its reports, the calls to its embedded output component and
 * memory, and the results of an Output node.
 */
export type NodeFacet = 'activity' | 'calls' | 'llm' | 'reports' | 'output' | 'memory' | 'results';

export const RUN_POINT: PointId = 'run';
export const nodePoint = (nodeId: string, facet: NodeFacet): PointId => `node:${nodeId}/${facet}`;
export const connectionPoint = (from: string, to: string): PointId => `connection:${from}->${to}`;

/** Whether a saved value names a point, so that it can be kept as one. */
export const isPoint = (value: string): value is PointId =>
  value === RUN_POINT || value.startsWith('node:') || value.startsWith('connection:');

const kind = (node: GraphNode): string => node.component.split('@')[0] ?? '';

/** The facets of a node's embedded components, in the order of their positions. */
function embeddedFacets(node: GraphNode): NodeFacet[] {
  const positions = new Set((node.embedded ?? []).map((item) => item.position));
  return (['output', 'memory'] as const).filter((position) => positions.has(position));
}

/** Whether the node's component may call an LLM: it declares a service use. */
function callsLlm(node: GraphNode, catalog: Catalog): boolean {
  const declaration = catalog.components.find(
    (item) => `${item.type}@${item.version}` === node.component,
  );
  return declaration === undefined || declaration.uses.length > 0;
}

/** The facets a node can record, in the order they are listed. */
export function nodeFacets(node: GraphNode, catalog: Catalog): NodeFacet[] {
  if (kind(node) === 'trigger') return ['activity'];
  if (kind(node) === 'output') return ['activity', 'results'];
  const llm: NodeFacet[] = callsLlm(node, catalog) ? ['llm'] : [];
  return ['activity', 'calls', ...llm, 'reports', ...embeddedFacets(node)];
}

/** Every point of a document: the run, each node's facets, then its connections. */
export function documentPoints(document: GraphDocument, catalog: Catalog): PointId[] {
  return [
    RUN_POINT,
    ...document.nodes.flatMap((node) =>
      nodeFacets(node, catalog).map((facet) => nodePoint(node.id, facet)),
    ),
    ...document.connections.map((item) => connectionPoint(item.from, item.to)),
  ];
}

/** The facet of each event kind that is not simply the node's activity. */
const FACETS: Partial<Record<RunEventKind, NodeFacet>> = {
  'llm.called': 'llm',
  report: 'reports',
  'run.result': 'results',
};

function facetOf(event: RunEvent): NodeFacet {
  if (event.kind === 'component.called')
    return event.data.position === 'node' ? 'calls' : event.data.position;
  return FACETS[event.kind] ?? 'activity';
}

/** Where an event was recorded: a message on its connection, a node's facet, or the run. */
export function eventPoint(event: RunEvent): PointId {
  if (event.kind === 'message.sent') {
    const {from, to} = event.data;
    return connectionPoint(`${from.node_id}.${from.port}`, `${to.node_id}.${to.port}`);
  }
  return event.node_id === null ? RUN_POINT : nodePoint(event.node_id, facetOf(event));
}
