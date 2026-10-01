import type {ReactElement} from 'react';
import {objectRecord} from './input-schema.ts';

export interface InputField {
  readonly name: string;
  readonly type: 'string' | 'number' | 'integer' | 'boolean';
  readonly title: string;
  readonly required: boolean;
}
export function simpleFields(schema: Readonly<Record<string, unknown>>): InputField[] | null {
  const properties = objectRecord(schema['properties']);
  if (schema['type'] !== 'object' || properties === null) return null;
  const required = schema['required'];
  const fields = Object.entries(properties).map(([name, value]): InputField | null => {
    const property = objectRecord(value);
    const type = property?.['type'];
    if (type !== 'string' && type !== 'number' && type !== 'integer' && type !== 'boolean')
      return null;
    return {
      name,
      type,
      title: fieldTitle(name, property?.['title']),
      required: Array.isArray(required) && required.includes(name),
    };
  });
  return fields.every((field) => field !== null) ? fields : null;
}
function fieldTitle(name: string, title: unknown): string {
  if (typeof title === 'string') return title;
  return name === 'problem' ? 'Task or problem' : name;
}
export function formValue(fields: InputField[], values: Readonly<Record<string, string>>): unknown {
  return Object.fromEntries(
    fields.flatMap((field) => {
      const text = values[field.name] ?? '';
      if (text === '' && !field.required) return [];
      return [[field.name, fieldValue(field.type, text)]];
    }),
  );
}
function fieldValue(type: InputField['type'], text: string): unknown {
  if (type === 'string') return text;
  if (text === '') return undefined;
  return type === 'boolean' ? text === 'true' : Number(text);
}
interface FieldProps {
  readonly field: InputField;
  readonly value: string;
  readonly onChange: (value: string) => void;
}
export function InputFieldControl({field, value, onChange}: FieldProps): ReactElement {
  return (
    <label>
      {field.title}
      {field.required && ' (required)'}
      {field.type === 'boolean' ? (
        <select
          value={value}
          onChange={(event) => {
            onChange(event.target.value);
          }}
        >
          <option value="">Select</option>
          <option value="true">Yes</option>
          <option value="false">No</option>
        </select>
      ) : (
        <textarea
          value={value}
          rows={field.type === 'string' ? 3 : 1}
          onChange={(event) => {
            onChange(event.target.value);
          }}
        />
      )}
    </label>
  );
}
