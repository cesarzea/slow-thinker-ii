import type * as ReactFlowModule from '@xyflow/react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {CatalogFixture} from './support/catalog-view.tsx';
import {numericSource, press} from './support/editor-view.tsx';
vi.mock('@xyflow/react', async (original) => {
  const {Canvas, Empty, EdgeFrame} = await import('./support/graph-canvas.tsx');
  return {
    ...(await original<typeof ReactFlowModule>()),
    ReactFlow: Canvas,
    Background: Empty,
    Controls: Empty,
    Handle: Empty,
    BaseEdge: EdgeFrame,
  };
});
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});
it('keeps one draft while keyboard navigation visits all five formal pages', async () => {
  const fixture = new CatalogFixture();
  await fixture.ready();
  fixture.change(`${numericSource}\n`);
  const navigation = within(screen.getByRole('navigation', {name: 'Workspace'}));
  expect(navigation.getAllByRole('button').map((button) => button.textContent)).toEqual([
    'Experiments',
    'Components',
    'Resources',
    'Runs',
    'Settings',
  ]);
  for (const name of ['Components', 'Resources', 'Settings', 'Runs', 'Experiments']) {
    const button = navigation.getByRole('button', {name});
    button.focus();
    await userEvent.keyboard('{Enter}');
    expect(button.getAttribute('aria-current')).toBe('page');
  }
  expect(fixture.text.value).toBe(`${numericSource}\n`);
  await press('Runs');
  expect(screen.getByText(/Unsaved draft/)).toBeTruthy();
  expect(fixture.operator.mutations).toHaveLength(0);
});
it('keeps unapplied settings edits when switching pages without issuing a command', async () => {
  const fixture = new CatalogFixture();
  await fixture.ready();
  await press('Settings');
  const field = screen.getByLabelText<HTMLInputElement>('Run deadline (seconds)', {exact: false});
  await userEvent.clear(field);
  await userEvent.type(field, '50.5');
  await press('Components');
  await press('Settings');
  expect(field.value).toBe('50.5');
  expect(fixture.operator.mutations).toHaveLength(0);
});
