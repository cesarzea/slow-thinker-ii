import single from '../../../docs/contracts/examples/single-agent.graph.json';
import bounded from '../../../docs/contracts/examples/bounded-review.graph.json';
import type {GraphDetail, ExecutionPage, GraphSummary} from '../../src/api/index.ts';
import {fixtureRoles} from './projection-roles.ts';

const inputSchema = {
  type: 'object',
  properties: {problem: {type: 'string', minLength: 1}},
  required: ['problem'],
  additionalProperties: false,
};
export const singleDetail: GraphDetail = {
  graph_id: single.graph_id,
  revision: single.revision,
  input_schema: inputSchema,
  definition: single,
  structure: {
    components: Object.entries(single.components).map(([id, item]) => ({
      id,
      type_id: item.type_id,
      type_version: item.type_version,
      roles: fixtureRoles(item.type_id),
      contained_by: null,
    })),
    nodes: [{id: 'draft', component: 'proposer'}],
    edges: [
      {id: 'exit', kind: 'control', source: 'draft', target: null, label: 'next'},
      {id: 'model', kind: 'permission', source: 'proposer', target: 'model', label: 'complete'},
    ],
  },
};
export const boundedDetail: GraphDetail = {
  graph_id: bounded.graph_id,
  revision: bounded.revision,
  input_schema: bounded.input_schema,
  definition: bounded,
  structure: {
    components: Object.entries(bounded.components).map(([id, item]) => ({
      id,
      type_id: item.type_id,
      type_version: item.type_version,
      roles: fixtureRoles(item.type_id),
      contained_by: 'contained_by' in item ? item.contained_by : null,
    })),
    nodes: [
      {id: 'propose', component: 'proposer'},
      {id: 'review', component: 'reviewer'},
    ],
    edges: [
      {id: 'next', kind: 'control', source: 'propose', target: 'review', label: 'next'},
      {id: 'return', kind: 'control', source: 'review', target: 'propose', label: 'revise'},
      {id: 'exit', kind: 'control', source: 'review', target: null, label: 'accept'},
      {id: 'worker', kind: 'binding', source: 'reviewer', target: 'review-worker', label: 'worker'},
      {
        id: 'allowed',
        kind: 'permission',
        source: 'reviewer',
        target: 'review-worker',
        label: 'generate',
      },
    ],
  },
};
export const executionPage: ExecutionPage = {
  run_id: 'run',
  graph_revision: singleDetail.revision,
  backend_generation: 'backend',
  through_sequence: 10,
  next_cursor: null,
  activations: [
    {
      id: 'activation',
      node: 'draft',
      component: 'proposer',
      ordinal: 1,
      state: 'completed',
      call_id: 'parent',
      selected_port: null,
    },
  ],
  calls: [
    {
      id: 'child',
      caller: 'proposer',
      target: 'model',
      operation: 'complete',
      parent_call_id: 'parent',
      activation_id: 'activation',
      state: 'completed',
    },
  ],
};
export const repeatedPage: ExecutionPage = {
  ...executionPage,
  graph_revision: boundedDetail.revision,
  activations: [
    {
      id: 'draft-one',
      node: 'propose',
      component: 'proposer',
      ordinal: 1,
      state: 'completed',
      call_id: 'one',
      selected_port: 'next',
    },
    {
      id: 'review-one',
      node: 'review',
      component: 'reviewer',
      ordinal: 2,
      state: 'completed',
      call_id: 'two',
      selected_port: 'revise',
    },
    {
      id: 'draft-two',
      node: 'propose',
      component: 'proposer',
      ordinal: 3,
      state: 'running',
      call_id: 'three',
      selected_port: null,
    },
  ],
  calls: [
    {
      id: 'worker-call',
      caller: 'reviewer',
      target: 'review-worker',
      operation: 'generate',
      parent_call_id: 'two',
      activation_id: 'review-one',
      state: 'completed',
    },
  ],
};
export function summary(detail: GraphDetail): GraphSummary {
  return {
    graph_id: detail.graph_id,
    revision: detail.revision,
    nodes: [...detail.structure.nodes],
    participants: detail.structure.components.filter((item) => item.roles.includes('agent')).length,
    input_schema: detail.input_schema,
  };
}
export function savedDefinition(detail: GraphDetail = singleDetail, run = 'run'): unknown {
  return {...detail, schema_version: '0.1-draft', run_id: run, execution: detail.execution ?? {}};
}
