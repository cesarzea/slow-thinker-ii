import type {ReactElement} from 'react';
import {resolveSchema, schemaObject} from './schema-resolution.ts';
import {SchemaField, pointerToken} from '../../ui/index.ts';
import type {SourceValue} from '../../ui/index.ts';
import type {SourceWorkspaceProps} from './types.ts';

export function SchemaForm(
  props: SourceWorkspaceProps & {
    readonly schema: Readonly<Record<string, unknown>>;
    readonly value: SourceValue | undefined;
    readonly path: string;
  },
): ReactElement {
  const resolved = resolveSchema(props.schema, props.catalog?.schema_documents ?? {});
  const properties = schemaObject(resolved['properties']);
  return (
    <div className="schema-fields">
      <SchemaHint properties={properties} />
      {Object.entries(properties).map(([name, schema]) => (
        <SchemaField
          key={JSON.stringify([props.path, name, props.value?.entries.get(name)?.raw])}
          label={name}
          path={`${props.path}/${pointerToken(name)}`}
          raw={props.value?.entries.get(name)?.raw}
          source={props.value?.entries.get(name)}
          schema={schemaObject(schema)}
          disabled={props.locked || props.value === undefined}
          patch={props.patch}
        />
      ))}
    </div>
  );
}

function SchemaHint({
  properties,
}: {
  readonly properties: Readonly<Record<string, unknown>>;
}): ReactElement | null {
  return Object.keys(properties).length === 0 ? (
    <p>Use the configuration JSON field for opaque options or schemas without individual fields.</p>
  ) : null;
}
