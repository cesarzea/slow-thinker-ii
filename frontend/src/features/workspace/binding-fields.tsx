import type {ReactElement} from 'react';
import {JsonField, SchemaField, pointerToken, sourceString, sourceTree} from '../../ui/index.ts';
import type {ComponentFormProps} from './types.ts';
export function BindingFields(props: ComponentFormProps & {readonly path: string}): ReactElement {
  return (
    <fieldset disabled={props.locked}>
      <legend>Managed children and resources</legend>
      <p>
        Bindings do not grant permission. Add authorized operations explicitly in Graph permissions.
      </p>
      <DeclaredSlots {...props} />
      <JsonField
        label={`${props.id} resource bindings`}
        path={`${props.path}/resources`}
        raw={props.component.entries.get('resources')?.raw}
        disabled={props.locked}
        patch={props.patch}
      />
    </fieldset>
  );
}
function DeclaredSlots(props: ComponentFormProps & {readonly path: string}): ReactElement {
  const descriptor = props.catalog?.components.find(
    (item) =>
      item.type_id === sourceString(props.component.entries.get('type_id')) &&
      item.type_version === sourceString(props.component.entries.get('type_version')),
  );
  const instances = [
    ...(sourceTree(props.source)?.entries.get('components')?.entries.keys() ?? []),
  ];
  const resources = props.component.entries.get('resources');
  return (
    <>
      {Object.keys(descriptor?.resource_slots ?? {}).map((slot) => (
        <SchemaField
          schema={{type: 'string', enum: instances}}
          source={resources?.entries.get(slot)}
          key={slot}
          label={`Resource slot ${slot}`}
          path={`${props.path}/resources/${pointerToken(slot)}`}
          raw={resources?.entries.get(slot)?.raw}
          disabled={props.locked || resources === undefined}
          patch={props.patch}
        />
      ))}
    </>
  );
}
