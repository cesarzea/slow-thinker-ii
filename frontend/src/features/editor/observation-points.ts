import {RUN_POINT, connectionPoint, nodeFacets, nodePoint} from '../../api/index.ts';
import type {Catalog, GraphDocument, GraphNode, NodeFacet, PointId} from '../../api/index.ts';
import type {KindTile} from '../../ui/index.ts';
import {flowOrder} from './state/arrange.ts';
import {declarationFor, embeddedAt, splitRef} from './state/ports.ts';

export interface Point {
  /** The point, or for a node the key of its group of facets. */
  readonly id: PointId;
  readonly title: string;
  readonly detail: string;
  /** A component's tile, or the run's or a connection's own icon; none for a facet. */
  readonly icon: Parameters<typeof KindTile>[0]['icon'] | 'run' | 'connection' | null;
  /** The points it stands for: itself, or a node's facets. */
  readonly members: readonly PointId[];
  readonly facets: readonly Point[];
}

/** A node's group of facets, the key that focusing a whole node uses. */
const nodeGroup = (nodeId: string): PointId => `node:${nodeId}`;

const FACETS: Readonly<Record<NodeFacet, string>> = {
  activity: 'Activity',
  calls: 'Component calls',
  llm: 'LLM calls',
  reports: 'Reports',
  output: 'Output component',
  memory: 'Memory',
  results: 'Results',
};

/** A facet's name: an embedded component's facet takes that component's label. */
function facetLabel(node: GraphNode, facet: NodeFacet, catalog: Catalog): string {
  if (facet !== 'output' && facet !== 'memory') return FACETS[facet];
  const embedded = embeddedAt(node, facet);
  return declarationFor(catalog, embedded?.component)?.label ?? FACETS[facet];
}

function nodePointOf(node: GraphNode, catalog: Catalog): Point {
  const declaration = declarationFor(catalog, node.component);
  const facets = nodeFacets(node, catalog).map((facet): Point => {
    const id = nodePoint(node.id, facet);
    const title = facetLabel(node, facet, catalog);
    return {id, title, detail: node.name, icon: null, members: [id], facets: []};
  });
  return {
    id: nodeGroup(node.id),
    title: node.name,
    detail: declaration?.label ?? node.component,
    icon: declaration?.icon ?? 'component',
    members: facets.map((facet) => facet.id),
    facets,
  };
}

function nodeName(document: GraphDocument, ref: string): [string, string] {
  const [nodeId, port] = splitRef(ref);
  return [document.nodes.find((node) => node.id === nodeId)?.name ?? nodeId, port];
}

const RUN: Point = {
  id: RUN_POINT,
  title: 'Run',
  detail: 'Start, end and totals',
  icon: 'run',
  members: [RUN_POINT],
  facets: [],
};

function connectionPointOf(
  document: GraphDocument,
  item: GraphDocument['connections'][number],
): Point {
  const [from, out] = nodeName(document, item.from);
  const [to, into] = nodeName(document, item.to);
  const id = connectionPoint(item.from, item.to);
  return {
    id,
    title: `${from} → ${to}`,
    detail: `${out} → ${into}`,
    icon: 'connection',
    members: [id],
    facets: [],
  };
}

/** The run, the nodes in flow order with their facets, and the connections of a document. */
export function points(
  document: GraphDocument,
  catalog: Catalog,
): {
  readonly run: Point;
  readonly nodes: Point[];
  readonly connections: Point[];
} {
  const nodes = flowOrder(document, catalog).flatMap((id): Point[] => {
    const node = document.nodes.find((item) => item.id === id);
    return node === undefined ? [] : [nodePointOf(node, catalog)];
  });
  const connections = document.connections.map((item) => connectionPointOf(document, item));
  return {run: RUN, nodes, connections};
}

/** Every point's readable name, a facet's with its node's, for the run panel's messages. */
export function pointLabels(
  document: GraphDocument,
  catalog: Catalog,
): Partial<Record<PointId, string>> {
  const all = points(document, catalog);
  const facets = all.nodes.flatMap((node) =>
    node.facets.map((facet) => [facet.id, `${node.title} · ${facet.title}`] as const),
  );
  const named = [all.run, ...all.nodes, ...all.connections].map(
    (point) => [point.id, point.title] as const,
  );
  return Object.fromEntries([...named, ...facets]);
}

/** The points a focus stands for: a node's group is each of its facets. */
export function focusedPoints(
  focus: PointId,
  document: GraphDocument,
  catalog: Catalog,
): PointId[] {
  const node = points(document, catalog).nodes.find((item) => item.id === focus);
  return node === undefined ? [focus] : [...node.members];
}
