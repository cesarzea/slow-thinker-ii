import type {JsonValue, LlmEntry, UiField} from '../api/index.ts';
import {isJsonObject, readPointer} from './json.ts';
import {parameterProperties} from './parameter-rules.ts';
import {formatNumber} from './presentation.ts';
import {serviceSelection} from './service-control.tsx';

export const NOT_SET = 'Not set';
const PREVIEW_LENGTH = 120;

type Summarizer = (field: UiField, value: JsonValue, services: readonly LlmEntry[]) => string;

/** Plain text of at most 120 characters, with runs of white space collapsed. */
export function textPreview(value: string): string {
  const text = value.replaceAll(/\s+/gu, ' ').trim();
  if (text === '') return NOT_SET;
  return text.length > PREVIEW_LENGTH ? `${text.slice(0, PREVIEW_LENGTH - 1)}…` : text;
}

/** A short readable form of any JSON value. */
export function jsonPreview(value: JsonValue | undefined): string {
  if (value === undefined || value === null) return NOT_SET;
  return typeof value === 'string' ? textPreview(value) : textPreview(JSON.stringify(value));
}

const summarizers: Readonly<Record<UiField['control'], Summarizer>> = {
  text: (_field, value) => jsonPreview(value),
  multiline: (_field, value) => jsonPreview(value),
  number: (field, value) =>
    typeof value === 'number' ? formatNumber(value, field.format) : jsonPreview(value),
  choice: (field, value) =>
    field.options?.find((option) => option.value === value)?.label ?? jsonPreview(value),
  list: (_field, value) =>
    Array.isArray(value) && value.length > 0 ? value.map(String).join(', ') : NOT_SET,
  code: (_field, value) => lineCount(value),
  schema: () => 'JSON schema',
  service: (_field, value, services) => serviceSummary(value, services),
};

/** The summary-card text of one field's value, following the declaration's summary rules. */
export function summaryValue(
  field: UiField,
  value: JsonValue | undefined,
  services: readonly LlmEntry[],
): string {
  if (value === null && field.control === 'schema') return field.empty_label ?? NOT_SET;
  if (value === undefined || value === null) return NOT_SET;
  return summarizers[field.control](field, value, services);
}

/** The one-line form of a field's value: an LLM by its label, a schema by its properties. */
export function previewValue(
  field: UiField,
  value: JsonValue | undefined,
  services: readonly LlmEntry[],
): string {
  if (field.control === 'service') {
    const selection = serviceSelection(value);
    const entry = services.find((item) => item.id === selection?.llm);
    return entry?.label ?? summaryValue(field, value, services);
  }
  if (field.control === 'schema' && isJsonObject(value) && isJsonObject(value['properties'])) {
    const count = Object.keys(value['properties']).length;
    return count === 1 ? '1 property' : `${String(count)} properties`;
  }
  return summaryValue(field, value, services);
}

/** Whether a field's `when` condition holds for this configuration. */
export function fieldVisible(field: UiField, config: JsonValue): boolean {
  return field.when === undefined || readPointer(config, field.when.path) === field.when.equals;
}

function lineCount(value: JsonValue): string {
  if (typeof value !== 'string' || value === '') return NOT_SET;
  const lines = value.replace(/\n$/u, '').split('\n').length;
  return lines === 1 ? '1 line' : `${String(lines)} lines`;
}

function serviceSummary(value: JsonValue, services: readonly LlmEntry[]): string {
  const selection = serviceSelection(value);
  if (selection === null) return NOT_SET;
  const entry = services.find((item) => item.id === selection.llm);
  if (entry === undefined) return `${selection.llm} (not available)`;
  const parameters = parameterProperties(entry.parameters).flatMap(([name, schema]) => {
    const parameter = selection.parameters[name];
    if (parameter === undefined) return [];
    const title = typeof schema['title'] === 'string' ? schema['title'] : name;
    return [`${title} ${typeof parameter === 'string' ? parameter : JSON.stringify(parameter)}`];
  });
  return [entry.label, ...parameters].join(' · ');
}
