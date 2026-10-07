import type {JsonObject, JsonValue} from '../api/index.ts';
import {canonicalJson, isJsonObject} from './json.ts';

export type PropertyType = 'string' | 'integer' | 'number' | 'boolean' | 'list';
export interface PropertyRow {
  readonly name: string;
  readonly type: PropertyType;
  readonly required: boolean;
  readonly minimum?: number | undefined;
  readonly maximum?: number | undefined;
}

export const propertyTypes: readonly {readonly value: PropertyType; readonly label: string}[] = [
  {value: 'string', label: 'Text'},
  {value: 'integer', label: 'Integer'},
  {value: 'number', label: 'Number'},
  {value: 'boolean', label: 'True or false'},
  {value: 'list', label: 'List of text'},
];

const SCHEMA_KEYS = new Set(['type', 'additionalProperties', 'properties', 'required']);
const NUMERIC_KEYS = new Set(['type', 'minimum', 'maximum']);
const SIMPLE: Readonly<Record<string, PropertyType>> = {
  '{"type":"string"}': 'string',
  '{"type":"boolean"}': 'boolean',
  '{"items":{"type":"string"},"type":"array"}': 'list',
};

export function isNumeric(type: PropertyType): boolean {
  return type === 'integer' || type === 'number';
}

/** Rows for an object schema with typed top-level properties; null when it is not editable here. */
export function rowsFromSchema(schema: JsonValue | undefined): PropertyRow[] | null {
  if (schema === undefined || schema === null) return [];
  if (!isJsonObject(schema) || !editableObject(schema)) return null;
  const properties = isJsonObject(schema['properties']) ? schema['properties'] : {};
  const required = requiredNames(schema['required'], properties);
  if (required === null) return null;
  const rows = Object.entries(properties).map(([name, property]) =>
    propertyRow(name, property, required.includes(name)),
  );
  return rows.every((row) => row !== null) ? rows : null;
}

function requiredNames(value: JsonValue | undefined, properties: JsonObject): string[] | null {
  const names = value ?? [];
  if (!Array.isArray(names)) return null;
  const known = names.filter(
    (name): name is string => typeof name === 'string' && Object.hasOwn(properties, name),
  );
  return known.length === names.length ? known : null;
}

function editableObject(schema: JsonObject): boolean {
  return (
    Object.keys(schema).every((key) => SCHEMA_KEYS.has(key)) &&
    schema['type'] === 'object' &&
    (schema['additionalProperties'] ?? false) === false &&
    (schema['properties'] === undefined || isJsonObject(schema['properties']))
  );
}

function propertyRow(
  name: string,
  schema: JsonValue | undefined,
  required: boolean,
): PropertyRow | null {
  if (!isJsonObject(schema)) return null;
  const type = schema['type'];
  if (type === 'integer' || type === 'number') return numericRow(name, schema, type, required);
  const simple = SIMPLE[canonicalJson(schema)];
  return simple === undefined ? null : {name, type: simple, required};
}

function numericRow(
  name: string,
  schema: JsonObject,
  type: 'integer' | 'number',
  required: boolean,
): PropertyRow | null {
  const {minimum, maximum} = schema;
  if (!Object.keys(schema).every((key) => NUMERIC_KEYS.has(key))) return null;
  if (!isBound(minimum) || !isBound(maximum)) return null;
  return {name, type, required, minimum, maximum};
}

function isBound(value: JsonValue | undefined): value is number | undefined {
  return value === undefined || typeof value === 'number';
}

/** The schema the editor generates; rows without a name, or repeating one, are left out. */
export function schemaFromRows(rows: readonly PropertyRow[]): JsonObject {
  const properties: JsonObject = {};
  const required: string[] = [];
  for (const row of rows) {
    if (row.name === '' || Object.hasOwn(properties, row.name)) continue;
    properties[row.name] = propertySchema(row);
    if (row.required) required.push(row.name);
  }
  return {type: 'object', additionalProperties: false, properties, required};
}

function propertySchema(row: PropertyRow): JsonObject {
  if (row.type === 'list') return {type: 'array', items: {type: 'string'}};
  if (!isNumeric(row.type)) return {type: row.type};
  return {
    type: row.type,
    ...(row.minimum === undefined ? {} : {minimum: row.minimum}),
    ...(row.maximum === undefined ? {} : {maximum: row.maximum}),
  };
}
