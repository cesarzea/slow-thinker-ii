import {z} from 'zod';
import {branchSchema, changeNumber, graphDocumentSchema, versionNumber} from './graph.ts';
import {timestampSchema} from './json.ts';

export const branchListSchema = z.strictObject({branches: z.array(branchSchema)});
export const branchCreatedSchema = z.strictObject({name: z.string().min(1), change: changeNumber});
export const changeSavedSchema = z.strictObject({change: changeNumber, at: timestampSchema});

const changeSummarySchema = z.strictObject({
  change: changeNumber,
  branch: z.string().min(1),
  at: timestampSchema,
  name: z.string(),
  version: versionNumber.nullable(),
});
export const changeListSchema = z.strictObject({changes: z.array(changeSummarySchema)});
export const changeRecordSchema = z.strictObject({
  graph_id: z.string(),
  change: changeNumber,
  branch: z.string().min(1),
  at: timestampSchema,
  document: graphDocumentSchema,
  version: versionNumber.nullable(),
});
export const activationSchema = z.strictObject({
  version: versionNumber,
  branch: z.string().min(1),
  change: changeNumber,
});

/** Where a new branch starts: a version or a change of any branch. */
export type BranchOrigin = {readonly version: number} | {readonly change: number};
export type CreatedBranch = z.infer<typeof branchCreatedSchema>;
export type SavedChange = z.infer<typeof changeSavedSchema>;
export type ChangeSummary = z.infer<typeof changeSummarySchema>;
export type ChangeRecord = z.infer<typeof changeRecordSchema>;
export type Activation = z.infer<typeof activationSchema>;
/** `GET /graphs/{id}/changes`: one branch or every branch, numbers below `before`. */
export interface ChangeQuery {
  readonly branch?: string;
  readonly before?: number;
  readonly limit?: number;
}
