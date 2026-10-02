import type {GraphReference, GraphSummary} from '../api/index.ts';

export interface CatalogState {
  readonly graphs: readonly GraphSummary[];
  readonly graph: GraphSummary | null;
  readonly error: string | null;
  readonly loading: boolean;
  readonly nextCursor: string | null;
  readonly confirmedSaved: GraphReference | null;
  readonly needsSavedSelection: boolean;
  readonly selectionBlocked: boolean;
}

export interface CatalogPage {
  readonly items: readonly GraphSummary[];
  readonly next_cursor: string | null;
}

export function referenceKey(reference: GraphReference): string {
  return JSON.stringify([reference.graph_id, reference.revision]);
}

export function initialCatalog(): CatalogState {
  return {
    graphs: [],
    graph: null,
    error: null,
    loading: true,
    nextCursor: null,
    confirmedSaved: null,
    needsSavedSelection: false,
    selectionBlocked: false,
  };
}

export function mergePage(
  graphs: readonly GraphSummary[],
  page: CatalogPage,
): readonly GraphSummary[] {
  const merged = [...graphs, ...page.items];
  if (new Set(merged.map(referenceKey)).size !== merged.length) {
    throw new Error('The library repeated an experiment identity. Refresh the library.');
  }
  return merged;
}

export function savedSelection(state: CatalogState, graph: GraphSummary | null): CatalogState {
  return graph === null
    ? {
        ...state,
        loading: false,
        error:
          'The saved definition is confirmed, but was not found in this listing. Retry its library refresh.',
      }
    : {...state, loading: false, graph, needsSavedSelection: false, selectionBlocked: false};
}
