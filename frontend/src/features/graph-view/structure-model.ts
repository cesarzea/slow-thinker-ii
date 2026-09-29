import type {
  GraphStructure,
  RelationshipView,
  ComponentView,
  PlannedNodeView,
} from '../../api/index.ts';
import type {GraphLayers, GraphViewProps, VisualGraph} from './types.ts';
import {componentRole, componentStyle} from './component-role.ts';
import {visualNode, visualEdge} from './visual-records.ts';

export function graphStructure({graph, detail}: GraphViewProps): GraphStructure {
  if (detail !== undefined) return detail.structure;
  const components = [...new Set(graph.nodes.map((node) => node.component))].map((id) => ({
    id,
    type_id: 'No disponible',
    type_version: '',
    roles: [],
    contained_by: null,
  }));
  return {components, nodes: graph.nodes, edges: []};
}
export function structureModel(
  structure: GraphStructure,
  layers: GraphLayers,
  expanded: boolean,
): VisualGraph {
  const nodes = structureNodes(structure, layers.control, expanded);
  const relationships = structure.edges.filter((edge) => layers[edge.kind]);
  const terminals = relationships
    .filter((edge) => edge.target === null)
    .map((edge, index) =>
      visualNode(
        `terminal:${edge.id}`,
        `Salida: ${edge.label}`,
        (structure.nodes.length + index) * 250,
        40,
        null,
      ),
    );
  return {
    nodes: [...nodes, ...terminals],
    edges: relationships.map((edge) => relationshipEdge(edge, structure, expanded)),
  };
}
function relationshipEdge(
  edge: RelationshipView,
  structure: GraphStructure,
  expanded: boolean,
): ReturnType<typeof visualEdge> {
  const source = endpoint(edge.source, edge.kind, structure, expanded);
  const target =
    edge.target === null
      ? `terminal:${edge.id}`
      : endpoint(edge.target, edge.kind, structure, expanded);
  const colors = {control: '#274f85', permission: '#986517', binding: '#7751a2'};
  const visual = visualEdge(
    `${edge.kind}:${edge.id}`,
    source,
    target,
    `${edge.kind}: ${edge.label}`,
    colors[edge.kind],
  );
  return isReturnRoute(edge, structure) ? {...visual, type: 'control-return'} : visual;
}
export function visibleComponent(id: string, structure: GraphStructure, expanded: boolean): string {
  let current = id;
  let parent = structure.components.find((item) => item.id === current)?.contained_by;
  while (!expanded && typeof parent === 'string') {
    current = parent;
    parent = structure.components.find((item) => item.id === current)?.contained_by;
  }
  return current;
}
function endpoint(
  id: string,
  kind: RelationshipView['kind'],
  structure: GraphStructure,
  expanded: boolean,
): string {
  return kind === 'control'
    ? `node:${id}`
    : `component:${visibleComponent(id, structure, expanded)}`;
}

function structureNodes(
  structure: GraphStructure,
  control: boolean,
  expanded: boolean,
): VisualGraph['nodes'] {
  const nodes = structure.components
    .filter((item) => expanded || item.contained_by === null)
    .map(componentNode);
  if (control) nodes.push(...structure.nodes.map(plannedNode));
  return nodes;
}

function componentNode(item: ComponentView, index: number): VisualGraph['nodes'][number] {
  const node = visualNode(
    `component:${item.id}`,
    `${componentRole(item)}: ${item.id}`,
    index * 250,
    260,
    {
      kind: 'component',
      id: item.id,
    },
  );
  return {...node, style: componentStyle(item)};
}
function plannedNode(item: PlannedNodeView, index: number): VisualGraph['nodes'][number] {
  return visualNode(`node:${item.id}`, `Nodo: ${item.id} · ${item.component}`, index * 250, 40, {
    kind: 'node',
    id: item.id,
  });
}

function isReturnRoute(edge: RelationshipView, structure: GraphStructure): boolean {
  if (edge.kind !== 'control' || edge.target === null) return false;
  return (
    structure.nodes.findIndex((node) => node.id === edge.target) <=
    structure.nodes.findIndex((node) => node.id === edge.source)
  );
}
