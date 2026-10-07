import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {GraphPreview} from '../src/features/editor/index.ts';
import {editorApi, renderEditor, saved, toolbarStatus} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {catalog, j1} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});
const ROUTE = 'Story · out to Proposer · in';
const connection = (): HTMLElement | null =>
  screen.queryByRole('img', {name: `Connection from ${ROUTE}`});
const removeButton = (): HTMLElement | null =>
  screen.queryByRole('button', {name: `Remove connection from ${ROUTE}`});

async function selectConnection(): Promise<void> {
  const edge = connection();
  if (edge === null) throw new Error('No connection to select');
  await userEvent.click(edge);
  expect(edge.classList.contains('selected')).toBe(true);
}

it('selects a connection with a click and removes it with its × button', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  expect(removeButton()).toBeNull();
  await selectConnection();
  await userEvent.click(removeButton() ?? document.body);
  expect([connection(), removeButton()]).toEqual([null, null]);
  await saved();
  expect(toolbarStatus()).toBe('Saved · 1 change since v1');
});

it('removes the selected connection with Delete or Backspace, never while typing', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  await selectConnection();
  const field = document.body.appendChild(document.createElement('input'));
  field.focus();
  await userEvent.keyboard('{Backspace}{Delete}');
  expect(connection()).not.toBeNull();
  field.remove();
  document.body.focus();
  await userEvent.keyboard('{Delete}');
  expect(connection()).toBeNull();
  const output = screen.queryByRole('img', {
    name: 'Connection from Proposer · out to Funny story · in',
  });
  if (output === null) throw new Error('No second connection');
  await userEvent.click(output);
  await userEvent.keyboard('{Backspace}');
  expect(screen.queryAllByRole('img', {name: /^Connection from/u})).toHaveLength(0);
});

it('clears the selected connection with Escape or a click on the empty canvas', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  await selectConnection();
  await userEvent.keyboard('{Escape}');
  expect(removeButton()).toBeNull();
  await selectConnection();
  const pane = document.querySelector('.react-flow__pane');
  if (pane === null) throw new Error('No canvas pane');
  fireEvent.click(pane);
  expect(removeButton()).toBeNull();
  expect(connection()).not.toBeNull();
});

it('lists incoming connections in the side panel, each with Remove', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  fireEvent.click(screen.getByRole('group', {name: 'Proposer'}));
  const panel = screen.getByRole('complementary', {name: 'Selected node'});
  const incoming = within(panel).getByRole('list', {name: 'Incoming connections'});
  expect(within(incoming).getByText('Story · out')).toBeTruthy();
  expect(within(panel).getByRole('combobox', {name: 'Connect out to'})).toBeTruthy();
  expect(
    within(panel).getByRole('button', {name: 'Remove connection to Funny story · in'}),
  ).toBeTruthy();
  await userEvent.click(
    within(panel).getByRole('button', {name: 'Remove connection from Story · out'}),
  );
  expect(within(panel).queryByRole('list', {name: 'Incoming connections'})).toBeNull();
  expect(connection()).toBeNull();
});

it('never offers removal on the read-only canvas of a run', async () => {
  render(
    <div style={{width: '900px', height: '500px'}}>
      <GraphPreview
        document={j1}
        catalog={catalog}
        activations={{}}
        messages={{'story.out -> proposer.in': 2}}
      />
    </div>,
  );
  const edge = await screen.findByRole('img', {name: `Connection from ${ROUTE}`});
  await userEvent.click(edge);
  expect(removeButton()).toBeNull();
  expect(screen.getByText('2')).toBeTruthy();
});

it('draws the hovered or selected connection and its source port in the accent colour', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  const active = (): HTMLElement | null => document.querySelector('.edge-port.active');
  const edge = connection()?.closest('.react-flow__edge');
  if (edge === null || edge === undefined) throw new Error('No connection');
  fireEvent.mouseEnter(edge);
  expect(active()?.textContent).toBe('out');
  const marker = (): string | null =>
    edge.querySelector('.react-flow__edge-path')?.getAttribute('marker-end') ?? null;
  expect(marker()).toContain('1d5c79');
  fireEvent.mouseLeave(edge);
  expect(active()).toBeNull();
  expect(marker()).toContain('8b939e');
  await selectConnection();
  expect(active()?.textContent).toBe('out');
});
