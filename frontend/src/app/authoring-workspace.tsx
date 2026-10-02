import {useState} from 'react';
import type {ReactElement} from 'react';
import type {ExecutionObservation} from '../features/execution/index.ts';
import type {GraphDetail} from '../api/index.ts';
import {DefinitionEditorView, definitionLocked} from '../features/definition-editor/index.tsx';
import type {EditorModel} from '../features/definition-editor/index.tsx';
import {ResourceInventory, StructuredWorkspace} from '../features/workspace/index.tsx';
import {DefinitionGraph} from './graph-workspace.tsx';
import {useReadiness} from './use-readiness.ts';
import {referenceKey} from './catalog-state.ts';
import type {ExperimentExecutionProps} from './experiment-types.ts';
interface Props extends ExperimentExecutionProps {
  readonly model: EditorModel;
  readonly detail: GraphDetail | null;
  readonly error: string | null;
}
export function AuthoringWorkspace(props: Props): ReactElement {
  const {page = 'Experiments'} = props;
  useReadiness(props);
  return (
    <>
      <div hidden={page !== 'Experiments'}>
        <DefinitionGraph
          key={referenceKey(props.graph)}
          graph={props.graph}
          detail={props.detail}
          error={props.error}
        />
        <DefinitionEditing {...props} />
      </div>
      <div hidden={page !== 'Resources'}>
        <ResourcePage {...props} />
      </div>
    </>
  );
}
function ResourcePage(props: Props): ReactElement {
  const observation = props.observation;
  const run = observationRun(observation);
  return (
    <ResourceInventory
      source={props.model.state.source}
      catalog={props.catalog ?? null}
      detail={props.detail}
      activityDetail={props.observation?.detail ?? null}
      execution={props.observation?.execution ?? null}
      run={run}
    />
  );
}
function DefinitionEditing(props: Props): ReactElement {
  const [mode, select] = useState('forms');
  const {model} = props;
  return (
    <>
      <EditingMode mode={mode} select={select} />
      <DefinitionEditorView model={model} reference={props.graph} sourceVisible={mode === 'json'} />
      <div hidden={mode !== 'forms'}>
        <StructuredWorkspace
          source={model.state.source}
          locked={definitionLocked(model.state)}
          catalog={props.catalog ?? null}
          patch={model.patch}
        />
      </div>
    </>
  );
}
function EditingMode({
  mode,
  select,
}: {
  readonly mode: string;
  readonly select: (mode: string) => void;
}): ReactElement {
  return (
    <div className="actions" aria-label="Definition editing mode">
      <button
        aria-pressed={mode === 'forms'}
        onClick={() => {
          select('forms');
        }}
      >
        Structured forms
      </button>
      <button
        aria-pressed={mode === 'json'}
        onClick={() => {
          select('json');
        }}
      >
        JSON source
      </button>
    </div>
  );
}

function observationRun(observation: ExecutionObservation | undefined): string | null {
  return observation?.run?.run_id ?? null;
}
