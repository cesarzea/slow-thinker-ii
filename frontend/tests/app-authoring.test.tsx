import type * as ReactFlowModule from '@xyflow/react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, waitFor} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {CatalogFixture} from './support/catalog-view.tsx';
import {libraryItem, libraryPage, option} from './support/catalog-data.ts';
import {
  draftText,
  numericSource,
  parentReference,
  personalReference,
  press,
} from './support/editor-view.tsx';

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

it('gates Start through editing and validation until the exact saved revision is selected', async () => {
  localStorage.clear();
  const fixture = new CatalogFixture();
  await fixture.ready();
  await press('Runs');
  await userEvent.type(screen.getByLabelText(/Task or problem/), 'personal input');
  const start = screen.getByRole<HTMLButtonElement>('button', {name: 'Start run'});
  expect(start.disabled).toBe(false);
  await press('Experiments');
  fixture.change(draftText());
  expect(start.disabled).toBe(true);
  expect(screen.getByText(/Unsaved draft — save or discard/)).toBeTruthy();
  await press('Validate definition');
  expect(start.disabled).toBe(true);
  fixture.list.mockResolvedValue(libraryPage([libraryItem(), libraryItem('personal-1')]));
  await press('Save definition');
  await waitFor(() => {
    expect(screen.getByLabelText<HTMLSelectElement>('Experiment').value).toBe(
      option(personalReference),
    );
  });
  await press('Runs');
  await userEvent.type(screen.getByLabelText(/Task or problem/), 'selected saved input');
  await press('Start run');
  expectSavedStart(fixture);
  expect(JSON.stringify(localStorage)).not.toMatch(/selected saved input|temperature/u);
});

it('keeps confirmed Save separate from failed listing and restores the selected source baseline', async () => {
  const fixture = new CatalogFixture();
  await fixture.ready();
  fixture.change(draftText());
  await press('Validate definition');
  fixture.list.mockRejectedValue(new Error('library offline'));
  await press('Save definition');
  expect(await screen.findByText(/its library refresh failed/)).toBeTruthy();
  expect(screen.getByText('Confirmed saved definition: single-agent · personal-1')).toBeTruthy();
  expect(fixture.text.value).toBe(numericSource);
  expect(screen.getByLabelText<HTMLSelectElement>('Experiment').value).toBe(
    option(parentReference),
  );
  expect(screen.queryByText(/Definition validation passed/)).toBeNull();
  await press('Create draft from saved definition');
  expect(fixture.draft).toHaveBeenLastCalledWith(
    parentReference,
    expect.any(Object),
    expect.any(AbortSignal),
  );
  await press('Discard draft');
  fixture.list.mockResolvedValue(libraryPage([libraryItem('personal-1')]));
  await press('Retry saved definition selection');
  await press('JSON source');
  await waitFor(() => {
    expect(fixture.text.value).toBe(draftText());
  });
  expect(fixture.save).toHaveBeenCalledTimes(1);
});

it('retains historical run evidence while selecting and editing another saved revision', async () => {
  const fixture = new CatalogFixture();
  await fixture.ready();
  await press('Runs');
  await userEvent.type(screen.getByLabelText(/Task or problem/), 'first run');
  await press('Start run');
  await screen.findByRole('heading', {name: 'Completed'});
  fixture.list.mockResolvedValue(libraryPage([libraryItem(), libraryItem('personal-1')]));
  await press('Experiments');
  await press('Refresh library');
  await userEvent.selectOptions(screen.getByLabelText('Experiment'), option(personalReference));
  await press('JSON source');
  await waitFor(() => {
    expect(fixture.text.value).toBe(draftText());
  });
  fixture.change(`${draftText()}\n`);
  await press('Runs');
  expect(
    within(screen.getByRole('region', {name: 'Run state'})).getByRole('heading', {
      name: 'Completed',
    }),
  ).toBeTruthy();
  expect(screen.getByRole('region', {name: 'Selected run graph'}).textContent).toContain(
    'example-2',
  );
  expect(fixture.operator.mutations.filter(({path}) => path.includes('/runs'))).toHaveLength(1);
});

function expectSavedStart(fixture: CatalogFixture): void {
  const body: unknown = JSON.parse(fixture.operator.mutations.at(-1)?.body ?? '{}');
  expect(body).toMatchObject({graph_id: 'single-agent', graph_revision: 'personal-1'});
}
