import {afterEach, expect, it, vi} from 'vitest';
import {act, cleanup, waitFor} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import type {SaveResult} from '../src/api/index.ts';
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

async function validated(fixture: EditorFixture): Promise<string> {
  await fixture.ready();
  const source = `\n${draftText()}\n`;
  fixture.change(source);
  await press('Validate definition');
  return source;
}

it('freezes a pending save and restores the actual selected baseline after confirmation', async () => {
  const fixture = new EditorFixture();
  const source = await validated(fixture);
  const reply = Promise.withResolvers<SaveResult>();
  fixture.save.mockReturnValue(reply.promise);
  await press('Save definition');
  expect(fixture.text.readOnly).toBe(true);
  expect(disabled('Discard draft')).toBe(true);
  expect(disabled('Create draft from saved definition')).toBe(true);
  expect(screen.getByLabelText<HTMLInputElement>('Import UTF-8 JSON file').disabled).toBe(true);
  fixture.change('modified while saving');
  expect(fixture.text.value).toBe(source);
  await act(async () => {
    reply.resolve({...personalReference, created: true});
    await reply.promise;
  });
  expect(fixture.text.value).toBe(numericSource);
  expect(disabled('Save definition')).toBe(true);
  await press('Create draft from saved definition');
  expect(fixture.draft).toHaveBeenLastCalledWith(
    parentReference,
    expect.any(Object),
    expect.any(AbortSignal),
  );
});

it('replays exactly the frozen source after an uncertain write', async () => {
  const fixture = new EditorFixture();
  const source = await validated(fixture);
  fixture.save.mockRejectedValueOnce(new Error('transport lost'));
  await press('Save definition');
  expect(screen.getByText(/Save unconfirmed/)).toBeTruthy();
  expect(fixture.text.readOnly).toBe(true);
  expect(fixture.dirty).toHaveBeenLastCalledWith(true);
  fixture.change('changed text');
  expect(fixture.text.value).toBe(source);
  fixture.save.mockResolvedValue({...personalReference, created: false});
  await press('Retry same save');
  expect(fixture.save.mock.calls.map(([text]) => text)).toEqual([source, source]);
  expect(fixture.saved).toHaveBeenCalledWith({...personalReference, created: false});
  expect(screen.getByText(/Identical saved definition confirmed/)).toBeTruthy();
  expect(fixture.text.value).toBe(numericSource);
});

it('can discard an uncertain draft while acknowledging the possible saved revision', async () => {
  const fixture = new EditorFixture();
  await validated(fixture);
  fixture.save.mockRejectedValue(new Error('no confirmed response'));
  await press('Save definition');
  await press('Discard draft');
  expect(fixture.text.value).toBe(numericSource);
  expect(fixture.text.readOnly).toBe(false);
  expect(screen.getByText(/previous save may have succeeded/)).toBeTruthy();
  expect(fixture.saved).not.toHaveBeenCalled();
});

it('aborts a pending save on credential replacement and ignores its late confirmation', async () => {
  const fixture = new EditorFixture();
  await validated(fixture);
  const reply = Promise.withResolvers<SaveResult>();
  fixture.save.mockReturnValue(reply.promise);
  await press('Save definition');
  const signal = fixture.save.mock.calls[0]?.[1];
  fixture.select(parentReference, 'replacement-key');
  await fixture.ready();
  expect(signal?.aborted).toBe(true);
  await act(async () => {
    reply.resolve({...personalReference, created: true});
    await reply.promise;
  });
  expect(fixture.saved).not.toHaveBeenCalled();
  expect(fixture.text.value).toBe(numericSource);
  expect(screen.queryByText(/Definition saved:/)).toBeNull();
  await waitFor(() => {
    expect(fixture.dirty).toHaveBeenLastCalledWith(false);
  });
});
