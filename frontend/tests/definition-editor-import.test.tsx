import {afterEach, expect, it, vi} from 'vitest';
import {act, cleanup, waitFor} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {
  disabled,
  draftText,
  EditorFixture,
  importFile,
  numericSource,
  parentReference,
  press,
} from './support/editor-view.tsx';

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

async function upload(file: File): Promise<void> {
  await userEvent.upload(screen.getByLabelText('Import UTF-8 JSON file'), file);
}

it('bounds submitted text by UTF-8 bytes and preserves the last accepted source', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  const exact = `${numericSource}${' '.repeat(1_048_576 - new TextEncoder().encode(numericSource).length)}`;
  fixture.change(exact);
  expect(fixture.text.value).toBe(exact);
  fixture.change(`${exact}é`);
  expect(screen.getByText('JSON text exceeds the 1 MiB UTF-8 limit.')).toBeTruthy();
  expect(fixture.text.value).toBe(exact);
  expect(disabled('Save definition')).toBe(true);
});

it('rejects oversized files and actual buffers independently of reported file size', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  const file = importFile(new Uint8Array(1_048_577));
  await upload(file);
  expect(await screen.findByText('The JSON file exceeds the 1 MiB limit.')).toBeTruthy();
  Object.defineProperty(file, 'size', {value: 1});
  await upload(file);
  expect(fixture.text.value).toBe(numericSource);
  expect(screen.getByText('The JSON file exceeds the 1 MiB limit.')).toBeTruthy();
  expect(fixture.validate).not.toHaveBeenCalled();
});

it('rejects invalid UTF-8 and retains a BOM for authoritative JSON validation', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  await upload(importFile(new Uint8Array([0xc3, 0x28])));
  expect(await screen.findByText('Import a JSON file encoded as valid UTF-8.')).toBeTruthy();
  const source = `\uFEFF${draftText()}`;
  await upload(importFile(new TextEncoder().encode(source)));
  await waitFor(() => {
    expect(fixture.text.value).toBe(source);
  });
  expect(fixture.text.value.charCodeAt(0)).toBe(0xfeff);
  expect(disabled('Save definition')).toBe(true);
});

it('locks a pending import and ignores its reply after credentials change', async () => {
  const fixture = new EditorFixture();
  await fixture.ready();
  const reply = Promise.withResolvers<ArrayBuffer>();
  const file = new File(['pending'], 'pending.json', {type: 'application/json'});
  Object.defineProperty(file, 'arrayBuffer', {value: () => reply.promise});
  await upload(file);
  expect(fixture.text.readOnly).toBe(true);
  expect(disabled('Discard draft')).toBe(true);
  expect(disabled('Validate definition')).toBe(true);
  fixture.select(parentReference, 'replacement');
  await fixture.ready();
  await act(async () => {
    reply.resolve(new TextEncoder().encode(draftText()).buffer);
    await reply.promise;
  });
  expect(fixture.text.value).toBe(numericSource);
  expect(fixture.text.readOnly).toBe(false);
  await press('Discard draft');
  expect(fixture.text.value).toBe(numericSource);
});
