import {useState} from 'react';
import type {ReactElement} from 'react';
import type {SourceFieldProps} from './json-field.tsx';
import {JsonField} from './json-field.tsx';
import type {SourceValue} from './json-source.ts';
import {sourceString} from './json-source.ts';

export interface SchemaFieldProps extends SourceFieldProps {
  readonly schema: Readonly<Record<string, unknown>>;
  readonly source: SourceValue | undefined;
}

export function SchemaField(props: SchemaFieldProps): ReactElement {
  if (props.schema['type'] !== 'string' && props.schema['type'] !== 'boolean')
    return <JsonField {...props} />;
  return <SimpleField key={props.raw ?? 'missing'} {...props} />;
}

function SimpleField(props: SchemaFieldProps): ReactElement {
  const boolean = props.schema['type'] === 'boolean';
  const [value, setValue] = useState(boolean ? props.raw === 'true' : sourceString(props.source));
  const options = Array.isArray(props.schema['enum'])
    ? props.schema['enum'].filter((item): item is string => typeof item === 'string')
    : [];
  const apply = (): void => {
    void props.patch([
      {
        op: props.raw === undefined ? 'add' : 'replace',
        path: props.path,
        value_json: JSON.stringify(value),
      },
    ]);
  };
  return (
    <div className="form-field">
      <label>
        {props.label}
        <SimpleInput {...{boolean, value, setValue, options}} disabled={props.disabled} />
      </label>
      <button disabled={props.disabled} onClick={apply}>
        Apply {props.label}
      </button>
    </div>
  );
}

interface InputProps {
  readonly boolean: boolean;
  readonly value: string | boolean;
  readonly setValue: (value: string | boolean) => void;
  readonly options: readonly string[];
  readonly disabled: boolean;
}
function SimpleInput(props: InputProps): ReactElement {
  if (props.boolean)
    return (
      <input
        type="checkbox"
        checked={props.value === true}
        disabled={props.disabled}
        onChange={(event) => {
          props.setValue(event.target.checked);
        }}
      />
    );
  if (props.options.length > 0) return <OptionInput {...props} />;
  return (
    <textarea
      rows={3}
      value={String(props.value)}
      disabled={props.disabled}
      onChange={(event) => {
        props.setValue(event.target.value);
      }}
    />
  );
}
function OptionInput(props: InputProps): ReactElement {
  return (
    <select
      value={String(props.value)}
      disabled={props.disabled}
      onChange={(event) => {
        props.setValue(event.target.value);
      }}
    >
      <option value="">Choose a value</option>
      {props.options.map((option) => (
        <option key={option}>{option}</option>
      ))}
    </select>
  );
}
