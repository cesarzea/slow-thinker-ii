import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {GraphPreview} from '../src/features/editor/index.ts';
import type {GraphDocument} from '../src/api/index.ts';
import {editorApi, renderEditor, saved} from './support/editor-harness.tsx';
import {catalog, j3} from './support/contract.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const GRAPH = 'funny-story-with-review';
type Api = Awaited<ReturnType<typeof renderEditor>>['api'];
const stored = (api: Api): GraphDocument | undefined =>
  (api.last(`POST /graphs/${GRAPH}/changes`)?.body as {document: GraphDocument} | undefined)
    ?.document;
const paths = (): string[] =>
  [...document.querySelectorAll('.graph-canvas .react-flow__edge-path')].map(
    (path) => path.getAttribute('d') ?? '',
  );

it('draws curved connections unless the graph says routed, as an undoable saved change', async () => {
  const {api} = await renderEditor(editorApi(GRAPH, j3), GRAPH);
  expect(paths().every((path) => path.includes(' C'))).toBe(true);
  await userEvent.click(screen.getByRole('button', {name: 'Connection style'}));
  const curved = screen.getByRole('menuitemradio', {name: 'Curved connections'});
  expect(curved.getAttribute('aria-checked')).toBe('true');
  await userEvent.click(
    screen.getByRole('menuitemradio', {name: 'Connections routed around boxes'}),
  );
  await saved();
  expect(stored(api)?.view).toEqual({connections: 'routed'});
  expect(paths().some((path) => path.includes(' C'))).toBe(false);
  expect(screen.queryByRole('slider', {name: 'Curvature'})).toBeNull();
  await userEvent.click(screen.getByRole('button', {name: /^Undo$/u}));
  await saved();
  expect(stored(api)?.view).toBeUndefined();
});

it('previews the curvature while the slider moves and saves it once on release', async () => {
  const {api} = await renderEditor(editorApi(GRAPH, j3), GRAPH);
  await userEvent.click(screen.getByRole('button', {name: 'Connection style'}));
  const slider = screen.getByRole<HTMLInputElement>('slider', {name: 'Curvature'});
  expect(slider.value).toBe('0.25');
  const before = paths();
  fireEvent.change(slider, {target: {value: '0.6'}});
  fireEvent.change(slider, {target: {value: '0.9'}});
  expect(api.count(`POST /graphs/${GRAPH}/changes`)).toBe(0);
  fireEvent.pointerUp(slider);
  await saved();
  expect(api.count(`POST /graphs/${GRAPH}/changes`)).toBe(1);
  expect(stored(api)?.view).toEqual({curvature: 0.9});
  expect(slider.value).toBe('0.9');
  expect(paths()).toHaveLength(before.length);
});

it('draws a read-only canvas with the saved graph’s own view', () => {
  render(
    <div style={{width: '900px', height: '500px'}}>
      <GraphPreview document={{...j3, view: {connections: 'routed'}}} catalog={catalog} />
    </div>,
  );
  expect(paths().length).toBeGreaterThan(0);
  expect(paths().some((path) => path.includes(' C'))).toBe(false);
});

it('draws simple curves when the graph says so, without the curvature slider', async () => {
  const {api} = await renderEditor(editorApi(GRAPH, j3), GRAPH);
  await userEvent.click(screen.getByRole('button', {name: 'Connection style'}));
  expect(
    screen.getAllByRole('menuitemradio').map((item) => item.getAttribute('aria-label')),
  ).toEqual(['Curved connections', 'Simple curve connections', 'Connections routed around boxes']);
  const curved = paths();
  await userEvent.click(screen.getByRole('menuitemradio', {name: 'Simple curve connections'}));
  await saved();
  expect(stored(api)?.view).toEqual({connections: 'simple'});
  expect(screen.queryByRole('slider', {name: 'Curvature'})).toBeNull();
  expect(paths().every((path) => path.includes(' C'))).toBe(true);
  expect(paths()).not.toEqual(curved);
});
