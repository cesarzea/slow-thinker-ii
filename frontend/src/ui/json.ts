import type {JsonObject, JsonValue} from '../api/index.ts';

export function isJsonObject(value: JsonValue | undefined): value is JsonObject {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/** JSON text with object keys sorted, so equal values have equal text. */
export function canonicalJson(value: unknown): string {
  return JSON.stringify(sortedKeys(value ?? null));
}

function sortedKeys(value: unknown): unknown {
  let sorted = value;
  if (Array.isArray(value)) sorted = value.map(sortedKeys);
  else if (typeof value === 'object' && value !== null) {
    const entries = Object.entries(value).sort(([a], [b]) => (a < b ? -1 : 1));
    sorted = Object.fromEntries(entries.map(([key, item]) => [key, sortedKeys(item)]));
  }
  return sorted;
}

function tokens(pointer: string): string[] {
  if (pointer === '') return [];
  return pointer
    .slice(1)
    .split('/')
    .map((token) => token.replaceAll('~1', '/').replaceAll('~0', '~'));
}

function child(value: JsonValue | undefined, token: string): JsonValue | undefined {
  if (Array.isArray(value)) return /^\d+$/u.test(token) ? value[Number(token)] : undefined;
  return isJsonObject(value) && Object.hasOwn(value, token) ? value[token] : undefined;
}

/** Read the value at a JSON Pointer; undefined when any step is missing. */
export function readPointer(value: JsonValue | undefined, pointer: string): JsonValue | undefined {
  return tokens(pointer).reduce<JsonValue | undefined>(child, value);
}

/** Return a copy of an object with the value at the pointer replaced; undefined removes it. */
export function writePointer(
  root: JsonObject,
  pointer: string,
  next: JsonValue | undefined,
): JsonObject {
  const [head, ...rest] = tokens(pointer);
  if (head === undefined) return isJsonObject(next) ? next : root;
  return writeTokens(root, head, rest, next);
}

function writeTokens(
  object: JsonObject,
  head: string,
  rest: readonly string[],
  next: JsonValue | undefined,
): JsonObject {
  const [nextHead, ...nextRest] = rest;
  const value =
    nextHead === undefined
      ? next
      : writeTokens(nestedObject(object[head]), nextHead, nextRest, next);
  const copy = {...object};
  if (value === undefined) Reflect.deleteProperty(copy, head);
  else copy[head] = value;
  return copy;
}

function nestedObject(value: JsonValue | undefined): JsonObject {
  return isJsonObject(value) ? value : {};
}

/** Find the JSON Schema describing the value at a configuration pointer. */
export function schemaAt(schema: JsonValue | undefined, pointer: string): JsonObject | undefined {
  let current: JsonValue | undefined = schema;
  for (const token of tokens(pointer)) {
    if (!isJsonObject(current)) return undefined;
    current = schemaChild(current, token);
  }
  return isJsonObject(current) ? current : undefined;
}

function schemaChild(schema: JsonObject, token: string): JsonValue | undefined {
  const items = /^\d+$/u.test(token) ? schema['items'] : undefined;
  return child(schema['properties'], token) ?? items;
}
