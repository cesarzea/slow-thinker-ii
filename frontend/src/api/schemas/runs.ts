import {z} from 'zod';
import {
  countSchema,
  decimalSchema,
  durationSchema,
  jsonValueSchema,
  timestampSchema,
} from './json.ts';

const runStatusSchema = z.enum([
  'starting',
  'running',
  'completed',
  'stopped',
  'failed',
  'cancelled',
]);
export const runReasonSchema = z.enum([
  'activation_limit',
  'time_limit',
  'budget_run',
  'budget_day',
  'budget_month',
  'startup_failed',
  'activation_failed',
  'interrupted',
  'internal_error',
  'cancelled',
]);

export const runTotalsSchema = z.strictObject({
  duration_ms: durationSchema,
  activations: countSchema,
  messages: countSchema,
  llm_calls: countSchema,
  input_tokens: countSchema,
  output_tokens: countSchema,
  cost_usd: decimalSchema,
});

const runSummaryShape = {
  run_id: z.string().min(1),
  graph_id: z.string().min(1),
  /** Null for a run of a change that was never activated. */
  version: z.number().int().positive().nullable(),
  /** The change the run executed. */
  change: z.number().int().positive(),
  status: runStatusSchema,
  reason: runReasonSchema.nullable(),
  detail: z.string().nullable(),
  created_at: timestampSchema,
  ended_at: timestampSchema.nullable(),
  totals: z.union([z.null(), runTotalsSchema, z.strictObject({}).transform(() => null)]),
};
const runSummarySchema = z.strictObject(runSummaryShape);

export const runListSchema = z.strictObject({runs: z.array(runSummarySchema)});
export const runDetailSchema = z.strictObject({
  ...runSummaryShape,
  results: z.array(
    z.strictObject({
      node_id: z.string(),
      name: z.string(),
      payload: jsonValueSchema,
      at: timestampSchema,
    }),
  ),
  activations_by_node: z.record(z.string(), countSchema),
  messages_by_connection: z.record(z.string(), countSchema),
});
export const startedSchema = z.strictObject({run_id: z.string().min(1)});
export const stoppedSchema = z.strictObject({status: runStatusSchema});

const usageScope = z.strictObject({
  key: z.string(),
  limit_usd: decimalSchema,
  used_usd: decimalSchema,
});
export const usageSchema = z.strictObject({day: usageScope, month: usageScope});

export type RunStatus = z.infer<typeof runStatusSchema>;
export type RunReason = z.infer<typeof runReasonSchema>;
export type RunTotals = z.infer<typeof runTotalsSchema>;
export type RunSummary = z.infer<typeof runSummarySchema>;
export type RunDetail = z.infer<typeof runDetailSchema>;
export type Usage = z.infer<typeof usageSchema>;
