import type {ReactElement} from 'react';
import {JsonField, SourceFields, pointerToken} from '../../ui/index.ts';
import type {SourceValue} from '../../ui/index.ts';
import {SequenceOrder} from './sequence-order.tsx';
import {RouteEditor} from './route-editor.tsx';
import {controllerSource} from './source-config.ts';
import type {SourceWorkspaceProps} from './types.ts';
export function FlowEditor(props: SourceWorkspaceProps): ReactElement {
  const {id: controller, config, conditional} = controllerSource(props.source);
  const path = `/components/${pointerToken(controller)}/config`;
  return (
    <fieldset disabled={props.locked || config === undefined}>
      <legend>Sequence and conditional control</legend>
      <p>Controller: {controller || 'Choose a controller first'}</p>
      {conditional ? (
        <ConditionalFields {...props} path={path} config={config} />
      ) : (
        <SequenceOrder {...props} path={path} />
      )}
      <JsonField
        label="Controller configuration and extensions"
        path={path}
        raw={config?.raw}
        disabled={props.locked}
        patch={props.patch}
      />
    </fieldset>
  );
}
function ConditionalFields(
  props: SourceWorkspaceProps & {readonly path: string; readonly config: SourceValue | undefined},
): ReactElement {
  const fields = [
    {label: 'Entry node', path: `${props.path}/entry`, value: props.config?.entries.get('entry')},
    {
      label: 'Maximum activations',
      path: `${props.path}/max_activations`,
      value: props.config?.entries.get('max_activations'),
    },
  ];
  return (
    <>
      <SourceFields fields={fields} disabled={props.locked} patch={props.patch} />
      <RouteEditor {...props} />
    </>
  );
}
