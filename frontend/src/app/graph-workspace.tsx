import {useState} from 'react';
import type {ReactElement} from 'react';
import type {GraphSummary, GraphDetail} from '../api/index.ts';
import {GraphView} from '../features/graph-view/index.ts';
import type {GraphSelection} from '../features/graph-view/index.ts';
import {ObjectSummary} from './object-summary.tsx';
import {useGraphDetail} from './use-graph-detail.ts';

export function GraphWorkspace({graph}: {readonly graph: GraphSummary}): ReactElement {
  const {detail, error} = useGraphDetail(graph, undefined);
  return (
    <DefinitionGraph
      key={JSON.stringify([graph.graph_id, graph.revision])}
      graph={graph}
      detail={detail}
      error={error}
    />
  );
}
export function DefinitionGraph({
  graph,
  detail,
  error,
}: {
  readonly graph: GraphSummary;
  readonly detail: GraphDetail | null;
  readonly error: string | null;
}): ReactElement {
  const [selection, onSelect] = useState<GraphSelection>();
  return (
    <>
      {error !== null && <p role="alert">{error}</p>}
      <GraphView graph={graph} {...(detail === null ? {} : {detail})} onSelect={onSelect} />
      {detail !== null && selection !== undefined && (
        <ObjectSummary detail={detail} selection={selection} />
      )}
    </>
  );
}
