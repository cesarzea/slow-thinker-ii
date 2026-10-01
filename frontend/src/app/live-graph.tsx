import {useState} from 'react';
import type {GraphDetail, ExecutionPage} from '../api/index.ts';
import type {ReactElement} from 'react';
import {GraphView} from '../features/graph-view/index.ts';
import type {GraphSelection} from '../features/graph-view/index.ts';
import type {ExecutionObservation} from '../features/execution/index.ts';
import type {InspectionSelection} from '../features/inspector/index.ts';
import {ObjectSummary} from './object-summary.tsx';

interface Props {
  readonly observation: ExecutionObservation;
  readonly onInspect: (run: string, selection: InspectionSelection) => void;
}
export function LiveGraph(props: Props): ReactElement | null {
  const {run, detail, projectionError, stale} = props.observation;
  if (run === null) return null;
  return (
    <section aria-label="Selected run graph">
      <h2>Run {run.run_id}</h2>
      <p>
        Saved definition: {run.graph_id} · {run.graph_revision}
      </p>
      {(stale || projectionError !== null) && (
        <p role="status">
          {projectionError ?? 'Connection unconfirmed. Waiting for the visual state to refresh.'}
        </p>
      )}
      {detail === null ? (
        <p>Waiting for the saved definition.</p>
      ) : (
        <SelectedGraph key={run.run_id} {...props} />
      )}
    </section>
  );
}
function SelectedGraph({observation, onInspect}: Props): ReactElement | null {
  const [selection, select] = useState<GraphSelection>();
  const {run, detail, execution} = observation;
  if (run === null || detail === null) return null;
  const onSelect = (item: GraphSelection): void => {
    select(item);
    if (item.kind === 'activation' || item.kind === 'call')
      onInspect(run.run_id, {kind: item.kind, id: item.id});
  };
  return (
    <>
      <SnapshotGraph detail={detail} execution={execution} onSelect={onSelect} />
      {selection !== undefined && (
        <ObjectSummary
          detail={detail}
          selection={selection}
          {...(execution === null ? {} : {execution})}
          onSelect={onSelect}
        />
      )}
    </>
  );
}

interface SnapshotProps {
  readonly detail: GraphDetail;
  readonly execution: ExecutionPage | null;
  readonly onSelect: (selection: GraphSelection) => void;
}
function SnapshotGraph({detail, execution, onSelect}: SnapshotProps): ReactElement {
  const graph = {
    graph_id: detail.graph_id,
    revision: detail.revision,
    participants: detail.structure.components.length,
    nodes: [...detail.structure.nodes],
  };
  return (
    <>
      {execution !== null && (
        <p>
          Snapshot through event {execution.through_sequence}
          {execution.next_cursor !== null && ' · Loading more evidence…'}
        </p>
      )}
      <GraphView
        graph={graph}
        detail={detail}
        {...(execution === null ? {} : {execution})}
        onSelect={onSelect}
      />
    </>
  );
}
