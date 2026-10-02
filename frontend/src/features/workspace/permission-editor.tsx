import {useState} from 'react';
import type {ReactElement} from 'react';
import {JsonField, TextControl, sourceTree} from '../../ui/index.ts';
import type {SourceValue} from '../../ui/index.ts';
import type {SourceWorkspaceProps} from './types.ts';
export function PermissionEditor(props: SourceWorkspaceProps): ReactElement {
  const [caller, setCaller] = useState('');
  const [target, setTarget] = useState('');
  const [operation, setOperation] = useState('');
  const permissions = sourceTree(props.source)?.entries.get('permissions');
  const grant = (): void => {
    const value = JSON.stringify({caller, target, operations: [operation]});
    void props.patch(
      permissions === undefined
        ? [{op: 'add', path: '/permissions', value_json: `[${value}]`}]
        : [{op: 'add', path: '/permissions/-', value_json: value}],
    );
  };
  return (
    <fieldset disabled={props.locked}>
      <legend>Graph permissions</legend>
      <p>
        Each grant is an intentional authorization. Binding a child or resource alone grants
        nothing.
      </p>
      <PermissionInputs {...{caller, target, operation, setCaller, setTarget, setOperation}} />
      <button disabled={!caller || !target || !operation} onClick={grant}>
        Grant declared operation
      </button>
      <PermissionJson {...props} permissions={permissions} />
    </fieldset>
  );
}

function PermissionInputs(props: {
  readonly caller: string;
  readonly target: string;
  readonly operation: string;
  readonly setCaller: (value: string) => void;
  readonly setTarget: (value: string) => void;
  readonly setOperation: (value: string) => void;
}): ReactElement {
  return (
    <>
      <TextControl label="Authorized caller" value={props.caller} onValue={props.setCaller} />
      <TextControl label="Authorized target" value={props.target} onValue={props.setTarget} />
      <TextControl
        label="Authorized operation"
        value={props.operation}
        onValue={props.setOperation}
      />
    </>
  );
}

function PermissionJson(
  props: SourceWorkspaceProps & {readonly permissions: SourceValue | undefined},
): ReactElement {
  return (
    <JsonField
      label="Permission grants"
      path="/permissions"
      raw={props.permissions?.raw}
      disabled={props.locked}
      patch={props.patch}
    />
  );
}
