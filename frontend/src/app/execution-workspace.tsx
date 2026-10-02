import {useState} from 'react';
import type {ReactElement} from 'react';
import type {WorkspacePage} from './workspace-navigation.tsx';
import type {GraphReference, GraphSummary, ConfigurationCatalog} from '../api/index.ts';
import type {ExecutionObservation} from '../features/execution/index.ts';
import {Inspector} from '../features/inspector/index.ts';
import type {InspectionSelection} from '../features/inspector/index.ts';
import {ExperimentExecution} from './experiment-execution.tsx';
import {RunWorkspace} from './run-workspace.tsx';
import type {ExperimentReadiness} from './experiment-types.ts';
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
  readonly page?: WorkspacePage;
  readonly catalog?: ConfigurationCatalog | null;
}
export function ExecutionWorkspace(props: WorkspaceProps): ReactElement {
  const [observation, onObservation] = useState<ExecutionObservation>();
  const [inspection, inspect] = useState<Inspection>();
  const [readiness, onReadiness] = useState<ExperimentReadiness>();
  const onInspect = (run: string): void => {
    inspect({run});
  };
  return (
    <>
      <ExperimentExecution
        {...props}
        onSaved={props.onSaved ?? ignoreSaved}
        selectionBlocked={props.selectionBlocked ?? false}
        onObservation={onObservation}
        onInspect={onInspect}
        onReadiness={onReadiness}
        {...(observation === undefined ? {} : {observation})}
      />
      <RunPage
        {...props}
        {...{observation, inspection, readiness, inspect, onInspect, onObservation}}
      />
    </>
  );
}
function RunPage(
  props: WorkspaceProps &
    EvidenceProps & {
      readonly readiness: ExperimentReadiness | undefined;
      readonly onInspect: (run: string) => void;
      readonly onObservation: (state: ExecutionObservation) => void;
    },
): ReactElement {
  return (
    <div hidden={props.page !== 'Runs'}>
      <RunWorkspace {...props} />
      <EvidenceWorkspace {...props} />
    </div>
  );
}

function ignoreSaved(): undefined {
  return undefined;
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
    <aside className="technical-drawer" aria-label="Technical evidence">
      <button onClick={onClose}>Close inspector</button>
      <Inspector
        key={inspection.run}
        credential={credential}
        run={inspection.run}
        {...(inspection.selection === undefined ? {} : {selection: inspection.selection})}
      />
    </aside>
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
