import {z} from 'zod';

export interface DefinitionIssue {
  readonly pointer: string;
  readonly message: string;
}

export class DefinitionError extends Error {
  constructor(
    readonly code: string,
    readonly issues: readonly DefinitionIssue[] = [],
  ) {
    super(code.replaceAll('_', ' '));
    this.name = 'DefinitionError';
  }
}

const statuses: Readonly<Record<string, number>> = {
  invalid_json: 400,
  invalid_query: 400,
  invalid_cursor: 400,
  unsupported_transport_options: 400,
  operator_authentication_required: 401,
  operator_host_denied: 403,
  operator_origin_denied: 403,
  definition_not_found: 404,
  definition_conflict: 409,
  request_too_large: 413,
  response_too_large: 413,
  json_content_required: 415,
  invalid_definition: 422,
  definition_parent_missing: 422,
  operator_service_unavailable: 503,
};
const issueSchema = z.object({
  pointer: z
    .string()
    .max(160)
    .regex(/^(?:\/(?:[^~/]|~[01])*)*$/u),
  message: z.string().min(1).max(160),
});
const errorSchema = z.object({
  schema_version: z.literal('0.1-draft'),
  error: z.object({
    code: z.string(),
    message: z.string().min(1).max(160),
    request_id: z.string().min(1).max(128),
    issues: z.array(issueSchema).max(10).optional(),
  }),
});

export function definitionFailure(value: unknown, status: number): Error {
  const parsed = errorSchema.safeParse(value);
  if (!parsed.success) return new Error('Invalid definition error response.');
  const error = parsed.data.error;
  if (!Object.hasOwn(statuses, error.code) || statuses[error.code] !== status)
    return new Error('Unrecognized definition error response.');
  return new DefinitionError(error.code, error.code === 'invalid_definition' ? error.issues : []);
}

export function unconfirmedDefinitionFailure(saving: boolean): Error {
  return new Error(
    saving
      ? 'Could not confirm whether the definition was saved. Replay the unchanged source to recover.'
      : 'Could not confirm the definition response. Refresh and try again.',
  );
}
