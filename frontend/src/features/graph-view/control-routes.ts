import {MarkerType} from '@xyflow/react';
import type {GraphStructure, RelationshipView} from '../../api/index.ts';
import type {VisualGraph, VisualEdge} from './types.ts';
import {boundaryAnchor} from './boundary-routes.ts';

export function controlRoutes(structure: GraphStructure, system: boolean): VisualGraph {
  const routes = structure.edges.filter((edge) => edge.kind === 'control');
  return {
    nodes: routes
      .filter((edge) => edge.target === null)
      .map((edge) => boundaryAnchor(`terminal:${edge.id}`, edge.source, false)),
    edges: routes.map((edge) => route(edge, structure, system)),
  };
}
function route(edge: RelationshipView, structure: GraphStructure, system: boolean): VisualEdge {
  const source = structure.nodes.findIndex((node) => node.id === edge.source);
  const target = structure.nodes.findIndex((node) => node.id === edge.target);
  const returning = edge.target !== null && target <= source;
  return {
    id: `control:${edge.id}`,
    source: `node:${edge.source}`,
    target: edge.target === null ? `terminal:${edge.id}` : `node:${edge.target}`,
    sourceHandle: returning ? 'return-source' : 'out',
    targetHandle: returning ? 'return-target' : 'in',
    type: 'route',
    label: edge.label,
    ariaLabel: `Control route: ${edge.label}`,
    markerEnd: {type: MarkerType.ArrowClosed, color: '#405c79'},
    style: {stroke: '#405c79', strokeWidth: 2},
    selectable: false,
    focusable: false,
    data: {selection: null, returning, terminal: edge.target === null, system},
  };
}
