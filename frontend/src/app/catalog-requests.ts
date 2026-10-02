import {DefinitionClient, loadGraphs} from '../api/index.ts';
import type {GraphReference, GraphSummary} from '../api/index.ts';
import {referenceKey} from './catalog-state.ts';
import type {CatalogPage} from './catalog-state.ts';

export async function readCatalog(
  credential: string | undefined,
  signal: AbortSignal,
  cursor?: string,
): Promise<CatalogPage> {
  if (credential === undefined) return {items: await loadGraphs(signal), next_cursor: null};
  return new DefinitionClient(credential).list(signal, cursor, 50);
}

export async function findSaved(
  reference: GraphReference,
  signal: AbortSignal,
  read: (cursor?: string) => Promise<CatalogPage>,
  accept: (page: CatalogPage, append: boolean) => void,
): Promise<GraphSummary | null> {
  const cursors = new Set<string>();
  let cursor: string | null | undefined;
  while (cursor !== null) {
    const page = await read(cursor);
    if (signal.aborted) return null;
    accept(page, cursor !== undefined);
    const found = page.items.find((item) => referenceKey(item) === referenceKey(reference));
    if (found !== undefined) return found;
    if (page.next_cursor !== null && cursors.has(page.next_cursor))
      throw new Error('The library repeated a cursor.');
    if (page.next_cursor !== null) cursors.add(page.next_cursor);
    cursor = page.next_cursor;
  }
  return null;
}
