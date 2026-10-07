import {z} from 'zod';
import {eventData} from './event-data.ts';
import {durationSchema, timestampSchema} from './json.ts';

type Kinds = typeof eventData;
type Kind = keyof Kinds;

const envelope = {
  run_id: z.string(),
  seq: z.number().int().positive(),
  at: timestampSchema,
  elapsed_ms: durationSchema,
  evidence: z.enum(['observed', 'reported']),
  node_id: z.string().nullable(),
  activation_id: z.string().nullable(),
};

function variant<K extends Kind>(
  kind: K,
): z.ZodObject<typeof envelope & {kind: z.ZodLiteral<K>; data: Kinds[K]}, z.core.$strict> {
  return z.strictObject({...envelope, kind: z.literal(kind), data: eventData[kind]});
}

const runEventSchema = z.discriminatedUnion('kind', [
  variant('run.started'),
  variant('host.ready'),
  variant('host.failed'),
  variant('run.running'),
  variant('message.sent'),
  variant('message.discarded'),
  variant('message.dropped'),
  variant('activation.started'),
  variant('activation.completed'),
  variant('activation.failed'),
  variant('activation.cancelled'),
  variant('component.called'),
  variant('llm.called'),
  variant('report'),
  variant('run.result'),
  variant('run.finished'),
]);

export const eventPageSchema = z.strictObject({
  events: z.array(runEventSchema),
  last_seq: z.number().int().nonnegative(),
  finished: z.boolean(),
});

export type RunEvent = z.infer<typeof runEventSchema>;
export type RunEventKind = RunEvent['kind'];
export type EventOf<K extends RunEventKind> = Extract<RunEvent, {kind: K}>;
export type EventPage = z.infer<typeof eventPageSchema>;
