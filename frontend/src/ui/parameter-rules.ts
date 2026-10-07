import {Ajv2020} from 'ajv/dist/2020.js';
import type {ValidateFunction} from 'ajv/dist/2020.js';
import type {JsonObject, JsonValue} from '../api/index.ts';
import {isJsonObject} from './json.ts';

const ajv = new Ajv2020({strict: false, validateSchema: false, allErrors: false});
const compiled = new WeakMap<JsonObject, ValidateFunction | null>();

function holds(condition: JsonValue | undefined, value: JsonObject): boolean {
  if (typeof condition === 'boolean') return condition;
  if (!isJsonObject(condition)) return true;
  if (!compiled.has(condition)) compiled.set(condition, compile(condition));
  const validate = compiled.get(condition);
  return validate === null || validate === undefined ? true : validate(value);
}

function compile(schema: JsonObject): ValidateFunction | null {
  try {
    return ajv.compile(schema);
  } catch {
    return null;
  }
}

function conditionals(schema: JsonObject): JsonObject[] {
  const all = Array.isArray(schema['allOf']) ? schema['allOf'] : [];
  return [schema, ...all.filter(isJsonObject)].filter((entry) => Object.hasOwn(entry, 'if'));
}

function branchProperties(conditional: JsonObject, value: JsonObject): JsonObject {
  const branch = holds(conditional['if'], value) ? conditional['then'] : conditional['else'];
  const properties = isJsonObject(branch) ? branch['properties'] : undefined;
  return isJsonObject(properties) ? properties : {};
}

/** Properties that the branch selected by an if/then/else sets to false for these values. */
export function disabledProperties(schema: JsonObject, value: JsonObject): ReadonlySet<string> {
  return new Set(
    conditionals(schema).flatMap((conditional) =>
      Object.entries(branchProperties(conditional, value))
        .filter(([, rule]) => rule === false)
        .map(([name]) => name),
    ),
  );
}

export function parameterProperties(schema: JsonObject): [string, JsonObject][] {
  const properties = schema['properties'];
  if (!isJsonObject(properties)) return [];
  return Object.entries(properties).filter((entry): entry is [string, JsonObject] =>
    isJsonObject(entry[1]),
  );
}

/** Remove values of properties that the current values make unavailable. */
export function withoutDisabled(schema: JsonObject, value: JsonObject): JsonObject {
  const disabled = disabledProperties(schema, value);
  return Object.fromEntries(Object.entries(value).filter(([name]) => !disabled.has(name)));
}

/** Parameter values for a new selection: every declared default that the rules allow. */
export function parameterDefaults(schema: JsonObject): JsonObject {
  const defaults: JsonObject = {};
  for (const [name, property] of parameterProperties(schema)) {
    const fallback = property['default'];
    if (fallback !== undefined) defaults[name] = fallback;
  }
  return withoutDisabled(schema, defaults);
}
