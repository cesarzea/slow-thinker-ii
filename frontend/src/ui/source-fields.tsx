import type {ReactElement} from 'react';
import {JsonField} from './json-field.tsx';
import type {SourceFieldProps} from './json-field.tsx';
import type {SourceValue} from './json-source.ts';
export interface SourceField {
  readonly label: string;
  readonly path: string;
  readonly value: SourceValue | undefined;
}
export function SourceFields(props: {
  readonly fields: readonly SourceField[];
  readonly disabled: boolean;
  readonly patch: SourceFieldProps['patch'];
}): ReactElement {
  return (
    <>
      {props.fields.map((field) => (
        <JsonField
          key={field.path}
          label={field.label}
          path={field.path}
          raw={field.value?.raw}
          disabled={props.disabled}
          patch={props.patch}
        />
      ))}
    </>
  );
}
