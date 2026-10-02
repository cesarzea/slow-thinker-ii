import type {z} from 'zod';
import {referenceSchema} from './definition-library-schemas.ts';
import {
  DefinitionError,
  definitionFailure,
  unconfirmedDefinitionFailure,
} from './definition-errors.ts';

type SourceReference = z.infer<typeof referenceSchema>;

export class DefinitionTransport {
  constructor(private readonly credential: string) {}

  protected async read<T>(
    path: string,
    schema: z.ZodType<T>,
    signal: AbortSignal,
    source?: string,
    accepts?: (value: T, status: number) => boolean,
  ): Promise<T> {
    const saving = source !== undefined && path === '/definitions';
    try {
      const response = await this.request(path, signal, source, saving);
      return await definitionResponse(response, schema, saving, accepts);
    } catch (error) {
      if (error instanceof DefinitionError && !uncertainSaveError(error, saving)) throw error;
      throw unconfirmedDefinitionFailure(saving);
    }
  }

  protected async text(
    path: string,
    reference: SourceReference,
    signal: AbortSignal,
    body?: string,
  ): Promise<string> {
    try {
      const response = await this.request(path, signal, body, false);
      return await definitionTextResponse(response, reference);
    } catch (error) {
      if (error instanceof DefinitionError) throw error;
      throw unconfirmedDefinitionFailure(false);
    }
  }

  private async request(
    path: string,
    signal: AbortSignal,
    source: string | undefined,
    saving: boolean,
  ): Promise<Response> {
    return await fetch(`/api/v1${path}`, {
      method: source === undefined ? 'GET' : 'POST',
      credentials: 'omit',
      cache: 'no-store',
      headers: {authorization: `Bearer ${this.credential}`, 'content-type': 'application/json'},
      signal: AbortSignal.any([signal, AbortSignal.timeout(saving ? 65_000 : 10_000)]),
      ...(source === undefined ? {} : {body: source}),
    });
  }
}

async function definitionTextResponse(
  response: Response,
  reference: SourceReference,
): Promise<string> {
  const source = await response.text();
  const value: unknown = JSON.parse(source);
  if (!response.ok) throw definitionFailure(value, response.status);
  const contentType = response.headers.get('content-type')?.split(';')[0]?.trim().toLowerCase();
  if (response.status !== 200 || contentType !== 'application/json')
    throw unconfirmedDefinitionFailure(false);
  const identity = referenceSchema.parse(value);
  if (identity.graph_id !== reference.graph_id || identity.revision !== reference.revision)
    throw unconfirmedDefinitionFailure(false);
  return source;
}

function uncertainSaveError(error: DefinitionError, saving: boolean): boolean {
  return saving && ['response_too_large', 'operator_service_unavailable'].includes(error.code);
}

async function definitionResponse<T>(
  response: Response,
  schema: z.ZodType<T>,
  saving: boolean,
  accepts: ((value: T, status: number) => boolean) | undefined,
): Promise<T> {
  const value: unknown = await response.json();
  if (!response.ok) throw definitionFailure(value, response.status);
  const parsed = schema.parse(value);
  if (response.status !== 200 && !(saving && response.status === 201))
    throw unconfirmedDefinitionFailure(saving);
  if (accepts !== undefined && !accepts(parsed, response.status))
    throw unconfirmedDefinitionFailure(saving);
  return parsed;
}
