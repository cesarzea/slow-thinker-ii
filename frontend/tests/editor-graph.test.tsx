import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {GraphDocument} from '../src/api/index.ts';
import {editorApi, renderEditor, saved} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j1} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
const graph = (): HTMLElement => screen.getByRole('complementary', {name: 'Graph'});

it('renames the graph from the Graph inspector when no node is selected', async () => {
  const {api} = await renderEditor(editorApi('funny-story', j1), 'funny-story');
  const name = within(graph()).getByRole('textbox', {name: 'Graph name'});
  await userEvent.clear(name);
  fireEvent.blur(name);
  expect(within(graph()).getByText('The graph needs a name.')).toBeTruthy();
  await userEvent.type(name, 'Funnier story{Enter}');
  expect(screen.getByRole('heading', {name: 'Funnier story', level: 1})).toBeTruthy();
  await saved();
  const stored = api.last('POST /graphs/funny-story/changes')?.body as {document: GraphDocument};
  expect(stored.document.name).toBe('Funnier story');
});

it('edits the four run limits inline and refuses values outside their ranges', async () => {
  const {api} = await renderEditor(editorApi('funny-story', j1), 'funny-story');
  const activations = within(graph()).getByRole('spinbutton', {name: 'Maximum activations'});
  await userEvent.clear(activations);
  await userEvent.type(activations, '20000{Enter}');
  expect(within(graph()).getByText(/Maximum activations must be a whole number/u)).toBeTruthy();
  expect(activations.getAttribute('aria-invalid')).toBe('true');
  await userEvent.keyboard('{Escape}');
  expect((activations as HTMLInputElement).value).toBe('20');
  await userEvent.clear(activations);
  await userEvent.type(activations, '10{Enter}');
  const budget = within(graph()).getByRole('textbox', {name: 'Budget per run ($)'});
  await userEvent.clear(budget);
  await userEvent.type(budget, '0{Enter}');
  expect(within(graph()).getByText(/Budget per run must be an amount/u)).toBeTruthy();
  await userEvent.type(budget, '.05');
  fireEvent.blur(budget);
  await saved();
  const stored = api.last('POST /graphs/funny-story/changes')?.body as {document: GraphDocument};
  expect(stored.document.limits).toEqual({...j1.limits, max_activations: 10, budget_usd: '0.05'});
});
