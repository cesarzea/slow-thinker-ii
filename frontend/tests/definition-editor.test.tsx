import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, waitFor} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {DefinitionError} from '../src/api/index.ts';
import {
  disabled,
  draftText,
  EditorFixture,
  importFile,
  numericSource,
  parentReference,
  personalReference,
  press,
} from './support/editor-view.tsx';

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

it('loads raw numeric source and imports, validates and saves unchanged UTF-8 text', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  const source = `\n${draftText()}\n`;
  await userEvent.upload(
    screen.getByLabelText('Import UTF-8 JSON file'),
    importFile(new TextEncoder().encode(source)),
  );
  await waitFor(() => {
    expect(fixture.text.value).toBe(source);
  });
  expect(fixture.dirty).toHaveBeenLastCalledWith(true);
  expect(disabled('Save definition')).toBe(true);
  await press('Validate definition');
  expect(fixture.validate).toHaveBeenCalledWith(source, expect.any(AbortSignal));
  expect(screen.getByText(/Run inputs, policies, budgets/)).toBeTruthy();
  await press('Save definition');
  expect(fixture.save).toHaveBeenCalledWith(source, expect.any(AbortSignal));
  expect(fixture.saved).toHaveBeenCalledWith({...personalReference, created: true});
  expect(fixture.text.value).toBe(numericSource);
  expect(fixture.dirty).toHaveBeenLastCalledWith(false);
  expect(screen.queryByText(/Definition validation passed/)).toBeNull();
});

it('invalidates validation on edit and discards back to the selected saved source', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  fixture.change(draftText());
  await press('Validate definition');
  fixture.change(`${draftText()}\n`);
  expect(disabled('Save definition')).toBe(true);
  await press('Discard draft');
  expect(fixture.text.value).toBe(numericSource);
  expect(fixture.save).not.toHaveBeenCalled();
  expect(fixture.dirty).toHaveBeenLastCalledWith(false);
});

it('asks the backend for an exact-parent variant without rewriting numeric literals', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  const target = {...personalReference, graph_id: 'manual-variant'};
  fixture.draft.mockResolvedValue(draftText(target));
  await userEvent.clear(screen.getByLabelText('Graph ID'));
  await userEvent.type(screen.getByLabelText('Graph ID'), target.graph_id);
  await userEvent.clear(screen.getByLabelText('New revision'));
  await userEvent.type(screen.getByLabelText('New revision'), target.revision);
  await press('Create draft from saved definition');
  expect(fixture.draft).toHaveBeenCalledWith(parentReference, target, expect.any(AbortSignal));
  expect(fixture.text.value).toContain('"temperature":1.0');
  expect(fixture.text.value).toContain('9007199254740993');
  expect(fixture.text.value).toContain(`"derived_from":${JSON.stringify(parentReference)}`);
  expect(disabled('Create draft from saved definition')).toBe(true);
});

it('shows bounded rejection issues and never reports a rejected save as confirmed', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  fixture.validate.mockRejectedValue(
    new DefinitionError('invalid_definition', [
      {pointer: '/components/proposer/config', message: 'Invalid component configuration.'},
    ]),
  );
  fixture.change(draftText());
  await press('Validate definition');
  expect(screen.getByRole('list', {name: 'Definition validation issues'}).textContent).toContain(
    '/components/proposer/config',
  );
  expect(disabled('Save definition')).toBe(true);
  fixture.validate.mockResolvedValue({...personalReference, validation_scope: 'definition'});
  fixture.save.mockRejectedValue(new DefinitionError('request_too_large'));
  await press('Validate definition');
  await press('Save definition');
  expect(screen.getByText('request too large')).toBeTruthy();
  expect(fixture.text.readOnly).toBe(false);
  expect(fixture.saved).not.toHaveBeenCalled();
  expect(screen.queryByRole('button', {name: 'Retry same save'})).toBeNull();
});
