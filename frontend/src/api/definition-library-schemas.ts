import {z} from 'zod';
import {jsonObjectSchema} from './graph-schemas.ts';

export const referenceSchema = z.object({
  graph_id: z.string().regex(/^[a-z][a-z0-9_.-]*$/u),
  revision: z.string().min(1),
});
const libraryItemSchema = referenceSchema.extend({
  participants: z.number().int().positive(),
  nodes: z.array(z.object({id: z.string().min(1), component: z.string().min(1)})).min(1),
  input_schema: jsonObjectSchema,
  origin: z.enum(['bundled', 'personal']),
  derived_from: referenceSchema.nullable(),
});
export const libraryPageSchema = z
  .object({
    items: z.array(libraryItemSchema).max(100),
    next_cursor: z.string().min(1).nullable(),
  })
  .refine(
    (page) =>
      new Set(page.items.map((item) => JSON.stringify([item.graph_id, item.revision]))).size ===
      page.items.length,
    'The library page contains duplicate identities.',
  );
export const validationResultSchema = referenceSchema.extend({
  validation_scope: z.literal('definition'),
});
export const saveResultSchema = referenceSchema.extend({created: z.boolean()});
