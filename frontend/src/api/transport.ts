import type {z} from 'zod';

export type CommandBody = Readonly<Record<string, unknown>>;

export class OperatorTransport {
  constructor(private readonly credential: string) {}

  protected async request(
    path: string,
    signal?: AbortSignal,
    body?: CommandBody,
  ): Promise<Response> {
    return await fetch(`/api/v1${path}`, {
      method: body === undefined ? 'GET' : 'POST',
      credentials: 'omit',
      cache: 'no-store',
      headers: {authorization: `Bearer ${this.credential}`, 'content-type': 'application/json'},
      signal: requestSignal(signal),
      ...(body === undefined ? {} : {body: JSON.stringify(body)}),
    });
  }

  protected async read<T>(path: string, schema: z.ZodType<T>, signal: AbortSignal): Promise<T> {
    const response = await this.request(path, signal);
    if (!response.ok) throw new Error(readError(response.status));
    const value: unknown = await response.json();
    return schema.parse(value);
  }
}

export function readError(status: number): string {
  if (status === 401 || status === 403) return 'Access denied. Check the access key.';
  if (status === 404) return 'Execution is not enabled or the record does not exist.';
  return 'Could not confirm the server state. Check again before sending another command.';
}

function requestSignal(signal: AbortSignal | undefined): AbortSignal {
  const timeout = AbortSignal.timeout(signal === undefined ? 65_000 : 10_000);
  return signal === undefined ? timeout : AbortSignal.any([signal, timeout]);
}
