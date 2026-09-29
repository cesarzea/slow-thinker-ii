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

import {OperatorTransport, readError} from './transport.ts';
import type {CommandBody} from './transport.ts';
import {graphDetailSchema} from './graph-schemas.ts';
import type {GraphDetail} from './graph-schemas.ts';
import {executionPageSchema} from './execution-schemas.ts';
import type {ExecutionPage} from './execution-schemas.ts';
import {definitionSchema} from './definition-schema.ts';
export type {CommandBody} from './transport.ts';

export class OperatorClient extends OperatorTransport {
  async graph(id: string, revision: string, signal: AbortSignal): Promise<GraphDetail> {
    const path = `/graphs/${encodeURIComponent(id)}/revisions/${encodeURIComponent(revision)}`;
    const detail = await this.read(path, graphDetailSchema, signal);
    if (detail.graph_id !== id || detail.revision !== revision)
      throw new Error('Revisión incorrecta.');
    return detail;
  }

  async definition(run: string, signal: AbortSignal): Promise<GraphDetail> {
    const detail = await this.read(
      `/runs/${encodeURIComponent(run)}/definition`,
      definitionSchema,
      signal,
    );
    if (detail.run_id !== run) throw new Error('Definición de otra ejecución.');
    return detail;
  }

  async execution(run: string, signal: AbortSignal, cursor?: string): Promise<ExecutionPage> {
    const suffix = cursor === undefined ? '' : `?cursor=${encodeURIComponent(cursor)}`;
    const page = await this.read(
      `/runs/${encodeURIComponent(run)}/execution${suffix}`,
      executionPageSchema,
      signal,
    );
    if (page.run_id !== run) throw new Error('Proyección de otra ejecución.');
    return page;
  }

  async workspace(signal: AbortSignal, cursor?: string): Promise<Workspace> {
    const suffix = cursor === undefined ? '' : `?cursor=${encodeURIComponent(cursor)}`;
    return await this.read(`/workspace${suffix}`, workspaceSchema, signal);
  }

  async run(id: string, signal: AbortSignal): Promise<Run> {
    const run = await this.read(`/runs/${encodeURIComponent(id)}`, runSchema, signal);
    if (run.run_id !== id) throw new Error('Estado de otra ejecución.');
    return run;
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
