import type {GraphSummary, Run, Workspace} from '../../src/api/index.ts';

export const graph: GraphSummary = {
  graph_id: 'single-agent',
  revision: 'example-2',
  participants: 1,
  nodes: [{id: 'draft', component: 'proposer'}],
};
const budget = {
  currency: 'USD' as const,
  cap: '1.000000000',
  settled: '0.000000000',
  outstanding: '0.000000000',
  available: '1.000000000',
};
export const workspace: Workspace = {
  backend_generation: 'backend',
  configuration_revision: 'config',
  admission_available: true,
  admission_reason: null,
  blocking_run_id: null,
  month_budget: budget,
  sessions: {items: [{session_id: 'session', name: 'Research', created_at: 1}], next_cursor: null},
};

export function runRecord(id = 'run'): Run {
  return {
    run_id: id,
    session_id: 'session',
    graph_id: graph.graph_id,
    graph_revision: graph.revision,
    state: 'completed',
    reason: null,
    cleanup: 'confirmed',
    last_event_sequence: 10,
    backend_generation: 'backend',
    budget,
    session_budget: budget,
    admission_month_budget: budget,
    calls: {completed: 1},
  };
}

export function reply(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), {
    status,
    headers: {'content-type': 'application/json'},
  });
}
