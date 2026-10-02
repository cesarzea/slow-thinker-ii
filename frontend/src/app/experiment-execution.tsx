import type {ReactElement} from 'react';
import {DefinitionSession} from '../features/definition-editor/index.tsx';
import {useGraphDetail} from './use-graph-detail.ts';
import {AuthoringWorkspace} from './authoring-workspace.tsx';
import type {ExperimentExecutionProps} from './experiment-types.ts';
export function ExperimentExecution(props: ExperimentExecutionProps): ReactElement {
  const {detail, error} = useGraphDetail(props.graph, props.credential);
  return (
    <DefinitionSession
      credential={props.credential}
      reference={props.graph}
      onSaved={props.onSaved}
      onDirtyChange={ignoreDirty}
    >
      {(model) => <AuthoringWorkspace {...props} model={model} detail={detail} error={error} />}
    </DefinitionSession>
  );
}
function ignoreDirty(): undefined {
  return undefined;
}
