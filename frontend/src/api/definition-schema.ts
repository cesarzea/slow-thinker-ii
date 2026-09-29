import {z} from 'zod';
import {graphDetailSchema, jsonObjectSchema} from './graph-schemas.ts';

export const definitionSchema = graphDetailSchema.and(
  z.object({
    schema_version: z.literal('0.1-draft'),
    run_id: z.string().min(1),
    execution: jsonObjectSchema,
  }),
);
