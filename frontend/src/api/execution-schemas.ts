import {z} from 'zod';

const activationViewSchema = z.object({
  id: z.string().min(1),
  node: z.string().min(1),
  component: z.string().min(1),
  ordinal: z.number().int().positive(),
  state: z.string().min(1),
  call_id: z.string().min(1),
  selected_port: z.string().nullable(),
});
const communicationSchema = z.object({
  id: z.string().min(1),
  caller: z.string(),
  target: z.string().min(1),
  operation: z.string().min(1),
  parent_call_id: z.string().nullable(),
  activation_id: z.string().nullable(),
  state: z.string().min(1),
});
export const executionPageSchema = z
  .object({
    run_id: z.string().min(1),
    graph_revision: z.string().min(1),
    backend_generation: z.string().min(1),
    through_sequence: z.number().int().nonnegative(),
    activations: z.array(activationViewSchema).readonly(),
    calls: z.array(communicationSchema).readonly(),
    next_cursor: z.string().nullable(),
  })
  .refine(
    (page) =>
      new Set(page.activations.map((item) => item.id)).size === page.activations.length &&
      new Set(page.calls.map((item) => item.id)).size === page.calls.length,
    'The page contains duplicate identities.',
  );
export type ActivationView = Readonly<z.infer<typeof activationViewSchema>>;
export type CommunicationView = Readonly<z.infer<typeof communicationSchema>>;
export type ExecutionPage = Readonly<z.infer<typeof executionPageSchema>>;
