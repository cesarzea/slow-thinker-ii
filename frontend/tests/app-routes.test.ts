import {expect, it} from 'vitest';
import {GRAPHS, leavesEditor, parseRoute, routeHash, routeSection} from '../src/app/routes.ts';
import type {Route, Section} from '../src/app/routes.ts';

it.each<[string, Route]>([
  ['', GRAPHS],
  ['#', GRAPHS],
  ['#/', GRAPHS],
  ['#/graphs', GRAPHS],
  ['#/graphs/new', {kind: 'graphs', creating: true}],
  ['#/graphs/funny-story', {kind: 'editor', graphId: 'funny-story'}],
  ['#/graphs/funny-story/runs', {kind: 'runs', graphId: 'funny-story'}],
  ['#/graphs/funny-story/runs/run-1', {kind: 'run', graphId: 'funny-story', runId: 'run-1'}],
  ['#/graphs/funny-story/runs/run%201', GRAPHS],
  [
    '#/graphs/funny-story/runs/run.1/activity',
    {kind: 'activity', graphId: 'funny-story', runId: 'run.1'},
  ],
  ['#/runs', {kind: 'runs', graphId: null}],
  ['#/components', {kind: 'components'}],
])('parses %s', (hash, route) => {
  expect(parseRoute(hash)).toEqual(route);
});

it.each([
  '#/other',
  '#/graphs/Upper',
  '#/graphs/%E0%A4%A',
  '#/graphs/funny/extra',
  '#/graphs/funny/runs/',
  '#/graphs/funny/runs/r1/other',
  '#/graphs/funny/runs/r1/activity/more',
  '#/graphs/new/more',
  '#/graphs/Upper/runs',
  '#/runs/',
  '#/runs/run-1',
  '#/components/llm-call',
])('sends the unknown route %s to the graph list', (hash) => {
  expect(parseRoute(hash)).toEqual(GRAPHS);
});

it('builds the hash of every route and back', () => {
  const routes: Route[] = [
    GRAPHS,
    {kind: 'graphs', creating: true},
    {kind: 'editor', graphId: 'funny-story'},
    {kind: 'run', graphId: 'funny-story', runId: 'run-1'},
    {kind: 'activity', graphId: 'funny-story', runId: 'run-1'},
    {kind: 'runs', graphId: null},
    {kind: 'runs', graphId: 'funny-story'},
    {kind: 'components'},
  ];
  expect(routes.map(routeHash)).toEqual([
    '#/graphs',
    '#/graphs/new',
    '#/graphs/funny-story',
    '#/graphs/funny-story/runs/run-1',
    '#/graphs/funny-story/runs/run-1/activity',
    '#/runs',
    '#/graphs/funny-story/runs',
    '#/components',
  ]);
  expect(routes.map((route) => parseRoute(routeHash(route)))).toEqual(routes);
});

it.each<[Route, Section]>([
  [GRAPHS, 'graphs'],
  [{kind: 'graphs', creating: true}, 'graphs'],
  [{kind: 'editor', graphId: 'a'}, 'graphs'],
  [{kind: 'runs', graphId: null}, 'runs'],
  [{kind: 'runs', graphId: 'a'}, 'runs'],
  [{kind: 'run', graphId: 'a', runId: 'r'}, 'runs'],
  [{kind: 'activity', graphId: 'a', runId: 'r'}, 'runs'],
  [{kind: 'components'}, 'components'],
])('places %o in the %s section', (route, section) => {
  expect(routeSection(route)).toBe(section);
});

it('knows when a move leaves the open editor', () => {
  const editor: Route = {kind: 'editor', graphId: 'a'};
  expect(leavesEditor(editor, GRAPHS)).toBe(true);
  expect(leavesEditor(editor, {kind: 'editor', graphId: 'b'})).toBe(true);
  expect(leavesEditor(editor, {kind: 'runs', graphId: 'a'})).toBe(true);
  expect(leavesEditor(editor, {kind: 'components'})).toBe(true);
  expect(leavesEditor(editor, editor)).toBe(false);
  expect(leavesEditor(GRAPHS, editor)).toBe(false);
});
