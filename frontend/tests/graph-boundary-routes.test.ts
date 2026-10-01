import {expect, it} from 'vitest';
import type {GraphDetail} from '../src/api/index.ts';
import {entryRoute} from '../src/features/graph-view/boundary-routes.ts';
import {singleDetail, boundedDetail} from './support/projection-data.ts';

it('shows the declared sequence entry and preserves its step identity', () => {
  const entry = entryRoute(singleDetail, singleDetail.structure, false);
  expect(entry.edges[0]?.target).toBe('node:draft');
  expect(entry.edges[0]?.ariaLabel).toBe('Graph entry');
  expect(entry.nodes[0]?.parentId).toBe('node:draft');
  expect(entry.nodes[0]?.selectable).toBe(false);
  expect(entry.nodes[0]?.focusable).toBe(false);
});
it('shows the declared entry even when every step has an incoming loop route', () => {
  const entry = entryRoute(boundedDetail, boundedDetail.structure, false);
  expect(entry.edges[0]?.target).toBe('node:propose');
});
it('uses the saved controller entry rather than the illustrative definition', () => {
  const detail: GraphDetail = {
    ...boundedDetail,
    execution: {instances: {flow: {config: {entry: 'review'}}}},
  };
  expect(entryRoute(detail, detail.structure, true).edges[0]?.target).toBe('node:review');
});
it.each([null, [], {}, {steps: []}, {steps: ['missing', 'draft']}, {steps: [7]}])(
  'does not invent an entry from invalid saved sequence configuration %j',
  (config) => {
    const detail: GraphDetail = {...singleDetail, execution: {instances: {sequence: {config}}}};
    expect(entryRoute(detail, detail.structure, false).edges).toHaveLength(0);
  },
);
it.each([null, {entry: 'missing'}, {entry: ''}, {entry: 7}])(
  'rejects invalid saved bounded-flow entry %j',
  (config) => {
    const detail: GraphDetail = {...boundedDetail, execution: {instances: {flow: {config}}}};
    expect(entryRoute(detail, detail.structure, false).nodes).toHaveLength(0);
  },
);
it('does not infer an entry when the definition or controller identity is unavailable', () => {
  expect(entryRoute(undefined, singleDetail.structure, false).edges).toHaveLength(0);
  const detail: GraphDetail = {
    ...singleDetail,
    definition: {...singleDetail.definition, controller: {}},
  };
  expect(entryRoute(detail, detail.structure, false).edges).toHaveLength(0);
});
it('keeps unknown controllers visible without interpreting their configuration', () => {
  const detail: GraphDetail = {
    ...singleDetail,
    definition: {
      ...singleDetail.definition,
      controller: {component: 'extension'},
      components: {extension: {type_id: 'custom-controller', config: {steps: ['draft']}}},
    },
  };
  expect(entryRoute(detail, detail.structure, false).edges).toHaveLength(0);
});
