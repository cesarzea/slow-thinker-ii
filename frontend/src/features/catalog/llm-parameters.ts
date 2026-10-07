import type {JsonObject, JsonValue} from '../../api/index.ts';
import {isJsonObject} from '../../ui/index.ts';

/** One parameter of an LLM's parameter schema. */
export interface ParameterRow {
  readonly name: string;
  readonly title: string;
  readonly range: string;
  readonly initial: string;
}

const numbers = new Intl.NumberFormat('en', {maximumFractionDigits: 20});

function valueText(value: JsonValue): string {
  if (typeof value === 'number') return numbers.format(value);
  return typeof value === 'string' ? value : JSON.stringify(value);
}

function numberText(value: JsonValue | undefined): string | null {
  return typeof value === 'number' ? numbers.format(value) : null;
}

function boundsText(property: JsonObject): string | null {
  const low = numberText(property['minimum']);
  const high = numberText(property['maximum']);
  if (low !== null && high !== null) return `${low}–${high}`;
  if (low !== null) return `At least ${low}`;
  return high === null ? null : `At most ${high}`;
}

/** The allowed values: the choices, the numeric bounds, or “—” when not declared. */
function rangeText(property: JsonObject): string {
  const choices = property['enum'];
  if (Array.isArray(choices)) return choices.map(valueText).join(', ');
  return boundsText(property) ?? (property['type'] === 'boolean' ? 'true or false' : '—');
}

/** The parameters of an LLM, in schema order, with title, range and default. */
export function parameterRows(schema: JsonObject): ParameterRow[] {
  const properties = schema['properties'];
  if (!isJsonObject(properties)) return [];
  return Object.entries(properties).flatMap(([name, property]) => {
    if (!isJsonObject(property)) return [];
    const title = property['title'];
    const initial = property['default'];
    return [
      {
        name,
        title: typeof title === 'string' ? title : name,
        range: rangeText(property),
        initial: initial === undefined ? '—' : valueText(initial),
      },
    ];
  });
}
