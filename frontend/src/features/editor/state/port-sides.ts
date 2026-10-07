import type {Catalog, GraphDocument, GraphNode} from '../../../api/index.ts';
import {nodePorts} from './ports.ts';

export type PortSide = 'left' | 'right' | 'top' | 'bottom';
export type PortKind = 'input' | 'output';
/** Left and right, the default; top and bottom; or a side chosen per port. */
export type SidesMode = 'sides' | 'vertical' | 'custom';
export type Sides = Readonly<Record<string, PortSide>>;

export const PORT_SIDES: readonly PortSide[] = ['left', 'right', 'top', 'bottom'];
const DEFAULT_SIDES: Readonly<Record<PortKind, PortSide>> = {input: 'left', output: 'right'};
const VERTICAL_SIDES: Readonly<Record<PortKind, PortSide>> = {input: 'top', output: 'bottom'};

/** Where a port sits on its card: as `port_sides` says, or inputs left and outputs right. */
export function portSide(
  document: GraphDocument,
  nodeId: string,
  port: string,
  kind: PortKind,
): PortSide {
  return document.port_sides?.[nodeId]?.[port] ?? DEFAULT_SIDES[kind];
}

type Entry = [string, PortSide];

/** Every port of the node on its current side; an output wins a name shared with an input. */
export function nodeSides(document: GraphDocument, node: GraphNode, catalog: Catalog): Sides {
  const {inputs, outputs} = nodePorts(node, catalog);
  const entry =
    (kind: PortKind) =>
    (port: string): Entry => [port, portSide(document, node.id, port, kind)];
  return Object.fromEntries([...inputs.map(entry('input')), ...outputs.map(entry('output'))]);
}

/** No side listed is the default; all inputs on top and all outputs below is top and bottom. */
export function sidesMode(document: GraphDocument, node: GraphNode, catalog: Catalog): SidesMode {
  const listed = document.port_sides?.[node.id] ?? {};
  const {inputs, outputs} = nodePorts(node, catalog);
  if (![...inputs, ...outputs].some((port) => port in listed)) return 'sides';
  const vertical =
    inputs.every((port) => listed[port] === 'top') &&
    outputs.every((port) => listed[port] === 'bottom');
  return vertical ? 'vertical' : 'custom';
}

/** Inputs on top and outputs below. */
export function verticalSides(node: GraphNode, catalog: Catalog): Sides {
  const {inputs, outputs} = nodePorts(node, catalog);
  const entry =
    (kind: PortKind) =>
    (port: string): Entry => [port, VERTICAL_SIDES[kind]];
  return Object.fromEntries([...inputs.map(entry('input')), ...outputs.map(entry('output'))]);
}

/** Only the sides that differ from the default, for the node's existing ports. */
export function changedSides(node: GraphNode, catalog: Catalog, sides: Sides): Sides {
  const {inputs, outputs} = nodePorts(node, catalog);
  const changed = (port: string, kind: PortKind): Entry[] => {
    const side = sides[port];
    return side === undefined || side === DEFAULT_SIDES[kind] ? [] : [[port, side]];
  };
  return Object.fromEntries([
    ...inputs.flatMap((port) => changed(port, 'input')),
    ...outputs.flatMap((port) => changed(port, 'output')),
  ]);
}

/** The document with the node's sides replaced; none or an empty set removes its entry. */
export function withSides(
  document: GraphDocument,
  nodeId: string,
  sides: Sides | null,
): GraphDocument {
  const others: [string, Sides][] = Object.entries(document.port_sides ?? {}).filter(
    ([key]) => key !== nodeId,
  );
  const own: [string, Sides][] =
    sides === null || Object.keys(sides).length === 0 ? [] : [[nodeId, sides]];
  const entries = [...others, ...own];
  if (entries.length > 0) return {...document, port_sides: Object.fromEntries(entries)};
  const rest = {...document};
  delete rest.port_sides;
  return rest;
}

/** The node's listed sides for ports it still has, once its ports changed. */
export function keptSides(
  document: GraphDocument,
  nodeId: string,
  catalog: Catalog,
): GraphDocument {
  const node = document.nodes.find((item) => item.id === nodeId);
  const listed = document.port_sides?.[nodeId];
  if (node === undefined || listed === undefined) return document;
  const {inputs, outputs} = nodePorts(node, catalog);
  const ports = new Set([...inputs, ...outputs]);
  const kept = Object.entries(listed).filter(([port]) => ports.has(port));
  return withSides(document, nodeId, Object.fromEntries(kept));
}
