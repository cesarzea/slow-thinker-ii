import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen} from '@testing-library/react';
import {OperatorClient} from '../src/api/index.ts';
import {Editor} from '../src/features/editor/index.ts';
import {editorApi, renderEditor} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j3} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});

it('links to the runs of the graph and the graphs page when given their addresses', async () => {
  editorApi('funny-story-with-review', j3);
  render(
    <Editor
      client={new OperatorClient('credential')}
      graphId="funny-story-with-review"
      created={null}
      runsHref="#/graphs/funny-story-with-review/runs"
      graphsHref="#/graphs"
      onDraft={vi.fn()}
    />,
  );
  const runs = await screen.findByRole('link', {name: 'Runs'});
  expect(runs.getAttribute('href')).toBe('#/graphs/funny-story-with-review/runs');
  expect(runs.nextElementSibling).toBe(screen.getByRole('group', {name: 'Mode'}));
  expect(screen.getByRole('link', {name: 'Graphs'}).getAttribute('href')).toBe('#/graphs');
  cleanup();
  await renderEditor(editorApi('funny-story-with-review', j3), 'funny-story-with-review');
  expect(screen.queryByRole('link', {name: 'Runs'})).toBeNull();
  expect(screen.queryByRole('link', {name: 'Graphs'})).toBeNull();
});

it('offers Arrange only when the graph has nodes', async () => {
  await renderEditor(editorApi('empty', null), 'empty', {
    ...j3,
    id: 'empty',
    nodes: [],
    connections: [],
    layout: {},
  });
  expect(screen.getByRole('button', {name: 'Arrange the graph'}).matches(':disabled')).toBe(true);
});
