import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, renderHook, act} from '@testing-library/react';
import {documentPoints, eventPoint, isPoint, nodeFacets} from '../src/api/index.ts';
import type {GraphDocument, GraphNode, RunEvent} from '../src/api/index.ts';
import {useView} from '../src/features/activity/feed-view.tsx';
import {focusedPoints, pointLabels} from '../src/features/editor/observation-points.ts';
import {catalog, copy, j2} from './support/contract.ts';

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  localStorage.clear();
});

const node = (component: string, embedded: GraphNode['embedded'] = []): GraphNode => ({
  id: 'n',
  name: 'N',
  component,
  config: {},
  embedded,
});

it('derives a node’s facets from what its kind and embedded components record', () => {
  expect(nodeFacets(node('trigger@1.0.0'), catalog)).toEqual(['activity']);
  expect(nodeFacets(node('output@1.0.0'), catalog)).toEqual(['activity', 'results']);
  expect(nodeFacets(node('router@1.0.0'), catalog)).toEqual(['activity', 'calls', 'reports']);
  const memory = {position: 'memory' as const, component: 'memory@1.0.0', config: {}};
  expect(nodeFacets(node('missing@1.0.0', [memory]), catalog)).toEqual([
    'activity',
    'calls',
    'llm',
    'reports',
    'memory',
  ]);
});

it('names the points of a document and keeps unknown names readable', () => {
  const document: GraphDocument = copy(j2);
  const judge = document.nodes.find((item) => item.id === 'judge');
  if (judge === undefined) throw new Error('No judge');
  judge.embedded = [
    ...(judge.embedded ?? []),
    {position: 'memory', component: 'memory@9.0.0', config: {}},
  ];
  document.connections = [...document.connections, {from: 'gone.out', to: 'judge.in'}];
  const labels = pointLabels(document, catalog);
  expect(labels['node:judge/output']).toBe('Judge · Router');
  expect(labels['node:judge/memory']).toBe('Judge · Memory');
  expect(labels['connection:gone.out->judge.in']).toBe('gone → Judge');
  expect(focusedPoints('node:judge', document, catalog)).toContain('node:judge/memory');
  expect(focusedPoints('run', document, catalog)).toEqual(['run']);
  expect(documentPoints(document, catalog)[0]).toBe('run');
  expect([isPoint('run'), isPoint('node:x'), isPoint('connection:a->b'), isPoint('x')]).toEqual([
    true,
    true,
    true,
    false,
  ]);
});

it('places events on the run, a node facet or a connection', () => {
  const event = (fields: Partial<RunEvent>): RunEvent =>
    ({node_id: null, data: {}, kind: 'run.running', ...fields}) as RunEvent;
  expect(eventPoint(event({}))).toBe('run');
  expect(eventPoint(event({kind: 'report', node_id: 'p'}))).toBe('node:p/reports');
  expect(
    eventPoint(
      event({
        kind: 'component.called',
        node_id: 'p',
        data: {position: 'node'},
      } as Partial<RunEvent>),
    ),
  ).toBe('node:p/calls');
  expect(
    eventPoint(
      event({
        kind: 'component.called',
        node_id: 'p',
        data: {position: 'memory'},
      } as Partial<RunEvent>),
    ),
  ).toBe('node:p/memory');
});

it('keeps the feed view for the page when the browser refuses storage', () => {
  vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
    throw new Error('Blocked');
  });
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
    throw new Error('Blocked');
  });
  const {result} = renderHook(() => useView());
  expect(result.current[0]).toBe('content');
  act(() => {
    result.current[1]('all');
  });
  expect(result.current[0]).toBe('all');
});
