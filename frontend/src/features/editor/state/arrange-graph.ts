import type {Catalog, GraphDocument} from '../../../api/index.ts';
import {nodePorts, splitRef} from './ports.ts';

/** A connection between two different nodes, with its output's place among the source's outputs. */
export interface Link {
  readonly from: string;
  readonly to: string;
  /** Between 0 and 1: earlier outputs come first; unknown outputs come last. */
  readonly rank: number;
}

/** The connections between existing nodes, without connections from a node to itself. */
export function graphLinks(document: GraphDocument, catalog: Catalog): Link[] {
  const nodes = new Map(document.nodes.map((node) => [node.id, node]));
  return document.connections.flatMap((connection) => {
    const [from, port] = splitRef(connection.from);
    const [to] = splitRef(connection.to);
    const source = nodes.get(from);
    if (source === undefined || !nodes.has(to) || from === to) return [];
    const outputs = nodePorts(source, catalog).outputs;
    const index = outputs.includes(port) ? outputs.indexOf(port) : outputs.length;
    return [{from, to, rank: (index + 1) / (outputs.length + 1)}];
  });
}

/**
 * The links that remain once the links leading back are removed: a depth-first search from
 * the starting nodes, then from any node not reached, drops each link to a node on its path.
 */
export function forwardLinks(
  order: readonly string[],
  starts: readonly string[],
  links: readonly Link[],
): Link[] {
  const place = (id: string): number => order.indexOf(id);
  const open = new Set<string>();
  const done = new Set<string>();
  const back = new Set<Link>();
  const visit = (id: string): void => {
    open.add(id);
    const outgoing = links
      .filter((link) => link.from === id)
      .sort((left, right) => left.rank - right.rank || place(left.to) - place(right.to));
    for (const link of outgoing) {
      if (open.has(link.to)) back.add(link);
      else if (!done.has(link.to)) visit(link.to);
    }
    open.delete(id);
    done.add(id);
  };
  for (const id of [...starts, ...order]) if (!done.has(id)) visit(id);
  return links.filter((link) => !back.has(link));
}

/** Each node's layer: the length of the longest path that reaches it from a source. */
export function longestPathLayers(
  order: readonly string[],
  links: readonly Link[],
): Map<string, number> {
  const layers = new Map<string, number>();
  const layer = (id: string): number => {
    const known = layers.get(id);
    if (known !== undefined) return known;
    layers.set(id, 0);
    const before = links.filter((link) => link.to === id).map((link) => layer(link.from) + 1);
    const value = Math.max(0, ...before);
    layers.set(id, value);
    return value;
  };
  for (const id of order) layer(id);
  return layers;
}

type Neighbours = (id: string) => readonly (readonly [string, number])[];

/** Reorder one layer by the mean place of each node's neighbours; ties keep their order. */
function reorder(
  layer: readonly string[],
  neighbours: Neighbours,
  place: ReadonlyMap<string, number>,
): string[] {
  const key = (id: string, index: number): number => {
    const around = neighbours(id);
    if (around.length === 0) return index;
    const total = around.reduce(
      (sum, [other, offset]) => sum + (place.get(other) ?? 0) + offset,
      0,
    );
    return total / around.length;
  };
  return layer
    .map((id, index) => ({id, key: key(id, index)}))
    .sort((left, right) => left.key - right.key)
    .map((entry) => entry.id);
}

/**
 * Order the nodes of each layer by the barycentre of their neighbours: down by predecessors,
 * up by successors, then down again. A node's targets follow the order of its outputs.
 */
export function orderLayers(
  columns: readonly (readonly string[])[],
  links: readonly Link[],
): string[][] {
  const result = columns.map((column) => [...column]);
  const place = new Map<string, number>();
  const before: Neighbours = (id) =>
    links.filter((link) => link.to === id).map((link) => [link.from, link.rank] as const);
  const after: Neighbours = (id) =>
    links.filter((link) => link.from === id).map((link) => [link.to, 0] as const);
  const sweep = (indices: readonly number[], neighbours: Neighbours): void => {
    for (const index of indices) {
      result.forEach((column) => {
        column.forEach((id, position) => place.set(id, position));
      });
      result[index] = reorder(result[index] ?? [], neighbours, place);
    }
  };
  const indices = result.map((_, index) => index);
  sweep(indices.slice(1), before);
  sweep(indices.slice(0, -1).reverse(), after);
  sweep(indices.slice(1), before);
  return result;
}
