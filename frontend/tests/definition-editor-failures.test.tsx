import {afterEach, expect, it, vi} from 'vitest';
import {cleanup} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {DefinitionError} from '../src/api/index.ts';
import {
  draftText,
  EditorFixture,
  numericSource,
  parentReference,
  press,
} from './support/editor-view.tsx';

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

it('keeps a rejected draft on its selected source and exposes a safe stable error', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  fixture.draft.mockRejectedValueOnce(new DefinitionError('definition_parent_missing'));
  await press('Create draft from saved definition');
  expect(screen.getByText('definition parent missing')).toBeTruthy();
  expect(fixture.text.value).toBe(numericSource);
  expect(fixture.text.readOnly).toBe(false);
  fixture.draft.mockRejectedValueOnce(new Error('private backend details'));
  await press('Create draft from saved definition');
  expect(screen.getByText('Could not create the revision draft. Try again.')).toBeTruthy();
  expect(screen.queryByText('private backend details')).toBeNull();
});

it('blocks authoring when a selected raw source exceeds the editor byte cap', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  fixture.source.mockResolvedValue('é'.repeat(524_289));
  fixture.select(parentReference, 'other-key');
  expect(
    await screen.findByText('The saved definition exceeds the editor’s 1 MiB limit.'),
  ).toBeTruthy();
  expect(fixture.text.readOnly).toBe(true);
  expect(fixture.text.value).toBe('');
  expect(fixture.save).not.toHaveBeenCalled();
});

it('reports import I/O failure without replacing the source', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  const file = new File(['{}'], 'unreadable.json', {type: 'application/json'});
  Object.defineProperty(file, 'arrayBuffer', {
    value: () => Promise.reject(new Error('private file details')),
  });
  await userEvent.upload(screen.getByLabelText('Import UTF-8 JSON file'), file);
  expect(await screen.findByText('Could not read the JSON file.')).toBeTruthy();
  expect(fixture.text.value).toBe(numericSource);
  expect(fixture.text.readOnly).toBe(false);
});

it('reports transport validation failure and renders root-pointer issues as slash', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  fixture.change(draftText());
  fixture.validate.mockRejectedValueOnce(new Error('private validation details'));
  await press('Validate definition');
  expect(screen.getByText('Could not validate the definition. Try again.')).toBeTruthy();
  fixture.validate.mockRejectedValueOnce(
    new DefinitionError('invalid_definition', [{pointer: '', message: 'Invalid graph object.'}]),
  );
  await press('Validate definition');
  expect(screen.getByRole('list', {name: 'Definition validation issues'}).textContent).toContain(
    '/: Invalid graph object.',
  );
  expect(fixture.save).not.toHaveBeenCalled();
});
