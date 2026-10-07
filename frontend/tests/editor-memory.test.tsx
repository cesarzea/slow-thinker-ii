import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {GraphDocument} from '../src/api/index.ts';
import {editorApi, renderEditor} from './support/editor-harness.tsx';
import type {FakeApi} from './support/fake-api.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j1, j2, memoryCatalogBody} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

const DRAG = 'application/x-slow-thinker-component';
const panel = (): HTMLElement => screen.getByRole('complementary', {name: 'Selected node'});

async function open(graphId: string, saved: GraphDocument): Promise<FakeApi> {
  const api = editorApi(graphId, saved).on('GET /catalog', {status: 200, body: memoryCatalogBody});
  await renderEditor(api, graphId);
  return api;
}

/** The embedded components the last saved change gives a node. */
function embedded(api: FakeApi, graphId: string, nodeId: string): unknown {
  const body = api.last(`POST /graphs/${graphId}/changes`)?.body as
    {document: GraphDocument} | undefined;
  const node = body?.document.nodes.find((item) => item.id === nodeId);
  return node?.embedded?.map((item) => `${item.position}:${item.component}`);
}

it('lists Memory inside a node and adds it to the selected node, or explains how', async () => {
  const api = await open('funny-story', j1);
  const palette = screen.getByRole('navigation', {name: 'Components'});
  const inside = within(palette).getByRole('region', {name: 'Inside a node'});
  const memory = within(inside).getByRole('button', {name: 'Add Memory'});
  await userEvent.click(memory);
  expect(screen.getByText('Drag Memory onto a node, or select a node first.')).toBeTruthy();
  fireEvent.click(screen.getByRole('group', {name: 'Story'}));
  await userEvent.click(memory);
  expect(screen.getByText('Story cannot contain Memory.')).toBeTruthy();
  fireEvent.click(screen.getByRole('group', {name: 'Proposer'}));
  await userEvent.click(memory);
  expect(screen.getByText('Memory added to Proposer.')).toBeTruthy();
  expect(within(panel()).getByText('LLM Call · 1.0.0 · with Memory')).toBeTruthy();
  const card = screen.getByRole('group', {name: 'Proposer'});
  expect(within(card).getByText('Memory · 10')).toBeTruthy();
  await waitFor(() => {
    expect(embedded(api, 'funny-story', 'proposer')).toEqual(['memory:memory@1.0.0']);
  });
});

it('adds Memory dropped onto a card, and only there', async () => {
  const api = await open('funny-story', j1);
  const item = screen.getByRole('button', {name: 'Add Memory'});
  const data = new Map<string, string>();
  const transfer = {
    types: [DRAG],
    setData: (type: string, value: string) => data.set(type, value),
    getData: (type: string) => data.get(type) ?? '',
    effectAllowed: 'all',
    dropEffect: 'none',
  };
  fireEvent.dragStart(item, {dataTransfer: transfer});
  const canvas = document.querySelector('.react-flow');
  const card = document.querySelector('.react-flow__node[data-id="proposer"]');
  if (canvas === null || card === null) throw new Error('No canvas');
  fireEvent.drop(canvas, {dataTransfer: transfer, clientX: 10, clientY: 10});
  expect(screen.getByText('Drag Memory onto a node, or select a node first.')).toBeTruthy();
  vi.spyOn(document, 'elementFromPoint').mockReturnValue(card);
  fireEvent.drop(canvas, {dataTransfer: transfer, clientX: 400, clientY: 300});
  await waitFor(() => {
    expect(embedded(api, 'funny-story', 'proposer')).toEqual(['memory:memory@1.0.0']);
  });
  expect(screen.queryByRole('group', {name: 'Memory'})).toBeNull();
});

it('keeps a Router and a Memory together and removes each one on its own', async () => {
  const api = await open('story-triage', j2);
  fireEvent.click(screen.getByRole('group', {name: 'Judge'}));
  await userEvent.click(within(panel()).getByRole('button', {name: 'Add component'}));
  const dialog = screen.getByRole('dialog', {name: 'Add component'});
  expect(within(dialog).queryByRole('button', {name: 'Router'})).toBeNull();
  await userEvent.click(within(dialog).getByRole('button', {name: 'Memory'}));
  await waitFor(() => {
    expect(embedded(api, 'story-triage', 'judge')).toEqual([
      'output:router@1.0.0',
      'memory:memory@1.0.0',
    ]);
  });
  expect(within(panel()).queryByRole('button', {name: 'Add component'})).toBeNull();
  expect(within(panel()).getByText(/with Router and Memory$/u)).toBeTruthy();
  await userEvent.click(within(panel()).getByRole('button', {name: 'Edit Memory'}));
  const node = screen.getByRole('dialog', {name: 'Judge'});
  const memoryTab = within(node).getByRole('tab', {name: 'Memory'});
  expect(memoryTab.getAttribute('aria-selected')).toBe('true');
  await userEvent.click(within(node).getByRole('button', {name: 'Remove Memory'}));
  const confirm = screen.getByRole('dialog', {name: 'Remove Memory'});
  expect(within(confirm).getByText('No connections will be removed.')).toBeTruthy();
  await userEvent.click(within(confirm).getByRole('button', {name: 'Remove'}));
  await userEvent.click(within(node).getByRole('button', {name: 'Apply'}));
  await waitFor(() => {
    expect(embedded(api, 'story-triage', 'judge')).toEqual(['output:router@1.0.0']);
  });
});

it('removes a Memory from the node menu and keeps the Router', async () => {
  const api = await open('story-triage', j2);
  fireEvent.click(screen.getByRole('group', {name: 'Judge'}));
  await userEvent.click(within(panel()).getByRole('button', {name: 'Add component'}));
  await userEvent.click(
    within(screen.getByRole('dialog', {name: 'Add component'})).getByRole('button', {
      name: 'Memory',
    }),
  );
  await userEvent.click(within(panel()).getByRole('button', {name: 'More actions for Judge'}));
  await userEvent.click(screen.getByRole('menuitem', {name: 'Remove Memory'}));
  const menuConfirm = screen.getByRole('dialog', {name: 'Remove Memory'});
  await userEvent.click(within(menuConfirm).getByRole('button', {name: 'Remove'}));
  await waitFor(() => {
    expect(embedded(api, 'story-triage', 'judge')).toEqual(['output:router@1.0.0']);
  });
});
