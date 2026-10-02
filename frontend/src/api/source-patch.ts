import {z} from 'zod';

const patchOperationSchema = z.discriminatedUnion('op', [
  z.object({op: z.literal('add'), path: z.string(), value_json: z.string()}).strict(),
  z.object({op: z.literal('replace'), path: z.string(), value_json: z.string()}).strict(),
  z.object({op: z.literal('remove'), path: z.string()}).strict(),
]);
export type PatchOperation = z.infer<typeof patchOperationSchema>;

export function patchBody(source: string, operations: readonly PatchOperation[]): string {
  const parsed = z.array(patchOperationSchema).min(1).max(100).parse(operations);
  return JSON.stringify({source, operations: parsed});
}
