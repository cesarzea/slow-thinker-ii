import {z} from 'zod';

const eventSchema = z.object({
  sequence: z.number().int().positive(),
  event: z.string(),
  received_at: z.string(),
  call_id: z.string().nullable(),
  payload_id: z.string(),
});
export const eventsSchema = z.object({
  run_id: z.string(),
  through_sequence: z.number().int().nonnegative(),
  items: z.array(eventSchema),
  next_cursor: z.string().nullable(),
});
const receiptSchema = z.object({
  receipt_id: z.string(),
  received_at: z.string(),
  succeeded: z.boolean(),
  publish: z.boolean(),
  reason: z.string().nullable(),
  response_payload_id: z.string(),
  usage_payload_id: z.string(),
  amount: z.string().nullable(),
  source: z.string().nullable(),
});
export const callSchema = z.object({
  run_id: z.string(),
  call_id: z.string(),
  attempt_id: z.string(),
  state: z.string(),
  reason: z.string().nullable(),
  request_payload_id: z.string(),
  pricing_payload_id: z.string().nullable(),
  result_receipt_id: z.string().nullable(),
  context: z.object({
    parent_call_id: z.string().nullable(),
    caller: z.string().nullable(),
    target: z.object({instance: z.string(), operation: z.string()}),
    activation_id: z.string().nullable(),
    node_id: z.string().nullable().optional(),
  }),
  accounting: z
    .object({
      state: z.string(),
      bound: z.string(),
      amount: z.string().nullable(),
      outstanding: z.string(),
      source: z.string().nullable(),
      month_id: z.string(),
    })
    .nullable(),
  receipts: z.object({items: z.array(receiptSchema), next_cursor: z.string().nullable()}),
});
export const payloadSchema = z.object({
  run_id: z.string(),
  payload_id: z.string(),
  status: z.enum(['present', 'redacted', 'unavailable', 'omitted_size_limit', 'deleted']),
  reason: z.string().nullable(),
  size_bytes: z.number().int().nonnegative().nullable(),
  content: z.json(),
});
export type EventPage = z.infer<typeof eventsSchema>;
export type CallDetails = z.infer<typeof callSchema>;
export type RetainedPayload = z.infer<typeof payloadSchema>;

export const activationSchema = z.object({
  run_id: z.string(),
  activation_id: z.string(),
  node_id: z.string().nullable(),
  target: z.object({instance: z.string(), operation: z.string()}),
  root_call_id: z.string(),
  state: z.string(),
  reason: z.string().nullable(),
  input_payload_id: z.string(),
  output_payload_id: z.string().nullable(),
  bindings_payload_id: z.string(),
  calls: z.object({
    items: z.array(
      z.object({
        call_id: z.string(),
        parent_call_id: z.string().nullable(),
        caller: z.string().nullable(),
        target: z.object({instance: z.string(), operation: z.string()}),
        state: z.string(),
      }),
    ),
    next_cursor: z.string().nullable(),
  }),
});
export type ActivationDetails = z.infer<typeof activationSchema>;
