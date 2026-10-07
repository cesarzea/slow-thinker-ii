import {z} from 'zod';

/** `GET /access`: whether the operator endpoints need the operator token. */
export const accessSchema = z.strictObject({authentication: z.enum(['token', 'none'])});

export type Access = z.infer<typeof accessSchema>;
