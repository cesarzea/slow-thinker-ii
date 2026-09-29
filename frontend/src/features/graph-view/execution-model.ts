import type {
  ExecutionPage,
  GraphStructure,
  ActivationView,
  CommunicationView,
} from '../../api/index.ts';
import type {VisualGraph} from './types.ts';
import {visibleComponent} from './structure-model.ts';
import {visualNode, visualEdge} from './visual-records.ts';

export function executionModel(
  page: ExecutionPage | undefined,
  structure: GraphStructure,
  expanded: boolean,
  observed: boolean,
): VisualGraph {
  if (page === undefined) return {nodes: [], edges: []};
  const nodes = page.activations.map(activationNode);
  if (!observed) return {nodes, edges: []};
  const known = new Set(structure.components.map((item) => item.id));
  const external = [...new Set(page.calls.flatMap((call) => [call.caller, call.target]))].filter(
    (id) => !known.has(id),
  );
  nodes.push(
    ...external.map((id, index) =>
      visualNode(`component:${id}`, id || 'Orquestador', index * 250, 700, null),
    ),
  );
  const edges = page.calls.map((call) => communicationEdge(call, structure, expanded));
  return {nodes, edges};
}

function activationNode(activation: ActivationView): VisualGraph['nodes'][number] {
  const port = activation.selected_port === null ? '' : ` → ${activation.selected_port}`;
  const label = `#${String(activation.ordinal)} ${activation.node} · ${activation.component} · ${activation.state}${port}`;
  return visualNode(`activation:${activation.id}`, label, (activation.ordinal - 1) * 250, 480, {
    kind: 'activation',
    id: activation.id,
  });
}

function communicationEdge(
  call: CommunicationView,
  structure: GraphStructure,
  expanded: boolean,
): VisualGraph['edges'][number] {
  return visualEdge(
    `observed:${call.id}`,
    `component:${visibleComponent(call.caller, structure, expanded)}`,
    `component:${visibleComponent(call.target, structure, expanded)}`,
    `Observada: ${call.operation} · ${call.state}`,
    '#167060',
    {kind: 'call', id: call.id},
  );
}
