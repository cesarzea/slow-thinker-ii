import {afterEach, expect, it, vi} from 'vitest';
import {act, cleanup, waitFor} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import type {ValidationResult} from '../src/api/index.ts';
import {
  disabled,
  draftText,
  EditorFixture,
  numericSource,
  parentReference,
  personalReference,
  press,
} from './support/editor-view.tsx';

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

it('cancels validation after an edit and ignores the old result', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  const reply = Promise.withResolvers<ValidationResult>();
  fixture.validate.mockReturnValue(reply.promise);
  fixture.change(draftText());
  await press('Validate definition');
  const signal = fixture.validate.mock.calls[0]?.[1];
  fixture.change(`${draftText()}\n`);
  expect(signal?.aborted).toBe(true);
  await act(async () => {
    reply.resolve({...personalReference, validation_scope: 'definition'});
    await reply.promise;
  });
  expect(disabled('Save definition')).toBe(true);
  expect(screen.queryByText(/Definition validation passed/)).toBeNull();
});

it('locks a pending backend draft and drops it after selection changes', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  const reply = Promise.withResolvers<string>();
  fixture.draft.mockReturnValue(reply.promise);
  await press('Create draft from saved definition');
  const signal = fixture.draft.mock.calls[0]?.[2];
  expect(fixture.text.readOnly).toBe(true);
  expect(disabled('Discard draft')).toBe(true);
  expect(disabled('Validate definition')).toBe(true);
  fixture.source.mockResolvedValue(draftText());
  fixture.select(personalReference);
  await waitFor(() => {
    expect(fixture.text.value).toBe(draftText());
  });
  expect(signal?.aborted).toBe(true);
  await act(async () => {
    reply.resolve('stale derived source');
    await reply.promise;
  });
  expect(fixture.text.value).toBe(draftText());
});

it('ignores an old raw-source reply after a newer exact selection', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  const reply = Promise.withResolvers<string>();
  fixture.source.mockReturnValueOnce(reply.promise).mockResolvedValue(numericSource);
  fixture.select(personalReference);
  const signal = fixture.source.mock.calls[1]?.[1];
  fixture.select(parentReference);
  await fixture.ready();
  expect(signal?.aborted).toBe(true);
  await act(async () => {
    reply.resolve(draftText());
    await reply.promise;
  });
  expect(fixture.text.value).toBe(numericSource);
  expect(fixture.dirty).toHaveBeenLastCalledWith(false);
});

it('rejects an oversized returned draft and retries a failed raw-source load', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  fixture.draft.mockResolvedValue('é'.repeat(524_289));
  await press('Create draft from saved definition');
  expect(screen.getByText(/revision draft exceeds/)).toBeTruthy();
  expect(fixture.text.value).toBe(numericSource);
  fixture.source.mockRejectedValueOnce(new Error('unavailable'));
  fixture.select(parentReference, 'new-key');
  await screen.findByText(/Could not load the saved definition/);
  expect(fixture.text.readOnly).toBe(true);
  await press('Retry loading saved definition');
  await fixture.ready();
  expect(fixture.text.readOnly).toBe(false);
});
