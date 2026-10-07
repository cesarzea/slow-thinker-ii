import {useCallback} from 'react';
import type {ReactElement} from 'react';
import type {Catalog, OperatorClient} from '../../api/index.ts';
import {Panel, useRead} from '../../ui/index.ts';
import type {ReadResult} from '../../ui/index.ts';
import {Budgets} from './budgets.tsx';
import {ComponentList} from './component-list.tsx';
import {LlmList} from './llm-list.tsx';
import './catalog.css';

function CatalogSections({catalog}: {readonly catalog: ReadResult<Catalog>}): ReactElement {
  if (catalog.error !== null)
    return (
      <div role="alert" className="page-failure">
        <p>Could not load the catalog. {catalog.error}</p>
        <button type="button" onClick={catalog.refresh}>
          Try again
        </button>
      </div>
    );
  if (catalog.data === null) return <p className="muted">Loading the catalog…</p>;
  return (
    <>
      <Panel title="Components" className="catalog-section">
        <ComponentList components={catalog.data.components} />
      </Panel>
      <Panel title="LLMs" className="catalog-section">
        <LlmList llms={catalog.data.llms} />
      </Panel>
    </>
  );
}

/** The components, LLMs and budgets this server offers, read only. */
export function ComponentsPage({client}: {readonly client: OperatorClient}): ReactElement {
  const readCatalog = useCallback(async (signal: AbortSignal) => client.catalog(signal), [client]);
  const readUsage = useCallback(async (signal: AbortSignal) => client.usage(signal), [client]);
  const catalog = useRead(readCatalog);
  const usage = useRead(readUsage);
  return (
    <div className="page components-page">
      <div className="page-header">
        <div>
          <h1>Components</h1>
          <p>
            Read only. The operator installs components with <code>make components</code> and
            enables them, the LLMs and the budgets in the server configuration file. They cannot be
            edited from the interface yet.
          </p>
        </div>
      </div>
      <CatalogSections catalog={catalog} />
      <Budgets usage={usage} />
    </div>
  );
}
