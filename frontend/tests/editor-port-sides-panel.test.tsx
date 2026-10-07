import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {GraphDocument} from '../src/api/index.ts';
import {editorApi, renderEditor, saved} from './support/editor-harness.tsx';
import {j3} from './support/contract.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const GRAPH = 'funny-story-with-review';
const panel = (): HTMLElement => screen.getByRole('complementary', {name: 'Selected node'});
const ports = (): HTMLElement => within(panel()).getByRole('region', {name: 'Ports'});
type Api = Awaited<ReturnType<typeof renderEditor>>['api'];
const stored = (api: Api): GraphDocument =>
  (api.last(`POST /graphs/${GRAPH}/changes`)?.body as {document: GraphDocument}).document;

async function choose(name: string, option: string): Promise<void> {
  await userEvent.selectOptions(within(ports()).getByRole('combobox', {name}), option);
  await saved();
}

it('puts a node’s ports top and bottom, or back left and right, as saved changes', async () => {
  const {api} = await renderEditor(editorApi(GRAPH, j3), GRAPH);
  fireEvent.click(screen.getByRole('group', {name: 'Reviewer'}));
  const mode = within(ports()).getByRole('combobox', {name: 'Port sides'});
  expect((mode as HTMLSelectElement).value).toBe('sides');
  await choose('Port sides', 'Top and bottom');
  expect(stored(api).port_sides).toEqual({
    reviewer: {in: 'top', accepted: 'bottom', revise: 'bottom'},
  });
  await choose('Port sides', 'Left and right');
  expect(stored(api).port_sides).toBeUndefined();
});

it('chooses a side per port once the sides are custom', async () => {
  const {api} = await renderEditor(editorApi(GRAPH, j3), GRAPH);
  fireEvent.click(screen.getByRole('group', {name: 'Reviewer'}));
  await userEvent.selectOptions(
    within(ports()).getByRole('combobox', {name: 'Port sides'}),
    'Custom',
  );
  expect(
    within(ports())
      .getAllByRole('combobox')
      .slice(1)
      .map((select) => (select as HTMLSelectElement).value),
  ).toEqual(['left', 'right', 'right']);
  await choose('Output revise', 'Left');
  expect(stored(api).port_sides).toEqual({
    reviewer: {in: 'left', accepted: 'right', revise: 'left'},
  });
  expect(within(ports()).getByRole('combobox', {name: 'Input in'})).toBeTruthy();
});

it('shows no port sides for a node without ports', async () => {
  const mystery = {id: 'mystery', name: 'Mystery', component: 'mystery@1.0.0', config: {}};
  await renderEditor(editorApi(GRAPH, {...j3, nodes: [...j3.nodes, mystery]}), GRAPH);
  fireEvent.click(screen.getByRole('group', {name: 'Mystery'}));
  expect(within(panel()).queryByRole('region', {name: 'Ports'})).toBeNull();
});
