import {z} from 'zod';

export const reportSchema = z.object({
  event_sequence: z.number().int().positive(),
  kind: z.string().min(1),
  schema_version: z.string().min(1),
  evidence: z.literal('reported'),
  payload_id: z.string().nullable(),
  source_occurred_at: z.number().nullable(),
});
export type ReportView = z.infer<typeof reportSchema>;
