import type {GraphDetail} from '../../api/index.ts';
import type {ConfigurationValue} from './types.ts';

type RecordValue = Readonly<Record<string, unknown>>;
export function record(value: unknown): RecordValue {
  return isRecord(value) ? value : {};
}
function isRecord(value: unknown): value is RecordValue {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
export function textValue(value: unknown): string | undefined {
  return typeof value === 'string' && value.trim().length > 0 ? value : undefined;
}
export function definitionComponent(detail: GraphDetail | undefined, id: string): RecordValue {
  return record(record(detail?.definition['components'])[id]);
}
function savedInstance(detail: GraphDetail | undefined, id: string): RecordValue {
  return record(record(detail?.execution?.['instances'])[id]);
}
export function componentConfiguration(
  detail: GraphDetail | undefined,
  id: string,
): {config: RecordValue; source: ConfigurationValue['source']} {
  const saved = savedInstance(detail, id)['config'];
  const hasSaved = typeof saved === 'object' && saved !== null && !Array.isArray(saved);
  return hasSaved
    ? {config: record(saved), source: 'Saved configuration'}
    : {config: record(definitionComponent(detail, id)['config']), source: 'Graph configuration'};
}
export function resourceTarget(
  detail: GraphDetail | undefined,
  id: string,
  slot: string,
): string | undefined {
  return textValue(record(definitionComponent(detail, id)['resources'])[slot]);
}
export function enforcedEffort(detail: GraphDetail | undefined, id: string): string | undefined {
  const operations = savedInstance(detail, id)['operations'];
  if (!Array.isArray(operations)) return undefined;
  const values = operations.map((operation: unknown) => operationEffort(operation));
  const explicit = [...new Set(values.filter((value) => value !== undefined))];
  return explicit.length === 1 ? explicit[0] : undefined;
}
function operationEffort(operation: unknown): string | undefined {
  if (record(operation)['name'] !== 'complete') return undefined;
  const schema = record(record(operation)['input_schema']);
  const request = record(record(schema['properties'])['request']);
  const effort = record(record(request['properties'])['reasoning_effort']);
  return textValue(effort['const']);
}
