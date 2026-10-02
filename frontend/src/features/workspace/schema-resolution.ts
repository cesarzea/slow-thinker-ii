import {z} from 'zod';

export function schemaObject(value: unknown): Record<string, unknown> {
  const result = z.record(z.string(), z.unknown()).safeParse(value);
  return result.success ? result.data : {};
}
export function resolveSchema(
  schema: Readonly<Record<string, unknown>>,
  documents: Readonly<Record<string, Readonly<Record<string, unknown>>>>,
  root: Readonly<Record<string, unknown>> = schema,
  depth = 0,
  budget = {remaining: 1000},
): Record<string, unknown> {
  if (schemaBound(depth, budget)) return {};
  const referenced = referencedSchema(schema['$ref'], documents, root);
  const base =
    referenced === null
      ? {}
      : resolveSchema(referenced.schema, documents, referenced.root, depth + 1, budget);
  let result = mergeSchema(base, schema);
  const alternatives = z.array(z.unknown()).safeParse(schema['allOf']);
  for (const part of alternatives.success ? alternatives.data : []) {
    result = mergeSchema(
      result,
      resolveSchema(schemaObject(part), documents, root, depth + 1, budget),
    );
  }
  const properties = schemaObject(result['properties']);
  result['properties'] = Object.fromEntries(
    Object.entries(properties).map(([key, value]) => [
      key,
      resolveSchema(schemaObject(value), documents, referenced?.root ?? root, depth + 1, budget),
    ]),
  );
  return result;
}
function referencedSchema(
  value: unknown,
  documents: Readonly<Record<string, Readonly<Record<string, unknown>>>>,
  root: Readonly<Record<string, unknown>>,
): {
  readonly schema: Record<string, unknown>;
  readonly root: Readonly<Record<string, unknown>>;
} | null {
  if (typeof value !== 'string') return null;
  const separator = value.indexOf('#');
  const urn = separator === -1 ? value : value.slice(0, separator);
  const fragment = separator === -1 ? '' : value.slice(separator + 1);
  const document = urn === '' ? root : documents[urn];
  if (document === undefined || (fragment !== '' && !fragment.startsWith('/'))) return null;
  return {schema: fragmentSchema(document, fragment), root: document};
}
function fragmentSchema(
  document: Readonly<Record<string, unknown>>,
  fragment: string,
): Record<string, unknown> {
  let current: unknown = document;
  for (const token of fragment === '' ? [] : fragment.slice(1).split('/')) {
    current = schemaObject(current)[token.replaceAll('~1', '/').replaceAll('~0', '~')];
  }
  return schemaObject(current);
}

function mergeSchema(
  left: Readonly<Record<string, unknown>>,
  right: Readonly<Record<string, unknown>>,
): Record<string, unknown> {
  return {
    ...left,
    ...right,
    properties: {...schemaObject(left['properties']), ...schemaObject(right['properties'])},
  };
}

function schemaBound(depth: number, budget: {remaining: number}): boolean {
  return depth > 20 || budget.remaining-- <= 0;
}
