import {useMemo, useState} from 'react';
import type {ReactElement, ReactNode} from 'react';
import {compileInput, inputError} from './input-schema.ts';
import {formValue, InputFieldControl, simpleFields} from './input-fields.tsx';

interface Props {
  readonly schema: Readonly<Record<string, unknown>>;
  readonly children: (value: unknown, valid: boolean) => ReactNode;
}
export function RunInput({schema, children}: Props): ReactElement {
  const fields = useMemo(() => simpleFields(schema), [schema]);
  const validation = useMemo(() => compileInput(schema), [schema]);
  const [values, setValues] = useState<Readonly<Record<string, string>>>({});
  const [json, setJson] = useState('{}');
  const input =
    fields === null ? parseInput(json) : {value: formValue(fields, values), error: null};
  const error = input.error ?? inputError(validation, input.value);
  return (
    <>
      {fields === null ? (
        <JsonInput value={json} onChange={setJson} />
      ) : (
        fields.map((field) => (
          <InputFieldControl
            key={field.name}
            field={field}
            value={values[field.name] ?? ''}
            onChange={(value) => {
              setValues({...values, [field.name]: value});
            }}
          />
        ))
      )}
      {error !== null && <p role="status">{error}</p>}
      {children(input.value, error === null)}
    </>
  );
}
function JsonInput({
  value,
  onChange,
}: {
  readonly value: string;
  readonly onChange: (value: string) => void;
}): ReactElement {
  return (
    <label>
      Entrada JSON
      <textarea
        value={value}
        rows={8}
        onChange={(event) => {
          onChange(event.target.value);
        }}
      />
    </label>
  );
}
function parseInput(text: string): {value: unknown; error: string | null} {
  try {
    const value: unknown = JSON.parse(text);
    return {value, error: null};
  } catch {
    return {value: undefined, error: 'Escribe una entrada JSON válida.'};
  }
}
