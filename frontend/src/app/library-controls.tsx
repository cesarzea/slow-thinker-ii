import type {ReactElement} from 'react';
import type {CatalogModel} from './catalog-model.ts';
import type {CatalogState} from './catalog-state.ts';

interface Props {
  readonly catalog: CatalogState & {readonly model: CatalogModel};
  readonly connected: boolean;
}

export function LibraryControls({catalog, connected}: Props): ReactElement {
  return (
    <section aria-label="Experiment library">
      <h2>{connected ? 'Experiment library' : 'Bundled experiments'}</h2>
      <LibraryActions catalog={catalog} connected={connected} />
      {catalog.loading && <p role="status">Loading experiments…</p>}
      {catalog.error !== null && <p role="alert">{catalog.error}</p>}
      <SavedSelection catalog={catalog} />
      {catalog.selectionBlocked && (
        <p role="status">
          Start is unavailable while the confirmed saved revision awaits selection. Retry its
          selection or explicitly choose a saved experiment.
        </p>
      )}
      {!catalog.loading && catalog.graphs.length === 0 && (
        <p>No saved experiments are available.</p>
      )}
    </section>
  );
}

function LibraryActions({catalog, connected}: Props): ReactElement {
  return (
    <div className="actions">
      <button
        disabled={catalog.loading}
        onClick={() => {
          void catalog.model.refresh();
        }}
      >
        Refresh library
      </button>
      {connected && (
        <button
          disabled={catalog.loading || catalog.nextCursor === null}
          onClick={() => {
            void catalog.model.loadMore();
          }}
        >
          Load more experiments
        </button>
      )}
    </div>
  );
}

function SavedSelection({catalog}: Pick<Props, 'catalog'>): ReactElement | null {
  const reference = catalog.confirmedSaved;
  if (reference === null) return null;
  return (
    <>
      <p role="status">
        Confirmed saved definition: {reference.graph_id} · {reference.revision}
      </p>
      {catalog.needsSavedSelection && (
        <button
          disabled={catalog.loading}
          onClick={() => {
            void catalog.model.recoverSaved(reference);
          }}
        >
          Retry saved definition selection
        </button>
      )}
    </>
  );
}
