import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {editorApi, missingModel, renderEditor} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {copy, j3} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
const button = (name: string): HTMLButtonElement =>
  screen.getByRole<HTMLButtonElement>('button', {name});

it('outlines the nodes in flow order with their problems and where their outputs lead', async () => {
  const document = copy(j3);
  const reviewer = document.nodes[2];
  if (reviewer !== undefined) reviewer.config = {...reviewer.config, model: null};
  await renderEditor(editorApi('review', document, missingModel), 'review');
  await screen.findByRole('button', {name: '1 problem'});
  await userEvent.click(button('Outline'));
  expect(button('Outline').getAttribute('aria-pressed')).toBe('true');
  const outline = screen.getByRole('list', {name: 'Outline'});
  const entries = within(outline)
    .getAllByRole('listitem')
    .filter((item) => item.parentElement === outline);
  expect(entries.map((item) => item.querySelector('.outline-name')?.textContent)).toEqual([
    'Story',
    'Proposer',
    'Reviewer',
    'Funny story',
  ]);
  const routes = within(outline).getByRole('list', {name: 'Connections from Reviewer'});
  expect(
    within(routes)
      .getAllByRole('listitem')
      .map((item) => item.textContent),
  ).toEqual(['accepted→ Funny story · in', 'revise→ Proposer · in']);
  expect(within(outline).getByText('1 problem')).toBeTruthy();
  await userEvent.click(button('Outline'));
  expect(screen.queryByRole('list', {name: 'Outline'})).toBeNull();
});

it('zooms the canvas from the toolbar and frames the graph again', async () => {
  await renderEditor(editorApi('review', j3), 'review');
  const zoom = (): string => screen.getByTitle('Zoom').textContent;
  const before = zoom();
  await userEvent.click(button('Zoom in'));
  await userEvent.click(button('Zoom out'));
  await userEvent.click(button('Fit to screen'));
  expect(zoom()).toMatch(/^\d+%$/u);
  expect(before).toMatch(/^\d+%$/u);
});
