import type {z} from 'zod';
import {
  resultSchema,
  historySchema,
  receiptSchema,
  runSchema,
  workspaceSchema,
} from './operator-schemas.ts';
import type {History, Receipt, Run, Workspace} from './operator-schemas.ts';
import {eventsSchema, callSchema, payloadSchema, activationSchema} from './inspection-schemas.ts';
import type {EventPage, CallDetails, RetainedPayload} from './inspection-schemas.ts';
import type {ActivationDetails} from './inspection-schemas.ts';

export type CommandBody = Readonly<Record<string, unknown>>;

export class OperatorClient {
  constructor(private readonly credential: string) {}

  private async request(path: string, signal?: AbortSignal, body?: CommandBody): Promise<Response> {
    return await fetch(`/api/v1${path}`, {
      method: body === undefined ? 'GET' : 'POST',
      credentials: 'omit',
      cache: 'no-store',
      headers: {authorization: `Bearer ${this.credential}`, 'content-type': 'application/json'},
      signal: requestSignal(signal),
      ...(body === undefined ? {} : {body: JSON.stringify(body)}),
    });
  }

  private async read<T>(path: string, schema: z.ZodType<T>, signal: AbortSignal): Promise<T> {
    const response = await this.request(path, signal);
    if (!response.ok) throw new Error(readError(response.status));
    const value: unknown = await response.json();
    return schema.parse(value);
  }

  async workspace(signal: AbortSignal, cursor?: string): Promise<Workspace> {
    const suffix = cursor === undefined ? '' : `?cursor=${encodeURIComponent(cursor)}`;
    return await this.read(`/workspace${suffix}`, workspaceSchema, signal);
  }

  async run(id: string, signal: AbortSignal): Promise<Run> {
    return await this.read(`/runs/${encodeURIComponent(id)}`, runSchema, signal);
  }

  async history(session: string, signal: AbortSignal, cursor?: string): Promise<History> {
    const suffix = cursor === undefined ? '' : `?cursor=${encodeURIComponent(cursor)}`;
    return await this.read(
      `/sessions/${encodeURIComponent(session)}/runs${suffix}`,
      historySchema,
      signal,
    );
  }

  async result(id: string, signal: AbortSignal): Promise<string> {
    const reply = await this.read(`/runs/${encodeURIComponent(id)}/result`, resultSchema, signal);
    return reply.status === 'recorded'
      ? JSON.stringify(reply.content, null, 2)
      : 'No hay resultado final disponible.';
  }

  async command(id: string, signal: AbortSignal): Promise<Receipt | null> {
    const response = await this.request(`/commands/${encodeURIComponent(id)}`, signal);
    if (response.status === 404) return null;
    if (!response.ok) throw new Error(readError(response.status));
    const value: unknown = await response.json();
    return receiptSchema.parse(value);
  }

  async events(run: string, signal: AbortSignal, cursor?: string): Promise<EventPage> {
    const suffix = cursor === undefined ? '' : `?cursor=${encodeURIComponent(cursor)}`;
    return await this.read(
      `/runs/${encodeURIComponent(run)}/events${suffix}`,
      eventsSchema,
      signal,
    );
  }

  async call(run: string, id: string, signal: AbortSignal, cursor?: string): Promise<CallDetails> {
    const suffix = cursor === undefined ? '' : `?cursor=${encodeURIComponent(cursor)}`;
    const path = `/runs/${encodeURIComponent(run)}/calls/${encodeURIComponent(id)}${suffix}`;
    return await this.read(path, callSchema, signal);
  }

  async payload(run: string, id: string, signal: AbortSignal): Promise<RetainedPayload> {
    const path = `/runs/${encodeURIComponent(run)}/payloads/${encodeURIComponent(id)}`;
    return await this.read(path, payloadSchema, signal);
  }

  async activation(
    run: string,
    id: string,
    signal: AbortSignal,
    cursor?: string,
  ): Promise<ActivationDetails> {
    const suffix = cursor === undefined ? '' : `?cursor=${encodeURIComponent(cursor)}`;
    const path = `/runs/${encodeURIComponent(run)}/activations/${encodeURIComponent(id)}${suffix}`;
    return await this.read(path, activationSchema, signal);
  }

  async send(path: string, body: CommandBody): Promise<Receipt> {
    const response = await this.request(path, undefined, body);
    const value: unknown = await response.json();
    const receipt = receiptSchema.safeParse(value);
    if (receipt.success) return receipt.data;
    throw new Error(readError(response.status));
  }
}

function readError(status: number): string {
  if (status === 401 || status === 403) return 'Acceso rechazado. Comprueba la clave de acceso.';
  if (status === 404) return 'La ejecución no está habilitada o el registro no existe.';
  return 'No se pudo confirmar el estado del servidor. Vuelve a consultar antes de enviar otra orden.';
}

function requestSignal(signal: AbortSignal | undefined): AbortSignal {
  const timeout = AbortSignal.timeout(signal === undefined ? 65_000 : 10_000);
  return signal === undefined ? timeout : AbortSignal.any([signal, timeout]);
}
