import {z} from 'zod';

export type JsonValue = string | number | boolean | null | JsonValue[] | JsonObject;
export interface JsonObject {
  [key: string]: JsonValue;
}

export const jsonValueSchema: z.ZodType<JsonValue> = z.lazy(() =>
  z.union([
    z.string(),
    z.number(),
    z.boolean(),
    z.null(),
    z.array(jsonValueSchema),
    z.record(z.string(), jsonValueSchema),
  ]),
);
export const jsonObjectSchema: z.ZodType<JsonObject> = z.record(z.string(), jsonValueSchema);

export const timestampSchema = z.iso.datetime({offset: true});
export const decimalSchema = z.string().regex(/^-?\d+(?:\.\d+)?$/u);
export const countSchema = z.number().int().nonnegative();
export const durationSchema = z.number().nonnegative();
export const pointerSchema = z
  .string()
  .max(200)
  .regex(/^(?:\/(?:[^/~]|~[01])*)+$/u);
export const portNameSchema = z.string().regex(/^[a-z][a-z0-9_]{0,31}$/u);
