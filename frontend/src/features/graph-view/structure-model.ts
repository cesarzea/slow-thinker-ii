import type {GraphStructure, PlannedNodeView} from '../../api/index.ts';
import type {GraphViewProps, VisualGraph, VisualNode} from './types.ts';
import {agentConfiguration} from './agent-configuration.ts';
import {agentActivity} from './execution-model.ts';
import {controlRoutes} from './control-routes.ts';
import {entryRoute} from './boundary-routes.ts';

export function graphStructure({graph, detail}: GraphViewProps): GraphStructure {
  if (detail !== undefined) return detail.structure;
  const components = [...new Set(graph.nodes.map((node) => node.component))].map((id) => ({
    id,
    type_id: 'Unavailable',
    type_version: '',
    roles: [],
    contained_by: null,
  }));
  return {components, nodes: graph.nodes, edges: []};
}
interface Options {
  readonly configuration: boolean;
  readonly system: boolean;
  readonly execution: boolean;
}
export function structureModel(props: GraphViewProps, options: Options): VisualGraph {
  const structure = graphStructure(props);
  const nodes = structure.nodes.map((item, index) => agentNode(item, index, props, options));
  const routes = controlRoutes(structure, options.system);
  const entry = entryRoute(props.detail, structure, options.system);
  return {
    nodes: [...nodes, ...routes.nodes, ...entry.nodes],
    edges: [...entry.edges, ...routes.edges],
  };
}
function agentNode(
  item: PlannedNodeView,
  index: number,
  props: GraphViewProps,
  options: Options,
): VisualNode {
  const type = graphStructure(props).components.find((part) => part.id === item.component)?.type_id;
  const componentType = displayType(type);
  const name = item.component.charAt(0).toUpperCase() + item.component.slice(1);
  const label = `${componentType} · ${name} · Step ${item.id}`;
  return {
    id: `node:${item.id}`,
    type: 'agent',
    position: {x: index * 400, y: 60},
    ariaLabel: label,
    data: {
      label,
      selection: {kind: 'node', id: item.id},
      agent: {
        name,
        componentType,
        knownAgent: type === 'llm-call' || type === 'routed-call',
        configuration: options.configuration
          ? agentConfiguration(props.detail, item.component)
          : undefined,
        activity: options.execution ? agentActivity(props.execution, item.id) : undefined,
      },
    },
  };
}
function displayType(type: string | undefined): string {
  if (type === 'llm-call') return 'LLMCall';
  if (type === 'routed-call') return 'RoutedCall';
  return type ?? 'Unavailable';
}
