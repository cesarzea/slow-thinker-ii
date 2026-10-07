import type {Limits} from '../../../api/index.ts';

type LimitKey = keyof Limits;
export interface LimitField {
  readonly key: LimitKey;
  readonly label: string;
  /** Counts are whole numbers from 1; the budget is an amount in dollars. */
  readonly maximum: number | null;
}

/** The four run limits of a graph, in the order the inspector shows them. */
export const LIMIT_FIELDS: readonly LimitField[] = [
  {key: 'max_activations', label: 'Maximum activations', maximum: 10_000},
  {key: 'max_running_nodes', label: 'Maximum running nodes', maximum: 64},
  {key: 'time_limit_seconds', label: 'Time limit (s)', maximum: 86_400},
  {key: 'budget_usd', label: 'Budget per run ($)', maximum: null},
];

const BUDGET = /^(?:0|[1-9]\d{0,5})(?:\.\d{1,9})?$/u;

export type ParsedLimit =
  | {readonly value: number | string; readonly problem: null}
  | {readonly value: null; readonly problem: string};

function count(field: LimitField, maximum: number, text: string): ParsedLimit {
  const value = Number(text);
  if (text.trim() !== '' && Number.isInteger(value) && value >= 1 && value <= maximum)
    return {value, problem: null};
  const range = `from 1 to ${maximum.toLocaleString('en')}`;
  return {value: null, problem: `${field.label} must be a whole number ${range}.`};
}

/** The limit a field's text sets, or the problem with it. */
export function parseLimit(field: LimitField, text: string): ParsedLimit {
  if (field.maximum !== null) return count(field, field.maximum, text);
  const amount = text.trim();
  return BUDGET.test(amount) && Number(amount) > 0
    ? {value: amount, problem: null}
    : {
        value: null,
        problem:
          'Budget per run must be an amount in dollars greater than zero, with at most nine decimal places.',
      };
}

/** The problem with a graph name, or null: 1–120 characters, not only white space. */
export function graphNameProblem(name: string): string | null {
  const trimmed = name.trim();
  if (trimmed === '') return 'The graph needs a name.';
  return trimmed.length > 120 ? 'A graph name has at most 120 characters.' : null;
}
