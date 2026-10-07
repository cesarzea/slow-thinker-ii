import type {
  Catalog,
  ComponentDeclaration,
  Diagnostic,
  GraphDocument,
  GraphNode,
} from '../../../api/index.ts';
import {jsonPreview, previewValue, readPointer, summaryValue} from '../../../ui/index.ts';
import {
  declarationFor,
  embeddedAt,
  embeddedOutput,
  nodePorts,
  portLabel,
  splitRef,
} from '../state/ports.ts';
import {cardPorts} from './card-model.ts';
import {arrowhead} from './edge-look.ts';
import type {CardBand, CardNode, CardValue, RouteEdgeType} from './types.ts';

export interface FlowInput {
  readonly document: GraphDocument;
  readonly catalog: Catalog;
  readonly editable: boolean;
  readonly diagnostics?: readonly Diagnostic[];
  readonly selected?: string | null;
  readonly activations?: Readonly<Record<string, number>>;
  readonly messages?: Readonly<Record<string, number>>;
}

function cardValues(
  node: GraphNode,
  declaration: ComponentDeclaration,
  catalog: Catalog,
): CardValue[] {
  const fields = declaration.ui.sections.flatMap((section) => section.fields);
  return declaration.ui.card.map((pointer) => {
    const field = fields.find((item) => item.path === pointer);
    const value = readPointer(node.config, pointer);
    if (field === undefined) return {text: jsonPreview(value), chip: false};
    const service = field.control === 'service' && value !== null && value !== undefined;
    const text = service
      ? previewValue(field, value, catalog.llms)
      : summaryValue(field, value, catalog.llms);
    return {text, chip: service};
  });
}

function band(node: GraphNode, catalog: Catalog): CardBand | null {
  const embedded = embeddedOutput(node);
  if (embedded === undefined) return null;
  const declaration = declarationFor(catalog, embedded.component);
  return {label: declaration?.label ?? embedded.component, icon: declaration?.icon ?? 'component'};
}

/** The node's memory: its label and the card values its own declaration names. */
function memory(node: GraphNode, catalog: Catalog): string | null {
  const embedded = embeddedAt(node, 'memory');
  if (embedded === undefined) return null;
  const declaration = declarationFor(catalog, embedded.component);
  if (declaration === undefined) return embedded.component;
  const values = cardValues({...node, config: embedded.config}, declaration, catalog);
  return [declaration.label, ...values.map((value) => value.text)].join(' · ');
}

function position(document: GraphDocument, node: GraphNode, index: number): {x: number; y: number} {
  const [x, y] = document.layout?.[node.id] ?? [40 + index * 270, 40];
  return {x, y};
}

function firstProblem(input: FlowInput, nodeId: string): string | null {
  const problem = input.diagnostics?.find(
    (item) => item.node_id === nodeId && item.severity === 'error',
  );
  return problem?.message ?? null;
}

function activations(input: FlowInput, nodeId: string): number | null {
  return input.activations === undefined ? null : (input.activations[nodeId] ?? 0);
}

function toCard(input: FlowInput, node: GraphNode, index: number): CardNode {
  const declaration = declarationFor(input.catalog, node.component);
  const ports = nodePorts(node, input.catalog);
  return {
    id: node.id,
    type: 'card',
    position: position(input.document, node, index),
    ariaLabel: node.name,
    selected: input.selected === node.id,
    data: {
      name: node.name,
      label: declaration?.label ?? node.component,
      icon: declaration?.icon ?? 'component',
      values: declaration === undefined ? [] : cardValues(node, declaration, input.catalog),
      inputs: ports.inputs,
      outputs: ports.outputs,
      ports: cardPorts(input.document, node, input.catalog),
      band: band(node, input.catalog),
      memory: memory(node, input.catalog),
      problem: firstProblem(input, node.id),
      activations: activations(input, node.id),
      interactive: input.editable,
    },
  };
}

/** React Flow nodes for the document's nodes, with effective ports and card values. */
export function flowNodes(input: FlowInput): CardNode[] {
  return input.document.nodes.map((node, index) => toCard(input, node, index));
}

/** The connection's data: its references and its route's name. */
function routeData(
  input: FlowInput,
  connection: GraphDocument['connections'][number],
): NonNullable<RouteEdgeType['data']> {
  const {from, to} = connection;
  const route = `${portLabel(input.document, from)} to ${portLabel(input.document, to)}`;
  return {from, to, route};
}

/** React Flow edges for the connections whose ports exist. */
export function flowEdges(input: FlowInput, nodes: readonly CardNode[]): RouteEdgeType[] {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  return input.document.connections.flatMap((connection) => {
    const [source, sourcePort] = splitRef(connection.from);
    const [target, targetPort] = splitRef(connection.to);
    const from = byId.get(source);
    const to = byId.get(target);
    if (!from?.data.outputs.includes(sourcePort) || !to?.data.inputs.includes(targetPort))
      return [];
    const count = input.messages?.[`${connection.from} -> ${connection.to}`];
    const data = routeData(input, connection);
    const edge: RouteEdgeType = {
      id: `${connection.from}->${connection.to}`,
      source,
      sourceHandle: sourcePort,
      target,
      targetHandle: targetPort,
      type: 'route',
      markerEnd: arrowhead(false),
      ariaLabel: `Connection from ${data.route}`,
      data,
      ...(count === undefined ? {} : {label: String(count)}),
    };
    return [edge];
  });
}
