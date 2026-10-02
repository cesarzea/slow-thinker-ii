import type {ReactElement} from 'react';
import type {GraphSummary} from '../api/index.ts';
import {ExecutionPanel} from '../features/execution/index.ts';
import type {ExecutionObservation} from '../features/execution/index.ts';
import type {ExperimentReadiness} from './experiment-types.ts';
import {referenceKey} from './catalog-state.ts';
interface Props {
  readonly graph: GraphSummary;
  readonly credential: string;
  readonly readiness: ExperimentReadiness | undefined;
  readonly selectionBlocked?: boolean;
  readonly onObservation: (state: ExecutionObservation) => void;
  readonly onInspect: (run: string) => void;
}
export function RunWorkspace(props: Props): ReactElement {
  const ready = props.readiness?.key === referenceKey(props.graph) ? props.readiness : undefined;
  const blocked = (ready?.blocked ?? true) || props.selectionBlocked === true;
  return (
    <>
      <h2>Runs</h2>
      <StartStatus ready={ready} />
      <p>
        Start admits the selected saved revision. Resolve unsaved edits and pending configuration
        changes first.
      </p>
      <ExecutionPanel
        credential={props.credential}
        graph={ready?.graph ?? props.graph}
        inputUnavailable={blocked}
        onObservation={props.onObservation}
        onInspect={props.onInspect}
      />
    </>
  );
}

function StartStatus({
  ready,
}: {
  readonly ready: ExperimentReadiness | undefined;
}): ReactElement | null {
  if (ready === undefined) return null;
  return (
    <>
      {ready.error !== null && <p role="alert">{ready.error}</p>}
      {ready.reason !== null && <p role="status">{ready.reason}</p>}
    </>
  );
}
