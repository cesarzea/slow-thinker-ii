import type {Catalog, GraphDocument, GraphNode} from '../api/index.ts';
import {canonicalJson} from './json.ts';
import {componentLabel, nodeEdits} from './node-edits.ts';

type Nodes = ReadonlyMap<string, GraphNode>;

function nodesOf(document: GraphDocument): Nodes {
  return new Map(document.nodes.map((node) => [node.id, node]));
}

/** “Reviewer · revise” for the endpoint “reviewer.revise”. */
function endpoint(nodes: Nodes, end: string): string {
  const cut = end.lastIndexOf('.');
  const id = cut < 0 ? end : end.slice(0, cut);
  const port = cut < 0 ? '' : ` · ${end.slice(cut + 1)}`;
  return `${nodes.get(id)?.name ?? id}${port}`;
}

function nodeChanges(
  before: GraphDocument,
  after: GraphDocument,
  catalog: Catalog | null,
): string[] {
  const old = nodesOf(before);
  const now = nodesOf(after);
  const named = (node: GraphNode): string =>
    `${node.name} (${componentLabel(catalog, node.component)})`;
  return [
    ...before.nodes.filter((node) => !now.has(node.id)).map((node) => `Removed ${named(node)}`),
    ...after.nodes.filter((node) => !old.has(node.id)).map((node) => `Added ${named(node)}`),
    ...after.nodes.flatMap((node) => {
      const was = old.get(node.id);
      return was === undefined ? [] : nodeEdits(catalog, was, node);
    }),
  ];
}

function connectionChanges(before: GraphDocument, after: GraphDocument): string[] {
  const key = (connection: {from: string; to: string}): string =>
    `${connection.from}>${connection.to}`;
  const old = new Set(before.connections.map(key));
  const now = new Set(after.connections.map(key));
  const text = (document: GraphDocument, connection: {from: string; to: string}): string =>
    `${endpoint(nodesOf(document), connection.from)} → ${endpoint(nodesOf(document), connection.to)}`;
  return [
    ...before.connections
      .filter((connection) => !now.has(key(connection)))
      .map((connection) => `Disconnected ${text(before, connection)}`),
    ...after.connections
      .filter((connection) => !old.has(key(connection)))
      .map((connection) => `Connected ${text(after, connection)}`),
  ];
}

function layoutChange(before: GraphDocument, after: GraphDocument): string[] {
  const moved = after.nodes.filter((node) => {
    const was = before.layout?.[node.id];
    const now = after.layout?.[node.id];
    return was !== undefined && canonicalJson(was) !== canonicalJson(now);
  });
  if (moved.length === 0) return [];
  return moved.length === 1 ? [`Moved ${moved[0]?.name ?? ''}`] : ['Arranged the graph'];
}

function graphChanges(before: GraphDocument, after: GraphDocument): string[] {
  return [
    ...(before.name === after.name ? [] : [`Renamed the graph to ${after.name}`]),
    ...(canonicalJson(before.limits) === canonicalJson(after.limits) ? [] : ['Limits edited']),
  ];
}

/** A short description of what a change did, from its document and the one before it. */
export function describeChange(
  before: GraphDocument,
  after: GraphDocument,
  catalog: Catalog | null,
): string {
  const parts = [
    ...graphChanges(before, after),
    ...nodeChanges(before, after, catalog),
    ...connectionChanges(before, after),
    ...layoutChange(before, after),
  ];
  if (parts.length === 0) return 'No visible change';
  const shown = parts.slice(0, 2).join('; ');
  return parts.length > 2 ? `${shown}; and ${String(parts.length - 2)} more` : shown;
}
