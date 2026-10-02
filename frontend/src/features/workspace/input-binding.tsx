import {useState} from 'react';
import type {ReactElement} from 'react';
import {ChoiceControl, TextControl, sourceTree, pointerToken} from '../../ui/index.ts';
import type {PatchOperation} from '../../api/index.ts';
import type {SourceWorkspaceProps} from './types.ts';
interface BindingState {
  readonly field: string;
  readonly source: string;
  readonly node: string;
  readonly pointer: string;
}
export function InputBinding(props: SourceWorkspaceProps & {readonly path: string}): ReactElement {
  const [state, update] = useState<BindingState>({
    field: '',
    source: 'run_input',
    node: '',
    pointer: '/problem',
  });
  const change =
    (name: keyof BindingState) =>
    (value: string): void => {
      update({...state, [name]: value});
    };
  const add = (): void => {
    void props.patch(bindingPatch(props.path, state));
  };
  return (
    <fieldset disabled={props.locked}>
      <legend>Add or replace input binding</legend>
      <BindingInputs {...props} state={state} change={change} />
      <button
        disabled={!state.field || (state.source === 'node_output' && !state.node)}
        onClick={add}
      >
        Apply input binding
      </button>
    </fieldset>
  );
}
function BindingInputs(
  props: SourceWorkspaceProps & {
    readonly state: BindingState;
    readonly change: (name: keyof BindingState) => (value: string) => void;
  },
): ReactElement {
  const choices = [
    {value: 'run_input', label: 'Run input'},
    {value: 'node_output', label: 'Completed node output'},
  ];
  return (
    <>
      <TextControl label="Input field" value={props.state.field} onValue={props.change('field')} />
      <ChoiceControl
        label="Input source"
        value={props.state.source}
        onValue={props.change('source')}
        choices={choices}
      />
      <NodeBindingSource {...props} />
      <TextControl
        label="JSON Pointer"
        value={props.state.pointer}
        onValue={props.change('pointer')}
      />
    </>
  );
}

function NodeBindingSource(
  props: SourceWorkspaceProps & {
    readonly state: BindingState;
    readonly change: (name: keyof BindingState) => (value: string) => void;
  },
): ReactElement | null {
  const nodes = [...(sourceTree(props.source)?.entries.get('nodes')?.entries.keys() ?? [])].map(
    (id) => ({value: id, label: id}),
  );
  if (props.state.source !== 'node_output') return null;
  return (
    <ChoiceControl
      label="Source node"
      value={props.state.node}
      onValue={props.change('node')}
      choices={[{value: '', label: 'Choose a node'}, ...nodes]}
    />
  );
}

function bindingPatch(path: string, state: BindingState): PatchOperation[] {
  const {field, source, node, pointer} = state;
  const value =
    source === 'run_input'
      ? {source, pointer}
      : {source, node, pointer, activation: 'latest_completed'};
  return [
    {op: 'add', path: `${path}/inputs/${pointerToken(field)}`, value_json: JSON.stringify(value)},
  ];
}
