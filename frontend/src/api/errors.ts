import {z} from 'zod';
import {diagnosticSchema} from './schemas/graph.ts';
import type {Diagnostic} from './schemas/graph.ts';

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly diagnostics: readonly Diagnostic[] = [],
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Statuses the operator API documents for each error code; other codes keep their status. */
const documentedStatus: Readonly<Record<string, number>> = {
  graph_exists: 409,
  graph_not_found: 404,
  version_not_found: 404,
  run_not_found: 404,
  invalid_document: 422,
  too_many_runs: 409,
};

const errorSchema = z.strictObject({
  error: z.strictObject({
    code: z.string().regex(/^[a-z][a-z0-9_]{0,63}$/u),
    message: z.string().min(1).max(2000),
    diagnostics: z.array(diagnosticSchema).optional(),
  }),
});

export function errorFromReply(status: number, value: unknown): ApiError {
  const parsed = errorSchema.safeParse(value);
  if (!parsed.success) return fallbackError(status);
  const {code, message, diagnostics = []} = parsed.data.error;
  const expected = documentedStatus[code];
  if (expected !== undefined && expected !== status) return unexpectedReply(status);
  return new ApiError(status, code, message, diagnostics);
}

function fallbackError(status: number): ApiError {
  if (status === 401 || status === 403)
    return new ApiError(status, 'access_denied', 'The operator token was not accepted.');
  return unexpectedReply(status);
}

export function unexpectedReply(status: number): ApiError {
  return new ApiError(
    status,
    'invalid_response',
    'The server returned a response this interface does not understand.',
  );
}

export function requestFailure(signal: AbortSignal | undefined, timedOut: boolean): ApiError {
  if (signal?.aborted === true) return new ApiError(0, 'aborted', 'The request was cancelled.');
  if (timedOut) return new ApiError(0, 'timeout', 'The server did not answer in time.');
  return new ApiError(0, 'network_error', 'Could not reach the server.');
}

export function errorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : 'Something went wrong. Try again.';
}
