import type {JsonObject, JsonValue} from '../api/index.ts';
import {parameterProperties} from './parameter-rules.ts';
import {boundsText} from './presentation.ts';

/** Required parameters first, then the others, each group in the schema's order. */
export function orderedParameters(schema: JsonObject): [string, JsonObject][] {
  const required = Array.isArray(schema['required']) ? schema['required'] : [];
  const all = parameterProperties(schema);
  return [
    ...all.filter(([name]) => required.includes(name)),
    ...all.filter(([name]) => !required.includes(name)),
  ];
}

/** The help under a parameter's label: its bounds, then its description. */
export function parameterHelp(schema: JsonObject): string | undefined {
  const {minimum, maximum, description} = schema;
  const bounds = boundsText(
    typeof minimum === 'number' ? minimum : undefined,
    typeof maximum === 'number' ? maximum : undefined,
  );
  const parts = [bounds, typeof description === 'string' ? description : undefined];
  const help = parts.filter((part) => part !== undefined).join('; ');
  return help === '' ? undefined : help;
}

const KINDS: Readonly<Record<string, string>> = {
  integer: 'field-number width-sm align-end',
  number: 'field-number width-sm align-end',
  boolean: 'field-boolean width-md align-start',
};

/** The field classes of a parameter, with the declaration's defaults for its control. */
export function parameterClass(schema: JsonObject): string {
  if (Array.isArray(schema['enum'])) return 'field-choice width-md align-start';
  const type = typeof schema['type'] === 'string' ? schema['type'] : '';
  return KINDS[type] ?? 'field-text width-lg align-start';
}

export function numericBounds(
  schema: JsonObject,
  integer: boolean,
): {integer: boolean; minimum?: number; maximum?: number; placeholder?: string} {
  const {minimum, maximum} = schema;
  const fallback = schema['default'];
  return {
    integer,
    ...(typeof minimum === 'number' ? {minimum} : {}),
    ...(typeof maximum === 'number' ? {maximum} : {}),
    ...(typeof fallback === 'number' ? {placeholder: String(fallback)} : {}),
  };
}

export function scalarText(value: JsonValue): string {
  return typeof value === 'object' ? JSON.stringify(value) : String(value);
}
