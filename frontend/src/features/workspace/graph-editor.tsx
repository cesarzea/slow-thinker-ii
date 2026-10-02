import type {ReactElement} from 'react';
import {ChoiceControl, SourceFields, sourceTree, sourceString} from '../../ui/index.ts';
import {NodeEditor} from './node-editor.tsx';
import {PermissionEditor} from './permission-editor.tsx';
import {FlowEditor} from './flow-editor.tsx';
import type {SourceWorkspaceProps} from './types.ts';
export function GraphEditor(props: SourceWorkspaceProps): ReactElement {
  return (
    <section aria-label="Graph configuration">
      <h2>Graph configuration</h2>
      <GraphIdentityFields {...props} />
      <NodeEditor {...props} />
      <FlowEditor {...props} />
      <PermissionEditor {...props} />
      <ResultBinding {...props} />
    </section>
  );
}
function GraphIdentityFields(props: SourceWorkspaceProps): ReactElement {
  const root = sourceTree(props.source);
  const profile = sourceString(root?.entries.get('execution_profile')) || 'sequence';
  const fields = [
    {label: 'Run input schema', path: '/input_schema', value: root?.entries.get('input_schema')},
    {
      label: 'Controller component and operation',
      path: '/controller',
      value: root?.entries.get('controller'),
    },
  ];
  return (
    <>
      <ProfileChoice {...props} profile={profile} />
      <SourceFields fields={fields} disabled={props.locked} patch={props.patch} />
    </>
  );
}
function ProfileChoice(props: SourceWorkspaceProps & {readonly profile: string}): ReactElement {
  const choices =
    props.catalog?.supported_graph_profiles
      .filter((item) => ['sequence', 'bounded-conditional'].includes(item))
      .map((item) => ({value: item, label: item})) ?? [];
  const onValue = (value: string): void => {
    void props.patch([{op: 'add', path: '/execution_profile', value_json: JSON.stringify(value)}]);
  };
  return (
    <>
      <ChoiceControl
        label="Execution profile"
        value={props.profile}
        choices={choices}
        disabled={props.locked}
        onValue={onValue}
      />
      <p>
        Configure the matching controller and routes. Validation checks the complete profile before
        saving.
      </p>
    </>
  );
}
function ResultBinding(props: SourceWorkspaceProps): ReactElement {
  const root = sourceTree(props.source);
  return (
    <>
      <SourceFields
        fields={[
          {label: 'Final result binding', path: '/result', value: root?.entries.get('result')},
        ]}
        disabled={props.locked}
        patch={props.patch}
      />
      <p>
        Trusted limits policy: {sourceString(root?.entries.get('limits_profile')) || 'Not selected'}
        . Effective ceilings are configured in Settings.
      </p>
    </>
  );
}
