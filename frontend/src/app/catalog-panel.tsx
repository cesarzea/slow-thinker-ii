import type {GraphSummary, GraphReference} from '../api/index.ts';
import type {ReactElement} from 'react';
import {GraphWorkspace} from './graph-workspace.tsx';
import {ExecutionWorkspace} from './execution-workspace.tsx';
import {ExperimentPanel} from './experiment-panel.tsx';
import {LibraryControls} from './library-controls.tsx';
import {useCatalog} from './use-catalog.ts';

interface Props {
  readonly credential: string | undefined;
  readonly generation: number;
}

export function CatalogPanel({credential, generation}: Props): ReactElement {
  const catalog = useCatalog(credential);
  const {graph, graphs, model} = catalog;
  return (
    <>
      <LibraryControls catalog={catalog} connected={credential !== undefined} />
      {graph !== null && <ExperimentPanel graphs={graphs} graph={graph} onSelect={model.select} />}
      {graph !== null && (
        <SelectedWorkspace
          credential={credential}
          generation={generation}
          graph={graph}
          selectionBlocked={catalog.selectionBlocked}
          onSaved={(reference) => {
            void model.recoverSaved(reference);
          }}
        />
      )}
    </>
  );
}

function SelectedWorkspace({
  credential,
  generation,
  graph,
  onSaved,
  selectionBlocked,
}: Props & {
  readonly graph: GraphSummary;
  readonly onSaved: (reference: GraphReference) => void;
  readonly selectionBlocked: boolean;
}): ReactElement {
  return credential === undefined ? (
    <GraphWorkspace
      key={JSON.stringify([generation, graph.graph_id, graph.revision])}
      graph={graph}
    />
  ) : (
    <ExecutionWorkspace
      key={generation}
      credential={credential}
      graph={graph}
      onSaved={onSaved}
      selectionBlocked={selectionBlocked}
    />
  );
}
