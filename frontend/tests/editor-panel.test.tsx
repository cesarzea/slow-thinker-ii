import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {triggerMessage} from '../src/features/editor/run-request.ts';
import type {Diagnostic, GraphDocument} from '../src/api/index.ts';
import {editorApi, renderEditor} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {copy, j1, j2} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
const panel = (): HTMLElement => screen.getByRole('complementary', {name: 'Selected node'});

it('lists connections from outputs a node no longer has, so they can be removed', async () => {
  const document = {...j2, connections: [...j2.connections, {from: 'judge.maybe', to: 'funny.in'}]};
  await renderEditor(editorApi('story-triage', document), 'story-triage');
  fireEvent.click(screen.getByRole('group', {name: 'Judge'}));
  const stale = within(panel()).getByRole('list', {name: 'Connections from missing outputs'});
  expect(stale.textContent).toContain('From missing output “maybe” to Funny · in');
  await userEvent.click(
    within(stale).getByRole('button', {name: 'Remove connection to Funny · in'}),
  );
  expect(
    within(panel()).queryByRole('list', {name: 'Connections from missing outputs'}),
  ).toBeNull();
  await userEvent.click(within(panel()).getByRole('button', {name: 'Edit Outputs'}));
  const dialog = screen.getByRole('dialog', {name: 'Judge'});
  expect(within(dialog).getByRole('tab', {name: 'Outputs'}).getAttribute('aria-selected')).toBe(
    'true',
  );
});

it('shows nodes of unknown components and nodes without outputs', async () => {
  const document: GraphDocument = copy(j1);
  document.nodes.push({
    id: 'mystery',
    name: 'Mystery',
    component: 'mystery@2.0.0',
    config: {},
    embedded: [{position: 'output', component: 'gone@1.0.0', config: {}}],
  });
  await renderEditor(editorApi('funny-story', document), 'funny-story');
  fireEvent.click(screen.getByRole('group', {name: 'Mystery'}));
  expect(within(panel()).getByText('mystery@2.0.0 · unknown · with gone@1.0.0')).toBeTruthy();
  await userEvent.click(within(panel()).getByRole('button', {name: 'More actions for Mystery'}));
  expect(screen.getByRole('menuitem', {name: 'Remove gone@1.0.0'})).toBeTruthy();
  await userEvent.keyboard('{Escape}');
  expect(screen.queryByRole('menu')).toBeNull();
  fireEvent.click(screen.getByRole('group', {name: 'Funny story'}));
  expect(within(panel()).getByText('This node has no outputs.')).toBeTruthy();
  expect(within(panel()).queryByRole('button', {name: 'Add component'})).toBeNull();
});

it('lists errors and warnings from the status bar, naming the node or the graph', async () => {
  const diagnostics: Diagnostic[] = [
    {
      severity: 'warning',
      code: 'no_output_node',
      message: 'The graph has no Output node.',
      path: '/nodes',
      node_id: null,
    },
    {
      severity: 'error',
      code: 'invalid_config',
      message: 'Instructions is required.',
      path: '/nodes/1/config/prompt',
      node_id: 'proposer',
    },
  ];
  await renderEditor(
    editorApi('funny-story', j1, () => diagnostics),
    'funny-story',
  );
  await userEvent.click(await screen.findByRole('button', {name: '2 problems'}));
  const items = within(screen.getByRole('list', {name: 'Problems'})).getAllByRole('listitem');
  expect(items.map((item) => item.textContent)).toEqual([
    'WarningGraphThe graph has no Output node.',
    'ErrorProposerInstructions is required.',
  ]);
});

it('uses an empty run message when the graph has no Trigger message', () => {
  expect(triggerMessage(j1)).toBe('A cat tried to learn to fly.');
  expect(triggerMessage({...j1, nodes: []})).toBe('');
  const document = copy(j1);
  if (document.nodes[0] !== undefined) document.nodes[0].config = {message: 3};
  expect(triggerMessage(document)).toBe('');
});

it('connects ports by clicking handles, selects with Enter and moves with the arrow keys', async () => {
  const graph = {...copy(j1), connections: []};
  const {api} = await renderEditor(editorApi('funny-story', graph), 'funny-story');
  fireEvent.click(screen.getByRole('button', {name: 'Story output out'}));
  fireEvent.click(screen.getByRole('button', {name: 'Proposer input in'}));
  const story = screen.getByRole('group', {name: 'Story'});
  fireEvent.keyDown(story, {key: 'Enter'});
  expect(within(panel()).getByRole('heading', {name: 'Story'})).toBeTruthy();
  expect(
    within(panel()).getByRole('button', {name: 'Remove connection to Proposer · in'}),
  ).toBeTruthy();
  fireEvent.keyDown(story, {key: 'ArrowRight'});
  await waitFor(() => {
    const stored = api.last('POST /graphs/funny-story/changes')?.body as {document: GraphDocument};
    expect(stored.document.layout?.['story']).toEqual([21, 100]);
  });
});
