import {useState} from 'react';
import type {ReactElement} from 'react';
import type {GraphReference, GraphSummary} from '../api/index.ts';
import type {ExecutionObservation} from '../features/execution/index.ts';
import {Inspector} from '../features/inspector/index.ts';
import type {InspectionSelection} from '../features/inspector/index.ts';
import {ExperimentExecution} from './experiment-execution.tsx';
import {LiveGraph} from './live-graph.tsx';

interface Inspection {
  readonly run: string;
  readonly selection?: InspectionSelection;
}
interface WorkspaceProps {
  readonly credential: string;
  readonly graph: GraphSummary;
  readonly onSaved?: (reference: GraphReference) => void;
  readonly selectionBlocked?: boolean;
}
export function ExecutionWorkspace({
  credential,
  graph,
  onSaved = () => undefined,
  selectionBlocked = false,
}: WorkspaceProps): ReactElement {
  const [observation, onObservation] = useState<ExecutionObservation>();
  const [inspection, inspect] = useState<Inspection>();
  return (
    <>
      <ExperimentExecution
        credential={credential}
        graph={graph}
        onSaved={onSaved}
        selectionBlocked={selectionBlocked}
        onObservation={onObservation}
        onInspect={(run) => {
          inspect({run});
        }}
      />
      <EvidenceWorkspace
        observation={observation}
        inspection={inspection}
        inspect={inspect}
        credential={credential}
      />
    </>
  );
}
function InspectionPanel({
  credential,
  inspection,
  onClose,
}: {
  readonly credential: string;
  readonly inspection: Inspection;
  readonly onClose: () => void;
}): ReactElement {
  return (
    <>
      <button onClick={onClose}>Close inspector</button>
      <Inspector
        key={inspection.run}
        credential={credential}
        run={inspection.run}
        {...(inspection.selection === undefined ? {} : {selection: inspection.selection})}
      />
    </>
  );
}

interface EvidenceProps {
  readonly observation: ExecutionObservation | undefined;
  readonly inspection: Inspection | undefined;
  readonly inspect: (value: Inspection | undefined) => void;
  readonly credential: string;
}
function EvidenceWorkspace({
  observation,
  inspection,
  inspect,
  credential,
}: EvidenceProps): ReactElement {
  return (
    <>
      {observation !== undefined && (
        <LiveGraph
          observation={observation}
          onInspect={(run, selection) => {
            inspect({run, selection});
          }}
        />
      )}
      {inspection !== undefined && (
        <InspectionPanel
          credential={credential}
          inspection={inspection}
          onClose={() => {
            inspect(undefined);
          }}
        />
      )}
    </>
  );
}
