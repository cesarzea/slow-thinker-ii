import {useState} from 'react';
import type {ReactElement} from 'react';
import {ChoiceControl, TextControl, pointerToken, sourceTree} from '../../ui/index.ts';
import type {InstalledType} from '../../api/index.ts';
import type {SourceWorkspaceProps} from './types.ts';
export function NewInstance(props: SourceWorkspaceProps): ReactElement {
  const [name, setName] = useState('');
  const [type, setType] = useState('');
  const descriptor = props.catalog?.components.find(
    (item) => JSON.stringify([item.type_id, item.type_version]) === type,
  );
  const components = sourceTree(props.source)?.entries.get('components');
  const add = (): void => {
    if (descriptor === undefined) return;
    const instance = emptyInstance(descriptor);
    void props.patch([
      {op: 'add', path: `/components/${pointerToken(name)}`, value_json: JSON.stringify(instance)},
    ]);
  };
  return (
    <fieldset disabled={props.locked || components === undefined}>
      <legend>Add registered component</legend>
      <TextControl label="New component name" value={name} onValue={setName} />
      <TypeChoice {...props} type={type} setType={setType} />
      <button
        disabled={descriptor === undefined || !name || components?.entries.has(name)}
        onClick={add}
      >
        Add component instance
      </button>
    </fieldset>
  );
}
function TypeChoice(
  props: SourceWorkspaceProps & {readonly type: string; readonly setType: (type: string) => void},
): ReactElement {
  const choices =
    props.catalog?.components.map((item) => ({
      value: JSON.stringify([item.type_id, item.type_version]),
      label: `${item.type_id} · ${item.type_version} · ${item.installation_status}`,
      disabled: item.installation_status !== 'ready',
    })) ?? [];
  return (
    <ChoiceControl
      label="Registered component type"
      value={props.type}
      onValue={props.setType}
      choices={[{value: '', label: 'Choose a type'}, ...choices]}
    />
  );
}

function emptyInstance(type: InstalledType): Record<string, unknown> {
  return {type_id: type.type_id, type_version: type.type_version, config: {}, resources: {}};
}
