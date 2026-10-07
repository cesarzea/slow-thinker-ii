import {z} from 'zod';
import {
  countSchema,
  decimalSchema,
  durationSchema,
  jsonObjectSchema,
  jsonValueSchema,
} from './json.ts';
import {limitsSchema} from './graph.ts';
import {runReasonSchema, runTotalsSchema} from './runs.ts';

const endpoint = z.strictObject({node_id: z.string(), port: z.string()});
const failure = z.strictObject({
  code: z.string(),
  message: z.string(),
  type: z.string().optional(),
});
const position = z.enum(['node', 'output', 'memory']);

export const eventData = {
  'run.started': z.strictObject({
    graph_id: z.string(),
    graph_version: z.number().int().positive().nullable(),
    /** Absent from runs recorded before runs of changes. */
    graph_change: z.number().int().positive().optional(),
    input: jsonValueSchema,
    limits: limitsSchema,
    budgets: z.strictObject({
      run_usd: decimalSchema,
      day_usd: decimalSchema,
      month_usd: decimalSchema,
    }),
  }),
  'host.ready': z.strictObject({position, component: z.string(), startup_ms: durationSchema}),
  'host.failed': z.strictObject({position, component: z.string(), error: failure}),
  'run.running': z.strictObject({}),
  'message.sent': z.strictObject({
    message_id: z.string(),
    from: endpoint,
    to: endpoint,
    payload: jsonValueSchema,
  }),
  'message.discarded': z.strictObject({
    from: endpoint,
    reason: z.literal('no_connection'),
    payload: jsonValueSchema,
  }),
  'message.dropped': z.strictObject({
    message_id: z.string(),
    to: endpoint,
    reason: z.literal('run_ending'),
  }),
  'activation.started': z.strictObject({
    message_id: z.string().nullable(),
    number: z.number().int().positive(),
  }),
  'activation.completed': z.strictObject({
    emitted: z.array(z.strictObject({port: z.string(), message_ids: z.array(z.string())})),
    duration_ms: durationSchema,
  }),
  'activation.failed': z.strictObject({error: failure, duration_ms: durationSchema}),
  'activation.cancelled': z.strictObject({reason: z.string()}),
  'component.called': z.strictObject({
    position,
    component: z.string(),
    operation: z.string(),
    arguments: jsonValueSchema,
    result: jsonValueSchema.optional(),
    error: failure.optional(),
    duration_ms: durationSchema,
  }),
  'llm.called': z.strictObject({
    call_id: z.string(),
    llm: z.string().nullable(),
    provider_model: z.string().nullable(),
    request: jsonValueSchema,
    response: jsonObjectSchema.optional(),
    error: failure.nullable().optional(),
    usage: z
      .strictObject({
        input: countSchema,
        cached_input: countSchema,
        cache_write: countSchema,
        output: countSchema,
      })
      .nullable(),
    reserved_usd: decimalSchema,
    cost_usd: decimalSchema,
    estimated: z.boolean(),
    rates: z.record(z.string(), decimalSchema).nullable(),
    status: z.union([z.number().int(), z.string()]),
    duration_ms: durationSchema,
  }),
  report: z.strictObject({
    kind: z.enum(['step', 'progress', 'state', 'explanation', 'reasoning']),
    content: jsonValueSchema,
  }),
  'run.result': z.strictObject({
    name: z.string(),
    message_id: z.string(),
    payload: jsonValueSchema,
  }),
  'run.finished': z.strictObject({
    status: z.enum(['completed', 'stopped', 'failed', 'cancelled']),
    reason: runReasonSchema.nullable(),
    detail: z.string(),
    totals: runTotalsSchema,
    dropped: z.union([countSchema, z.array(z.string())]),
  }),
};
