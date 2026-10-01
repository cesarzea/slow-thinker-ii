import {MarkerType} from '@xyflow/react';
import type {GraphDetail, GraphStructure} from '../../api/index.ts';
import type {VisualGraph, VisualNode} from './types.ts';
import {
  componentConfiguration,
  definitionComponent,
  record,
  textValue,
} from './configuration-records.ts';

export const boundaryDistance = 112;
export function boundaryAnchor(id: string, node: string, entry: boolean): VisualNode {
  return {
    id,
    type: entry ? 'entry' : 'terminal',
    parentId: `node:${node}`,
    position: {x: entry ? -boundaryDistance : 264 + boundaryDistance, y: 0},
    data: {label: '', selection: null},
    draggable: false,
    selectable: false,
    focusable: false,
    connectable: false,
    domAttributes: {'aria-hidden': true},
  };
}
export function entryRoute(
  detail: GraphDetail | undefined,
  structure: GraphStructure,
  system: boolean,
): VisualGraph {
  const entry = declaredEntry(detail, structure);
  if (entry === undefined) return {nodes: [], edges: []};
  return {
    nodes: [boundaryAnchor(`entry:${entry}`, entry, true)],
    edges: [
      {
        id: `entry:${entry}`,
        source: `entry:${entry}`,
        target: `node:${entry}`,
        sourceHandle: 'out',
        targetHandle: 'in',
        type: 'route',
        ariaLabel: 'Graph entry',
        markerEnd: {type: MarkerType.ArrowClosed, color: '#405c79'},
        style: {stroke: '#405c79', strokeWidth: 2},
        selectable: false,
        focusable: false,
        data: {selection: null, returning: false, terminal: false, entry: true, system},
      },
    ],
  };
}
function declaredEntry(
  detail: GraphDetail | undefined,
  structure: GraphStructure,
): string | undefined {
  if (detail === undefined) return undefined;
  const controller = textValue(record(detail.definition['controller'])['component']);
  if (controller === undefined) return undefined;
  const type = definitionComponent(detail, controller)['type_id'];
  const config = controllerConfiguration(detail, controller);
  const entry = configuredEntry(type, config);
  return structure.nodes.some((node) => node.id === entry) ? entry : undefined;
}
function controllerConfiguration(
  detail: GraphDetail,
  controller: string,
): Readonly<Record<string, unknown>> {
  const saved = record(detail.execution?.['instances'])[controller];
  return saved === undefined
    ? componentConfiguration(detail, controller).config
    : record(record(saved)['config']);
}
function configuredEntry(
  type: unknown,
  config: Readonly<Record<string, unknown>>,
): string | undefined {
  if (type === 'bounded-flow') return textValue(config['entry']);
  const steps = config['steps'];
  if (type === 'example.sequence' && Array.isArray(steps)) return textValue(steps[0]);
  return undefined;
}
