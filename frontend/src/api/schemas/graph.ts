import {z} from 'zod';
import {jsonObjectSchema, timestampSchema} from './json.ts';

export const limitsSchema = z.strictObject({
  max_activations: z.number().int(),
  max_running_nodes: z.number().int(),
  time_limit_seconds: z.number().int(),
  budget_usd: z.string(),
});

const embeddedSchema = z.strictObject({
  position: z.enum(['output', 'memory']),
  component: z.string(),
  config: jsonObjectSchema,
});

const graphNodeSchema = z.strictObject({
  id: z.string(),
  name: z.string(),
  component: z.string(),
  config: jsonObjectSchema,
  embedded: z.array(embeddedSchema).optional(),
});

const connectionSchema = z.strictObject({from: z.string(), to: z.string()});

export const graphDocumentSchema = z.strictObject({
  format: z.literal('slow-thinker.graph/1'),
  id: z.string(),
  name: z.string(),
  limits: limitsSchema,
  nodes: z.array(graphNodeSchema),
  connections: z.array(connectionSchema),
  layout: z.record(z.string(), z.tuple([z.number(), z.number()])).optional(),
  view: z
    .strictObject({
      connections: z.enum(['curved', 'simple', 'routed']).optional(),
      curvature: z.number().min(0).max(1).optional(),
      /** The observation points shown live in run mode: `run`, `node:<id>`, `connection:<from>-><to>`. */
      observe: z.array(z.string().min(1).max(200)).max(1000).optional(),
    })
    .optional(),
  port_sides: z
    .record(
      z.string(),
      z.record(z.string().min(1).max(40), z.enum(['left', 'right', 'top', 'bottom'])),
    )
    .optional(),
});

export const diagnosticSchema = z.strictObject({
  severity: z.enum(['error', 'warning']),
  code: z.string().min(1),
  message: z.string().min(1),
  path: z.string(),
  node_id: z.string().nullable(),
});

export const versionNumber = z.number().int().positive();
export const changeNumber = z.number().int().positive();

export const validationSchema = z.strictObject({diagnostics: z.array(diagnosticSchema)});
export const graphListSchema = z.strictObject({
  graphs: z.array(
    z.strictObject({
      id: z.string(),
      name: z.string(),
      active_version: versionNumber.nullable(),
      latest_change: changeNumber,
      updated_at: timestampSchema,
    }),
  ),
});
export const createdSchema = z.strictObject({
  id: z.string(),
  branch: z.string(),
  change: changeNumber,
});
export const branchSchema = z.strictObject({
  name: z.string().min(1),
  created_at: timestampSchema,
  from_version: versionNumber.nullable(),
  from_change: changeNumber.nullable(),
  latest_change: changeNumber,
  head_version: versionNumber.nullable(),
});
const versionSummarySchema = z.strictObject({
  version: versionNumber,
  branch: z.string().min(1),
  parent: versionNumber.nullable(),
  change: changeNumber,
  name: z.string(),
  created_at: timestampSchema,
});
export const graphDetailSchema = z.strictObject({
  id: z.string(),
  name: z.string(),
  active_version: versionNumber.nullable(),
  latest_change: changeNumber,
  branches: z.array(branchSchema),
  versions: z.array(versionSummarySchema),
});
export const graphVersionSchema = z.strictObject({
  graph_id: z.string(),
  version: versionNumber,
  branch: z.string().min(1),
  parent: versionNumber.nullable(),
  change: changeNumber,
  created_at: timestampSchema,
  document: graphDocumentSchema,
});

export type Limits = z.infer<typeof limitsSchema>;
export type GraphNode = z.infer<typeof graphNodeSchema>;
export type Connection = z.infer<typeof connectionSchema>;
export type GraphDocument = z.infer<typeof graphDocumentSchema>;
export type Diagnostic = z.infer<typeof diagnosticSchema>;
export type GraphSummary = z.infer<typeof graphListSchema>['graphs'][number];
export type CreatedGraph = z.infer<typeof createdSchema>;
export type Branch = z.infer<typeof branchSchema>;
export type VersionSummary = z.infer<typeof versionSummarySchema>;
export type GraphDetail = z.infer<typeof graphDetailSchema>;
export type GraphVersion = z.infer<typeof graphVersionSchema>;
