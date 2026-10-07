import type {Catalog, ComponentDeclaration, Connection, GraphDocument} from '../../../api/index.ts';
import {staleConnections, updateNode, withoutConnections} from './document.ts';
import {keptSides} from './port-sides.ts';
import {componentRef, embeddedOutput, nodePorts, splitRef} from './ports.ts';
import type {EmbeddedPosition} from './ports.ts';

/** Where a component is embedded: as the node's memory, or at its output. */
function positionOf(declaration: ComponentDeclaration): EmbeddedPosition {
  return declaration.placements.includes('memory') ? 'memory' : 'output';
}

/** Components that can be embedded in a node, at the given positions. */
export function embeddable(
  catalog: Catalog,
  positions: readonly EmbeddedPosition[] = ['output', 'memory'],
): ComponentDeclaration[] {
  return catalog.components.filter((component) =>
    positions.some((position) => component.placements.includes(position)),
  );
}

/** The positions of a node that hold no embedded component yet. */
export function freePositions(node: GraphDocument['nodes'][number]): EmbeddedPosition[] {
  const taken = new Set((node.embedded ?? []).map((item) => item.position));
  return (['output', 'memory'] as const).filter((position) => !taken.has(position));
}

/**
 * Embed a component at its position, replacing any there; at the output, connections from
 * ports that disappear are removed.
 */
export function embedComponent(
  document: GraphDocument,
  nodeId: string,
  declaration: ComponentDeclaration,
  catalog: Catalog,
): GraphDocument {
  const position = positionOf(declaration);
  const component = {
    position,
    component: componentRef(declaration),
    config: structuredClone(declaration.initial_config),
  };
  const next = updateNode(document, nodeId, (node) => ({
    ...node,
    embedded: [...(node.embedded ?? []).filter((item) => item.position !== position), component],
  }));
  if (position === 'memory') return next;
  return keptSides(
    withoutConnections(next, staleConnections(next, nodeId, catalog)),
    nodeId,
    catalog,
  );
}

/** Connections that leave the ports provided by the node's embedded output component. */
export function providedConnections(
  document: GraphDocument,
  nodeId: string,
  catalog: Catalog,
): Connection[] {
  const node = document.nodes.find((item) => item.id === nodeId);
  if (node === undefined || embeddedOutput(node) === undefined) return [];
  const outputs = new Set(nodePorts(node, catalog).outputs);
  return document.connections.filter((connection) => {
    const [from, port] = splitRef(connection.from);
    return from === nodeId && outputs.has(port);
  });
}

/**
 * Remove the component embedded at a position; at the output, with the connections leaving
 * the ports it provided.
 */
export function removeEmbedded(
  document: GraphDocument,
  nodeId: string,
  catalog: Catalog,
  position: EmbeddedPosition = 'output',
): GraphDocument {
  const removed = position === 'output' ? providedConnections(document, nodeId, catalog) : [];
  const next = updateNode(document, nodeId, (node) => {
    const kept = (node.embedded ?? []).filter((item) => item.position !== position);
    const plain = {...node, embedded: kept};
    if (kept.length === 0) Reflect.deleteProperty(plain, 'embedded');
    return plain;
  });
  return keptSides(withoutConnections(next, removed), nodeId, catalog);
}
