import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {ElkNode} from 'elkjs/lib/elk-api.js';
import type {GraphDocument} from '../src/api/index.ts';
import {editorApi, renderEditor, saved} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j3} from './support/contract.ts';

const elk = vi.hoisted(() => ({layout: vi.fn(), load: vi.fn()}));
vi.mock('../src/features/editor/state/elk-loader.ts', () => ({loadElk: elk.load}));

beforeEach(() => {
  installFlowEnvironment();
  elk.layout.mockImplementation((graph: ElkNode) =>
    Promise.resolve({
      ...graph,
      children: graph.children?.map((child, index) => ({...child, x: index * 300, y: index * 10})),
    }),
  );
  elk.load.mockResolvedValue({layout: elk.layout});
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});
const stored = (api: Awaited<ReturnType<typeof renderEditor>>['api']): GraphDocument =>
  (api.last('POST /graphs/funny-story-with-review/changes')?.body as {document: GraphDocument})
    .document;

it('arranges to fit the screen with ELK and saves the positions as one change', async () => {
  const {api} = await renderEditor(
    editorApi('funny-story-with-review', j3),
    'funny-story-with-review',
  );
  await userEvent.click(screen.getByRole('button', {name: 'Arrange the graph'}));
  await saved();
  const graph = elk.layout.mock.lastCall?.[0] as ElkNode;
  expect(graph.layoutOptions?.['elk.layered.wrapping.strategy']).toBe('MULTI_EDGE');
  expect(graph.children?.find((child) => child.id === 'reviewer')?.ports).toHaveLength(3);
  expect(stored(api).layout).toEqual({
    story: [40, 40],
    proposer: [340, 50],
    reviewer: [640, 60],
    result: [940, 70],
  });
  expect(api.count('POST /graphs/funny-story-with-review/changes')).toBe(1);
});

async function choose(name: string): Promise<void> {
  await userEvent.click(screen.getByRole('button', {name: 'Arrange options'}));
  await userEvent.click(screen.getByRole('menuitem', {name}));
  await saved();
}

it('offers the port-aware ELK arrangements and React Flow’s layouts, by group', async () => {
  await renderEditor(editorApi('funny-story-with-review', j3), 'funny-story-with-review');
  await userEvent.click(screen.getByRole('button', {name: 'Arrange options'}));
  const menu = screen.getByRole('menu', {name: 'Arrange options'});
  const groups = within(menu).getAllByRole('group');
  expect(
    groups.map((group) => [
      group.getAttribute('aria-label'),
      within(group)
        .getAllByRole('menuitem')
        .map((item) => item.getAttribute('aria-label')),
    ]),
  ).toEqual([
    [
      'ELK with ports',
      ['Arrange: Fit to screen', 'Arrange: Compact', 'Arrange: ELK with ports (by flow)'],
    ],
    ['ELK tree', ['Arrange: ELK tree, left to right', 'Arrange: ELK tree, top to bottom']],
    ['Dagre tree', ['Arrange: Dagre tree, left to right', 'Arrange: Dagre tree, top to bottom']],
  ]);
  expect(within(menu).getByText('Dagre tree, left to right (horizontal flow)')).toBeTruthy();
});

it('lays the graph out with the options of each ELK arrangement', async () => {
  await renderEditor(editorApi('funny-story-with-review', j3), 'funny-story-with-review');
  await choose('Arrange: ELK with ports (by flow)');
  const flow = elk.layout.mock.lastCall?.[0] as ElkNode;
  expect(flow.layoutOptions?.['elk.layered.wrapping.strategy']).toBe('OFF');
  await choose('Arrange: Compact');
  const compact = elk.layout.mock.lastCall?.[0] as ElkNode;
  expect(compact.layoutOptions?.['elk.spacing.nodeNode']).toBe('24');
  await choose('Arrange: ELK tree, top to bottom');
  const tree = elk.layout.mock.lastCall?.[0] as ElkNode;
  expect(tree.layoutOptions?.['elk.direction']).toBe('DOWN');
});

it('arranges as a dagre tree, positions only, as one change', async () => {
  const {api} = await renderEditor(
    editorApi('funny-story-with-review', {...j3, port_sides: {reviewer: {in: 'top'}}}),
    'funny-story-with-review',
  );
  await choose('Arrange: Dagre tree, left to right');
  const document = stored(api);
  expect(document.port_sides).toEqual({reviewer: {in: 'top'}});
  const xs = ['story', 'proposer', 'reviewer', 'result'].map((id) => document.layout?.[id]?.[0]);
  expect(xs[0]).toBe(40);
  expect(xs).toEqual([...xs].sort((left, right) => (left ?? 0) - (right ?? 0)));
  expect(api.count('POST /graphs/funny-story-with-review/changes')).toBe(1);
  expect(elk.load).not.toHaveBeenCalled();
});

it('arranges with its own layered layout when ELK cannot be loaded', async () => {
  elk.load.mockRejectedValue(new Error('Offline'));
  const {api} = await renderEditor(
    editorApi('funny-story-with-review', j3),
    'funny-story-with-review',
  );
  await userEvent.click(screen.getByRole('button', {name: 'Arrange the graph'}));
  await saved();
  expect(stored(api).layout?.['story']).toEqual([40, expect.any(Number)]);
  expect(stored(api).layout?.['proposer']?.[0]).toBe(350);
});
