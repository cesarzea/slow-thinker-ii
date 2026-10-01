import type {OperatorClient} from '../../api/index.ts';
import type {CommandBody, GraphSummary} from '../../api/index.ts';
import {acceptReceipt, failureMessage} from './receipts.ts';
import {compileInput, inputError, legacyInputSchema} from './input-schema.ts';
import {canStart, pendingKey} from './state.ts';
import type {IdentityStorage, ExecutionStore} from './state.ts';

export class ExecutionCommands {
  private retryRequest: {path: string; body: CommandBody} | null = null;

  constructor(
    readonly store: ExecutionStore,
    private readonly client: OperatorClient,
    private readonly storage: IdentityStorage,
  ) {}

  async createSession(name: string): Promise<void> {
    if (name.trim() !== '') await this.begin('session', '/sessions', {name});
  }

  async start(graph: GraphSummary, value: unknown): Promise<void> {
    const state = this.store.snapshot();
    const schema = compileInput(graph.input_schema ?? legacyInputSchema);
    const input =
      typeof value === 'string' && inputError(schema, value) !== null ? {problem: value} : value;
    const error = inputError(schema, input);
    if (!canStart(state) || error !== null) return;
    await this.begin('start', '/runs', {
      session_id: state.sessionId,
      graph_id: graph.graph_id,
      graph_revision: graph.revision,
      configuration_revision: state.workspace?.configuration_revision,
      input,
    });
  }

  async stop(): Promise<void> {
    const run = this.store.snapshot().runId;
    if (run !== '') await this.begin('stop', `/runs/${encodeURIComponent(run)}/stop`, {});
  }

  private async begin(kind: string, path: string, values: CommandBody): Promise<void> {
    const state = this.store.snapshot();
    if (state.pending !== null || state.busy || this.store.closed || !state.storageReady) return;
    const commandId = `${kind}-${crypto.randomUUID()}`;
    try {
      this.storage.setItem(pendingKey, commandId);
    } catch {
      this.store.update({
        message: 'Could not save the command reference. The command was not sent.',
      });
      return;
    }
    this.store.invalidate();
    this.store.update({pending: commandId, busy: true});
    this.retryRequest = {
      path,
      body: {...values, schema_version: '0.1-draft', command_id: commandId},
    };
    await this.deliver(this.retryRequest);
  }

  private async deliver(request: {path: string; body: CommandBody}): Promise<void> {
    try {
      const receipt = await this.client.send(request.path, request.body);
      if (receipt.command_id !== request.body['command_id'])
        throw new Error('The receipt does not match this command.');
      acceptReceipt(this.store, this.storage, receipt);
    } catch (error) {
      this.store.update({message: failureMessage(error), busy: false, stale: true});
    }
  }

  async recover(signal: AbortSignal): Promise<void> {
    const id = this.store.snapshot().pending;
    if (id === null || this.store.snapshot().busy) return;
    try {
      const receipt = await this.client.command(id, signal);
      if (signal.aborted) return;
      if (receipt !== null) acceptReceipt(this.store, this.storage, receipt);
      else
        this.store.update({
          message: 'Request unconfirmed. You can check its receipt again.',
        });
    } catch (error) {
      if (!signal.aborted) this.store.update({message: failureMessage(error), stale: true});
    }
  }

  async retry(): Promise<void> {
    if (
      this.retryRequest === null ||
      this.store.snapshot().busy ||
      this.store.snapshot().pending === null
    )
      return;
    this.store.update({busy: true});
    await this.deliver(this.retryRequest);
  }

  async withdraw(): Promise<void> {
    const id = this.store.snapshot().pending;
    if (id?.startsWith('start-') !== true) return;
    this.store.update({busy: true});
    await this.deliver({
      path: `/commands/${encodeURIComponent(id)}/withdraw`,
      body: {schema_version: '0.1-draft', command_id: id},
    });
  }

  canRetry(): boolean {
    return this.retryRequest !== null;
  }

  forgetNonStart(): void {
    const id = this.store.snapshot().pending;
    if (id === null || id.startsWith('start-') || this.store.snapshot().busy) return;
    try {
      this.storage.removeItem(pendingKey);
    } catch {
      this.store.update({message: 'Could not remove local tracking.'});
      return;
    }
    this.store.update({
      pending: null,
      stale: true,
      message: 'Tracking removed. The request may still complete on the server.',
    });
  }
}
