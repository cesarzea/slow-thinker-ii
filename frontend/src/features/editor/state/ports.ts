import type {Catalog, ComponentDeclaration, GraphDocument, GraphNode} from '../../../api/index.ts';
import {readPointer} from '../../../ui/index.ts';

export interface NodePorts {
  readonly inputs: readonly string[];
  readonly outputs: readonly string[];
}
export interface PortTarget {
  readonly ref: string;
  readonly label: string;
}

export function componentRef(declaration: ComponentDeclaration): string {
  return `${declaration.type}@${declaration.version}`;
}

export function declarationFor(
  catalog: Catalog,
  ref: string | undefined,
): ComponentDeclaration | undefined {
  return catalog.components.find((component) => componentRef(component) === ref);
}

/** Where a component can be embedded in a node: at its output, or as its memory. */
export type EmbeddedPosition = 'output' | 'memory';

export function embeddedAt(
  node: GraphNode,
  position: EmbeddedPosition,
): {component: string; config: GraphNode['config']} | undefined {
  return node.embedded?.find((item) => item.position === position);
}

export function embeddedOutput(
  node: GraphNode,
): {component: string; config: GraphNode['config']} | undefined {
  return embeddedAt(node, 'output');
}

function declaredOutputs(declaration: ComponentDeclaration, config: GraphNode['config']): string[] {
  const {outputs, outputs_from: pointer} = declaration.ports;
  if (outputs !== undefined) return [...outputs];
  const configured = pointer === undefined ? undefined : readPointer(config, pointer);
  if (!Array.isArray(configured)) return [];
  const names = configured.filter(
    (name): name is string => typeof name === 'string' && name !== '',
  );
  return [...new Set(names)];
}

/** Effective ports: inputs from the host; outputs from the embedded output component if any. */
export function nodePorts(node: GraphNode, catalog: Catalog): NodePorts {
  const host = declarationFor(catalog, node.component);
  const embedded = embeddedOutput(node);
  const inputs = host?.ports.inputs ?? [];
  if (embedded !== undefined) {
    const declaration = declarationFor(catalog, embedded.component);
    const outputs = declaration === undefined ? [] : declaredOutputs(declaration, embedded.config);
    return {inputs, outputs};
  }
  return {inputs, outputs: host === undefined ? [] : declaredOutputs(host, node.config)};
}

export function splitRef(ref: string): [string, string] {
  const separator = ref.lastIndexOf('.');
  return [ref.slice(0, separator), ref.slice(separator + 1)];
}

/** Every input port of the graph, named "<node name> · <port>". */
export function inputTargets(document: GraphDocument, catalog: Catalog): PortTarget[] {
  return document.nodes.flatMap((node) =>
    nodePorts(node, catalog).inputs.map((port) => ({
      ref: `${node.id}.${port}`,
      label: `${node.name} · ${port}`,
    })),
  );
}

/** "<node name> · <port>" for a port reference, or the reference itself for unknown nodes. */
export function portLabel(document: GraphDocument, ref: string): string {
  const [nodeId, port] = splitRef(ref);
  const node = document.nodes.find((item) => item.id === nodeId);
  return node === undefined ? ref : `${node.name} · ${port}`;
}

/** A node's outgoing connections in the order of its outputs; unknown outputs come first. */
export function outgoingConnections(
  document: GraphDocument,
  node: GraphNode,
  catalog: Catalog,
): GraphDocument['connections'] {
  const outputs = nodePorts(node, catalog).outputs;
  const rank = (ref: string): number => outputs.indexOf(splitRef(ref)[1]);
  return document.connections
    .filter((item) => splitRef(item.from)[0] === node.id)
    .sort((left, right) => rank(left.from) - rank(right.from));
}

export function isTriggerOrOutput(node: GraphNode): boolean {
  const type = node.component.split('@')[0];
  return type === 'trigger' || type === 'output';
}

/** Each connection between existing ports, once per pair of nodes. */
export function linkedNodes(document: GraphDocument, catalog: Catalog): [string, string][] {
  const ports = new Map(document.nodes.map((node) => [node.id, nodePorts(node, catalog)]));
  const pairs = document.connections.flatMap((connection): [string, string][] => {
    const [source, output] = splitRef(connection.from);
    const [target, input] = splitRef(connection.to);
    const exists =
      ports.get(source)?.outputs.includes(output) === true &&
      ports.get(target)?.inputs.includes(input) === true;
    return exists ? [[source, target]] : [];
  });
  return [...new Map(pairs.map((pair) => [pair.join('\n'), pair])).values()];
}
