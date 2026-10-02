import type {ReactElement} from 'react';
import {SourceFields, sourceString, pointerToken} from '../../ui/index.ts';
import {SchemaForm} from './schema-form.tsx';
import {ModelFields} from './model-fields.tsx';
import {BindingFields} from './binding-fields.tsx';
import {registeredType} from './source-config.ts';
import type {SourceField} from '../../ui/index.ts';
import type {ComponentFormProps} from './types.ts';
export function ComponentForm(props: ComponentFormProps): ReactElement {
  const descriptor = registeredType(props.catalog, props.component);
  const path = `/components/${pointerToken(props.id)}`;
  return (
    <section aria-label={`Configure component ${props.id}`}>
      <h3>{props.id}</h3>
      <p>
        {sourceString(props.component.entries.get('type_id'))} ·{' '}
        {sourceString(props.component.entries.get('type_version'))} ·{' '}
        {descriptor?.installation_status ?? 'Not registered'}
      </p>
      <SchemaForm
        {...props}
        schema={descriptor?.config_schema ?? {}}
        value={props.component.entries.get('config')}
        path={`${path}/config`}
      />
      <ModelFields {...props} path={path} />
      <BindingFields {...props} path={path} />
      <SourceFields
        fields={componentFields(props, path)}
        disabled={props.locked}
        patch={props.patch}
      />
    </section>
  );
}

function componentFields(props: ComponentFormProps, path: string): SourceField[] {
  return [
    {
      label: `${props.id} configuration JSON and extensions`,
      path: `${path}/config`,
      value: props.component.entries.get('config'),
    },
    {
      label: `${props.id} managed parent`,
      path: `${path}/contained_by`,
      value: props.component.entries.get('contained_by'),
    },
  ];
}
