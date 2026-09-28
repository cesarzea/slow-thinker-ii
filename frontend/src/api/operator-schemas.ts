import {z} from 'zod';

const budgetSchema = z.object({
  currency: z.literal('USD'),
  cap: z.string(),
  settled: z.string(),
  outstanding: z.string(),
  available: z.string(),
});
const sessionSchema = z.object({
  session_id: z.string(),
  name: z.string(),
  created_at: z.number(),
});
export const workspaceSchema = z.object({
  backend_generation: z.string(),
  configuration_revision: z.string().nullable(),
  admission_available: z.boolean(),
  admission_reason: z.string().nullable(),
  blocking_run_id: z.string().nullable(),
  month_budget: budgetSchema,
  sessions: z.object({items: z.array(sessionSchema), next_cursor: z.string().nullable()}),
});
export const receiptSchema = z.object({
  command_id: z.string(),
  kind: z.enum(['session', 'start', 'stop']),
  disposition: z.enum(['accepted', 'rejected', 'already_terminal', 'withdrawn']),
  target_id: z.string().nullable(),
  reason: z.string().nullable(),
});
export const runSchema = z.object({
  run_id: z.string(),
  session_id: z.string(),
  graph_id: z.string().nullable(),
  graph_revision: z.string(),
  state: z.enum([
    'created',
    'running',
    'stopping',
    'completed',
    'failed',
    'cancelled',
    'timed_out',
    'interrupted',
  ]),
  reason: z.string().nullable(),
  cleanup: z.enum(['confirmed', 'unconfirmed']),
  last_event_sequence: z.number().int().nonnegative(),
  backend_generation: z.string(),
  budget: budgetSchema,
  session_budget: budgetSchema,
  admission_month_budget: budgetSchema,
  calls: z.record(z.string(), z.number().int().nonnegative()),
});
export const historySchema = z.object({
  items: z.array(runSchema.pick({run_id: true, graph_id: true, graph_revision: true, state: true})),
  next_cursor: z.string().nullable(),
});
export type Budget = z.infer<typeof budgetSchema>;
export type Workspace = z.infer<typeof workspaceSchema>;
export type Receipt = z.infer<typeof receiptSchema>;
export type Run = z.infer<typeof runSchema>;
export type History = z.infer<typeof historySchema>;

export const resultSchema = z.object({
  status: z.enum(['recorded', 'unavailable']),
  content: z.json(),
});
