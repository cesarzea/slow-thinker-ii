import {expect, it} from 'vitest';
import type {GraphDetail} from '../src/api/index.ts';
import {agentConfiguration} from '../src/features/graph-view/agent-configuration.ts';
import {singleDetail, boundedDetail} from './support/projection-data.ts';
import single from '../../docs/contracts/examples/single-agent.graph.json';
import bounded from '../../docs/contracts/examples/bounded-review.graph.json';

it.each([
  [{reasoning_effort: 'high'}, 'high'],
  [{reasoning: {effort: 'low'}}, 'low'],
  [{reasoning: {effort: ''}}, 'Not specified'],
  [{reasoning_effort: 5}, 'Not specified'],
])('reads only explicit reasoning parameters %j', (parameters, expected) => {
  const detail: GraphDetail = {
    ...singleDetail,
    execution: {instances: {proposer: {config: {parameters}}}},
  };
  expect(agentConfiguration(detail, 'proposer').effort).toEqual({
    value: expected,
    source: 'Saved configuration',
  });
});
it('uses original explicit parameters only when saved config is unavailable', () => {
  const detail: GraphDetail = {
    ...singleDetail,
    definition: {
      ...single,
      components: {
        ...single.components,
        proposer: {
          ...single.components.proposer,
          config: {...single.components.proposer.config, parameters: {reasoning_effort: 'medium'}},
        },
      },
    },
    execution: {instances: {proposer: {config: null}, model: {config: ['invalid']}}},
  };
  expect(agentConfiguration(detail, 'proposer').effort).toEqual({
    value: 'medium',
    source: 'Graph configuration',
  });
  expect(agentConfiguration(detail, 'proposer').model.value).toBe('illustrative-model');
});
it('does not infer effort from unrelated operations, defaults or enums', () => {
  const detail = savedOperations([
    operation('other', {const: 'high'}),
    operation('complete', {default: 'low', enum: ['none']}),
  ]);
  expect(agentConfiguration(detail, 'proposer').effort.value).toBe('Not specified');
});
it('does not choose a contradictory operation constant', () => {
  const detail = savedOperations([
    operation('complete', {const: 'none'}),
    operation('complete', {const: 'high'}),
  ]);
  expect(agentConfiguration(detail, 'proposer').effort.value).toBe('Not specified');
});
it('follows nested routed workers and resolves their actual model', () => {
  const detail: GraphDetail = {
    ...boundedDetail,
    definition: {
      ...bounded,
      components: {
        ...bounded.components,
        reviewer: {...bounded.components.reviewer, resources: {worker: 'nested'}},
        nested: {type_id: 'routed-call', resources: {worker: 'review-worker'}},
      },
    },
    execution: {instances: {'reviewer-model': {config: {model: 'saved-review-model'}}}},
  };
  expect(agentConfiguration(detail, 'reviewer').model).toEqual({
    value: 'saved-review-model',
    source: 'Saved configuration',
  });
});
it.each([undefined, {instances: null}, {instances: {model: {config: {model: 7}}}}])(
  'handles missing or malformed saved metadata %j',
  (execution) => {
    const detail: GraphDetail = {...singleDetail, ...(execution === undefined ? {} : {execution})};
    const expected =
      execution?.instances === null || execution === undefined
        ? 'illustrative-model'
        : 'Unavailable';
    expect(agentConfiguration(detail, 'proposer').model.value).toBe(expected);
  },
);
it('stops worker cycles and missing bindings without inventing metadata', () => {
  const cycle: GraphDetail = {
    ...boundedDetail,
    definition: {
      ...bounded,
      components: {
        reviewer: {type_id: 'routed-call', resources: {worker: 'reviewer'}},
      },
    },
  };
  expect(agentConfiguration(cycle, 'reviewer').model.value).toBe('Unavailable');
  expect(agentConfiguration(singleDetail, 'missing').model.value).toBe('Unavailable');
  expect(agentConfiguration(undefined, 'missing').effort.value).toBe('Not specified');
  const missing: GraphDetail = {
    ...singleDetail,
    definition: {...single, components: {proposer: {type_id: 'llm-call'}}},
  };
  expect(agentConfiguration(missing, 'proposer').model.value).toBe('Unavailable');
});
function savedOperations(operations: GraphDetail['definition'][string]): GraphDetail {
  return {...singleDetail, execution: {instances: {model: {operations}}}};
}
function operation(name: string, effort: GraphDetail['definition']): GraphDetail['definition'] {
  return {name, input_schema: {properties: {request: {properties: {reasoning_effort: effort}}}}};
}
