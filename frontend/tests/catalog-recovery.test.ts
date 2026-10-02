import {afterEach, expect, it, vi} from 'vitest';
import {DefinitionClient} from '../src/api/index.ts';
import type {LibraryPage} from '../src/api/index.ts';
import {CatalogModel} from '../src/app/catalog-model.ts';
import {libraryItem, libraryPage} from './support/catalog-data.ts';

afterEach(() => {
  vi.restoreAllMocks();
});

it.each(['cursor', 'identity'])(
  'stops a repeated %s without fabricating metadata',
  async (repeat) => {
    const read = vi.spyOn(DefinitionClient.prototype, 'list');
    read.mockResolvedValueOnce(libraryPage([libraryItem()]));
    read.mockResolvedValueOnce(libraryPage([libraryItem()], 'fixed-2'));
    read.mockResolvedValueOnce(
      repeat === 'cursor'
        ? libraryPage([libraryItem('other')], 'fixed-2')
        : libraryPage([libraryItem()]),
    );
    const model = new CatalogModel('key');
    await model.refresh();
    await model.recoverSaved(libraryItem('missing'));
    expect(read).toHaveBeenCalledTimes(3);
    expect(model.snapshot().graph?.revision).toBe('example-2');
    expect(model.snapshot().confirmedSaved?.revision).toBe('missing');
    expect(model.snapshot().needsSavedSelection).toBe(true);
    expect(model.snapshot().error).toContain('library refresh failed');
  },
);

it('stops at the fixed snapshot end while retaining an exhausted saved identity', async () => {
  const read = vi
    .spyOn(DefinitionClient.prototype, 'list')
    .mockResolvedValue(libraryPage([libraryItem()]));
  const model = new CatalogModel('key');
  await model.refresh();
  await model.recoverSaved(libraryItem('not-in-snapshot'));
  expect(read).toHaveBeenCalledTimes(2);
  expect(model.snapshot().error).toContain('not found in this listing');
  expect(model.snapshot().selectionBlocked).toBe(true);
  expect(model.snapshot().confirmedSaved?.revision).toBe('not-in-snapshot');
});

it('ignores a stale page after Refresh and aborts access disposal', async () => {
  const read = vi.spyOn(DefinitionClient.prototype, 'list');
  const reply = Promise.withResolvers<LibraryPage>();
  read
    .mockReturnValueOnce(reply.promise)
    .mockResolvedValueOnce(libraryPage([libraryItem('current')]));
  const model = new CatalogModel('key');
  const stale = model.refresh();
  const signal = read.mock.calls[0]?.[0];
  await model.refresh();
  expect(signal?.aborted).toBe(true);
  reply.resolve(libraryPage([libraryItem('stale')]));
  await stale;
  expect(model.snapshot().graphs.map(({revision}) => revision)).toEqual(['current']);
  model.dispose();
  expect(read.mock.calls[1]?.[0].aborted).toBe(true);
});

it('exposes initial errors and prevents repeated Load more cursors', async () => {
  const read = vi
    .spyOn(DefinitionClient.prototype, 'list')
    .mockRejectedValueOnce(new Error('offline'));
  const model = new CatalogModel('key');
  await model.refresh();
  expect(model.snapshot().graph).toBeNull();
  expect(model.snapshot().loading).toBe(false);
  read.mockResolvedValueOnce(libraryPage([libraryItem()], 'repeated'));
  await model.refresh();
  read.mockResolvedValueOnce(libraryPage([libraryItem('new')], 'repeated'));
  await model.loadMore();
  expect(model.snapshot().graphs).toHaveLength(1);
  expect(model.snapshot().error).toContain('Refresh to start a new listing');
});
