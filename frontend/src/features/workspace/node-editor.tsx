import {useState} from 'react';
import type {ReactElement} from 'react';
import {
  ChoiceControl,
  TextControl,
  SourceFields,
  SchemaField,
  sourceTree,
  pointerToken,
  sourceString,
} from '../../ui/index.ts';
import type {SourceValue} from '../../ui/index.ts';
import {registeredType} from './source-config.ts';
import {InputBinding} from './input-binding.tsx';
import type {SourceWorkspaceProps} from './types.ts';
interface NodeProps extends SourceWorkspaceProps {
  readonly id: string;
  readonly node: SourceValue;
}
export function NodeEditor(props: SourceWorkspaceProps): ReactElement {
  const nodes = sourceTree(props.source)?.entries.get('nodes');
  const [selected, select] = useState('');
  const ids = [...(nodes?.entries.keys() ?? [])];
  const id = ids.includes(selected) ? selected : (ids[0] ?? '');
  const node = nodes?.entries.get(id);
  return (
    <fieldset disabled={props.locked}>
      <legend>Declared nodes</legend>
      <ChoiceControl
        label="Node"
        value={id}
        onValue={select}
        choices={ids.map((item) => ({value: item, label: item}))}
      />
      {node !== undefined && <NodeFields key={id} {...props} id={id} node={node} />}
      <NewNode {...props} />
    </fieldset>
  );
}
function NodeFields(props: NodeProps): ReactElement {
  const path = `/nodes/${pointerToken(props.id)}`;
  const fields = [
    {
      label: 'Node input bindings JSON',
      path: `${path}/inputs`,
      value: props.node.entries.get('inputs'),
    },
    {label: 'Node output port', path: `${path}/output`, value: props.node.entries.get('output')},
  ];
  return (
    <>
      <NodeTargets {...props} path={path} />
      <SourceFields fields={fields} disabled={props.locked} patch={props.patch} />
      <InputBinding {...props} path={path} />
      <button
        onClick={() => {
          void props.patch([{op: 'remove', path}]);
        }}
      >
        Remove node {props.id}
      </button>
    </>
  );
}
function NodeTargets(props: NodeProps & {readonly path: string}): ReactElement {
  const components = sourceTree(props.source)?.entries.get('components');
  const component = components?.entries.get(sourceString(props.node.entries.get('component')));
  const descriptor = registeredType(props.catalog, component);
  const fields = [
    {name: 'component', label: 'Node component', options: [...(components?.entries.keys() ?? [])]},
    {
      name: 'operation',
      label: 'Node operation',
      options: Object.keys(descriptor?.operations ?? {}),
    },
  ];
  return (
    <>
      {fields.map((field) => (
        <SchemaField
          key={field.name}
          label={field.label}
          schema={{type: 'string', enum: field.options}}
          path={`${props.path}/${field.name}`}
          raw={props.node.entries.get(field.name)?.raw}
          source={props.node.entries.get(field.name)}
          disabled={props.locked}
          patch={props.patch}
        />
      ))}
    </>
  );
}
function NewNode(props: SourceWorkspaceProps): ReactElement {
  const [id, setId] = useState('');
  const nodes = sourceTree(props.source)?.entries.get('nodes');
  const add = (): void => {
    void props.patch([
      {
        op: 'add',
        path: `/nodes/${pointerToken(id)}`,
        value_json: '{"component":"","operation":"","inputs":{}}',
      },
    ]);
  };
  return (
    <div>
      <TextControl label="New node ID" value={id} onValue={setId} />
      <button disabled={!id || nodes === undefined || nodes.entries.has(id)} onClick={add}>
        Add node
      </button>
    </div>
  );
}
