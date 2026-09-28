import {useState} from 'react';
import type {ReactElement} from 'react';
import {ExecutionWorkspace} from './execution-workspace.tsx';
import {ExperimentPanel} from './experiment-panel.tsx';
import {useCatalog} from './use-catalog.ts';

interface Props {
  readonly credential: string | undefined;
  readonly generation: number;
}

export function CatalogPanel({credential, generation}: Props): ReactElement {
  const {graphs, error, loading} = useCatalog(credential);
  const [selected, select] = useState('');
  const graph = graphs.find((item) => item.graph_id === selected) ?? graphs[0];
  return (
    <>
      {loading && <p role="status">Cargando experimentos…</p>}
      {error !== null && <p role="alert">{error}</p>}
      {graph !== undefined && <ExperimentPanel graphs={graphs} graph={graph} onSelect={select} />}
      {credential !== undefined && graph !== undefined && (
        <ExecutionWorkspace key={generation} credential={credential} graph={graph} />
      )}
    </>
  );
}
