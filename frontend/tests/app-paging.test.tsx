import type * as ReactFlowModule from '@xyflow/react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, waitFor} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {CatalogFixture} from './support/catalog-view.tsx';
import {libraryItem, libraryPage, option} from './support/catalog-data.ts';
import {draftText, personalReference, press} from './support/editor-view.tsx';

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

it('exposes explicit fixed-page controls while preserving selection outside a refreshed page', async () => {
  const fixture = new CatalogFixture(libraryPage([libraryItem()], 'fixed-page-2'));
  await fixture.ready();
  expect(fixture.list).toHaveBeenCalledTimes(1);
  const selector = screen.getByLabelText<HTMLSelectElement>('Experiment');
  expect(selector.options).toHaveLength(1);
  fixture.list.mockResolvedValueOnce(libraryPage([libraryItem('personal-1')]));
  await press('Load more experiments');
  expect(selector.options).toHaveLength(2);
  expect(fixture.list.mock.calls[1]?.[1]).toBe('fixed-page-2');
  await userEvent.selectOptions(selector, option(personalReference));
  await press('JSON source');
  await waitFor(() => {
    expect(fixture.text.value).toBe(draftText());
  });
  fixture.list.mockResolvedValueOnce(libraryPage([libraryItem()]));
  await press('Refresh library');
  expect(selector.value).toBe(option(personalReference));
  expect(selector.options).toHaveLength(2);
  await userEvent.selectOptions(selector, option(personalReference));
  expect(
    screen.getByRole<HTMLButtonElement>('button', {name: 'Load more experiments'}).disabled,
  ).toBe(true);
  expect(fixture.list).toHaveBeenCalledTimes(3);
});
