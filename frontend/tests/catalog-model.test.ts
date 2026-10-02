import {afterEach, expect, it, vi} from 'vitest';
import {DefinitionClient} from '../src/api/index.ts';
import type {LibraryPage} from '../src/api/index.ts';
import {CatalogModel} from '../src/app/catalog-model.ts';
import {libraryItem, libraryPage, option} from './support/catalog-data.ts';

afterEach(() => {
  vi.restoreAllMocks();
});

it('loads one bounded connected page until explicit Load more or Refresh', async () => {
  const read = vi.spyOn(DefinitionClient.prototype, 'list');
  read.mockResolvedValueOnce(libraryPage([libraryItem()], 'snapshot-page-2'));
  read.mockResolvedValueOnce(libraryPage([libraryItem('personal-1')]));
  read.mockResolvedValueOnce(libraryPage([libraryItem('personal-2')]));
  const model = new CatalogModel('key');
  await model.refresh();
  expect(read).toHaveBeenCalledTimes(1);
  expect(model.snapshot().graphs).toHaveLength(1);
  await model.loadMore();
  expect(read.mock.calls.map(([, cursor, limit]) => [cursor, limit])).toEqual([
    [undefined, 50],
    ['snapshot-page-2', 50],
  ]);
  model.select(option(libraryItem('personal-1')));
  expect(model.snapshot().graph?.revision).toBe('personal-1');
  await model.refresh();
  expect(model.snapshot().graphs.map(({revision}) => revision)).toEqual(['personal-2']);
  expect(model.snapshot().graph?.revision).toBe('personal-1');
  await model.loadMore();
  expect(read).toHaveBeenCalledTimes(3);
});

it('selects the exact saved revision found beyond the first fixed listing page', async () => {
  const saved = libraryItem('personal-2');
  const read = vi.spyOn(DefinitionClient.prototype, 'list');
  read.mockResolvedValueOnce(libraryPage([libraryItem()]));
  read.mockResolvedValueOnce(libraryPage([libraryItem()], 'fixed-2'));
  read.mockResolvedValueOnce(libraryPage([libraryItem('personal-1')], 'fixed-3'));
  read.mockResolvedValueOnce(libraryPage([saved]));
  const model = new CatalogModel('key');
  await model.refresh();
  await model.recoverSaved(saved);
  expect(read.mock.calls.map(([, cursor]) => cursor)).toEqual([
    undefined,
    undefined,
    'fixed-2',
    'fixed-3',
  ]);
  expect(model.snapshot().graph).toEqual(saved);
  expect(model.snapshot().confirmedSaved).toEqual(saved);
  expect(model.snapshot().selectionBlocked).toBe(false);
  expect(model.snapshot().needsSavedSelection).toBe(false);
});

it('retains confirmed identity on listing failure and recovers without another save', async () => {
  const saved = libraryItem('personal-1');
  const read = vi
    .spyOn(DefinitionClient.prototype, 'list')
    .mockResolvedValueOnce(libraryPage([libraryItem()]));
  const model = new CatalogModel('key');
  await model.refresh();
  read.mockRejectedValueOnce(new Error('offline'));
  await model.recoverSaved(saved);
  expect(model.snapshot().confirmedSaved).toEqual(saved);
  expect(model.snapshot().graph?.revision).toBe('example-2');
  expect(model.snapshot().selectionBlocked).toBe(true);
  expect(model.snapshot().error).toContain('saved definition is confirmed');
  read.mockResolvedValueOnce(libraryPage([saved]));
  await model.recoverSaved(saved);
  expect(model.snapshot().graph).toEqual(saved);
  expect(model.snapshot().error).toBeNull();
});

it('aborts a saved lookup superseded by an explicit exact selection', async () => {
  const read = vi
    .spyOn(DefinitionClient.prototype, 'list')
    .mockResolvedValueOnce(libraryPage([libraryItem(), libraryItem('personal-1')]));
  const model = new CatalogModel('key');
  await model.refresh();
  const reply = Promise.withResolvers<LibraryPage>();
  read.mockReturnValueOnce(reply.promise);
  const lookup = model.recoverSaved(libraryItem('personal-2'));
  const signal = read.mock.calls[1]?.[0];
  model.select(option(libraryItem('personal-1')));
  expect(signal?.aborted).toBe(true);
  reply.resolve(libraryPage([libraryItem('personal-2')]));
  await lookup;
  expect(model.snapshot().graph?.revision).toBe('personal-1');
  expect(model.snapshot().loading).toBe(false);
  expect(model.snapshot().selectionBlocked).toBe(false);
});
