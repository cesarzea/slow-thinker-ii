import type {GraphReference, LibraryItem, LibraryPage} from '../../src/api/index.ts';
import {singleDetail, summary} from './projection-data.ts';

export function libraryItem(revision = 'example-2', graphId = 'single-agent'): LibraryItem {
  return {
    ...summary(singleDetail),
    graph_id: graphId,
    revision,
    origin: revision === 'example-2' ? 'bundled' : 'personal',
    derived_from: null,
  };
}

export function libraryPage(items: LibraryItem[], cursor: string | null = null): LibraryPage {
  return {items, next_cursor: cursor};
}

export function option(reference: GraphReference): string {
  return JSON.stringify([reference.graph_id, reference.revision]);
}
