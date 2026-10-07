import type {
  Catalog,
  ComponentDeclaration,
  Connection,
  GraphDocument,
  GraphNode,
  JsonObject,
  Limits,
} from '../../../api/index.ts';
import {withSides} from './port-sides.ts';
import {componentRef, nodePorts, splitRef} from './ports.ts';

function firstFree(base: string, separator: string, taken: (value: string) => boolean): string {
  let suffix = 1;
  let candidate = base;
  while (taken(candidate)) {
    suffix += 1;
    candidate = `${base}${separator}${String(suffix)}`;
  }
  return candidate;
}

export function uniqueNodeId(document: GraphDocument, type: string): string {
  const ids = new Set(document.nodes.map((node) => node.id));
  return firstFree(type.slice(0, 58), '-', (id) => ids.has(id));
}

function uniqueNodeName(document: GraphDocument, label: string): string {
  const names = new Set(document.nodes.map((node) => node.name.toLowerCase()));
  return firstFree(label, ' ', (name) => names.has(name.toLowerCase()));
}

export function addNode(
  document: GraphDocument,
  declaration: ComponentDeclaration,
  position: [number, number],
  id: string = uniqueNodeId(document, declaration.type),
): GraphDocument {
  const node: GraphNode = {
    id,
    name: uniqueNodeName(document, declaration.label),
    component: componentRef(declaration),
    config: structuredClone(declaration.initial_config),
  };
  return {
    ...document,
    nodes: [...document.nodes, node],
    layout: {...document.layout, [id]: position},
  };
}

export function updateNode(
  document: GraphDocument,
  nodeId: string,
  change: (node: GraphNode) => GraphNode,
): GraphDocument {
  return {
    ...document,
    nodes: document.nodes.map((node) => (node.id === nodeId ? change(node) : node)),
  };
}

export function renameNode(document: GraphDocument, nodeId: string, name: string): GraphDocument {
  return updateNode(document, nodeId, (node) => ({...node, name}));
}

export function deleteNode(document: GraphDocument, nodeId: string): GraphDocument {
  const layout = Object.fromEntries(
    Object.entries(document.layout ?? {}).filter(([key]) => key !== nodeId),
  );
  const touches = (connection: Connection): boolean =>
    splitRef(connection.from)[0] === nodeId || splitRef(connection.to)[0] === nodeId;
  return withSides(
    {
      ...document,
      nodes: document.nodes.filter((node) => node.id !== nodeId),
      connections: document.connections.filter((connection) => !touches(connection)),
      layout,
    },
    nodeId,
    null,
  );
}

export function connect(document: GraphDocument, from: string, to: string): GraphDocument {
  const exists = document.connections.some((item) => item.from === from && item.to === to);
  return exists ? document : {...document, connections: [...document.connections, {from, to}]};
}

export function disconnect(document: GraphDocument, from: string, to: string): GraphDocument {
  const connections = document.connections.filter((item) => item.from !== from || item.to !== to);
  return {...document, connections};
}

export function moveNode(
  document: GraphDocument,
  nodeId: string,
  [x, y]: [number, number],
): GraphDocument {
  return {...document, layout: {...document.layout, [nodeId]: [Math.round(x), Math.round(y)]}};
}

export function setNodeConfig(
  document: GraphDocument,
  nodeId: string,
  config: JsonObject,
): GraphDocument {
  return updateNode(document, nodeId, (node) => ({...node, config}));
}

export function setEmbeddedConfig(
  document: GraphDocument,
  nodeId: string,
  config: JsonObject,
  position: 'output' | 'memory' = 'output',
): GraphDocument {
  return updateNode(document, nodeId, (node) => ({
    ...node,
    embedded: (node.embedded ?? []).map((item) =>
      item.position === position ? {...item, config} : item,
    ),
  }));
}

export function setLimits(document: GraphDocument, limits: Limits): GraphDocument {
  return {...document, limits};
}

/** Connections leaving a node from ports it no longer has. */
export function staleConnections(
  document: GraphDocument,
  nodeId: string,
  catalog: Catalog,
): Connection[] {
  const node = document.nodes.find((item) => item.id === nodeId);
  if (node === undefined) return [];
  const outputs = new Set(nodePorts(node, catalog).outputs);
  return document.connections.filter((connection) => {
    const [from, port] = splitRef(connection.from);
    return from === nodeId && !outputs.has(port);
  });
}

export function withoutConnections(
  document: GraphDocument,
  removed: readonly Connection[],
): GraphDocument {
  const connections = document.connections.filter((item) => !removed.includes(item));
  return {...document, connections};
}
