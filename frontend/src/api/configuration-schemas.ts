import {z} from 'zod';
import {jsonObjectSchema} from './graph-schemas.ts';

const positive = z.number().positive();
const budget = z
  .string()
  .regex(/^(?:0|[1-9]\d*)(?:\.\d{1,9})?$/u)
  .max(40);
const limitsSchema = z.object({
  run_seconds: positive,
  call_seconds: positive,
  startup_seconds: positive,
  shutdown_seconds: positive,
  max_calls: positive.int(),
  max_depth: positive.int(),
  max_payload_bytes: positive.int(),
  run_budget: budget,
  session_budget: budget,
  month_budget: budget,
});
const installedTypeSchema = z.object({
  type_id: z.string().min(1),
  type_version: z.string().min(1),
  roles: z.array(z.string()),
  config_schema: jsonObjectSchema,
  resource_slots: jsonObjectSchema,
  operations: jsonObjectSchema,
  installation_status: z.string().min(1).max(160),
});
const modelProfileSchema = z.object({
  provider_profile: z.string().min(1),
  provider: z.string().min(1),
  model: z.string().min(1),
  reasoning_efforts: z.array(z.string()),
  supports_temperature: z.boolean(),
  default_output_tokens: positive.int(),
  maximum_output_tokens: positive.int(),
  billing_profile: z.string().min(1),
  review_expires_at: z.number(),
  tariff_status: z.enum(['ready', 'unavailable', 'stale', 'review_expired']),
});
export const configurationCatalogSchema = z.object({
  schema_version: z.literal('1'),
  configuration_revision: z.string().min(1),
  components: z.array(installedTypeSchema).max(1000),
  models: z.array(modelProfileSchema).max(1000),
  graph_schema: jsonObjectSchema,
  schema_documents: z.record(z.string(), jsonObjectSchema),
  supported_graph_profiles: z.array(z.string()),
  limits: z.object({current: limitsSchema, maximum: limitsSchema}),
});
export const limitsCommandSchema = z
  .object({
    command_id: z.string().regex(/^[0-9a-f]{32}$/u),
    expected_revision: z.string().min(1),
    limits: limitsSchema
      .partial()
      .strict()
      .refine((value) => Object.keys(value).length > 0),
  })
  .strict();
export const configurationReceiptSchema = z.object({
  command_id: z.string().regex(/^[0-9a-f]{32}$/u),
  configuration_revision: z.string().min(1),
  replayed: z.boolean(),
});
export type EffectiveLimits = z.infer<typeof limitsSchema>;
export type ConfigurationCatalog = z.infer<typeof configurationCatalogSchema>;
export type InstalledType = z.infer<typeof installedTypeSchema>;
export type ModelProfile = z.infer<typeof modelProfileSchema>;
export type LimitsCommand = z.infer<typeof limitsCommandSchema>;
export type ConfigurationReceipt = z.infer<typeof configurationReceiptSchema>;
