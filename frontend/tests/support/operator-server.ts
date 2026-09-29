import {z} from 'zod';
import {singleDetail, savedDefinition, executionPage} from './projection-data.ts';
import type {Receipt, Run} from '../../src/api/index.ts';
import {graph, reply, runRecord, workspace} from './operator-data.ts';

const commandSchema = z.object({command_id: z.string(), name: z.string().optional()});

export class OperatorServer {
  workspace = structuredClone(workspace);
  run: Run | null = null;
  readonly receipts = new Map<string, Receipt>();
  readonly mutations: {path: string; body: string}[] = [];
  loseReply = false;
  pending = false;
  readStatus = 200;
  historyCursor: string | null = null;
  resultStatus = 200;
  detail: unknown = singleDetail;
  definition: unknown = savedDefinition();
  execution: unknown = executionPage;
  projectionStatus = 200;

  readonly fetch = (input: string, init?: RequestInit): Promise<Response> =>
    Promise.resolve().then(() => {
      const path = new URL(input, 'https://fixture.invalid').pathname.replace('/api/v1', '');
      if (init?.method === 'POST') {
        if (typeof init.body !== 'string') throw new TypeError('Expected a JSON string');
        return this.mutate(path, init.body);
      }
      if (this.readStatus !== 200) return reply({error: 'unavailable'}, this.readStatus);
      return this.read(path);
    });

  private read(path: string): Response {
    const projection = this.projection(path);
    if (projection !== null) return projection;
    if (path === '/workspace') return reply(this.workspace);
    if (path.startsWith('/commands/')) return this.command(path);
    if (path.startsWith('/sessions/'))
      return reply({items: this.run === null ? [] : [this.run], next_cursor: this.historyCursor});
    if (path.endsWith('/result'))
      return reply(
        {status: 'recorded', content: {nodes: {draft: {text: 'A test result'}}}},
        this.resultStatus,
      );
    return this.run === null ? reply({}, 404) : reply(this.run);
  }

  private projection(path: string): Response | null {
    if (path.includes('/revisions/')) return reply(this.detail);
    if (path.endsWith('/definition')) return reply(this.definition, this.projectionStatus);
    if (path.endsWith('/execution')) return reply(this.execution, this.projectionStatus);
    if (path === '/graphs') return reply([graph]);
    return null;
  }

  private command(path: string): Response {
    const receipt = this.receipts.get(decodeURIComponent(path.slice('/commands/'.length)));
    return receipt === undefined ? reply({}, 404) : reply(receipt);
  }

  private mutate(path: string, body: string): Response {
    const command = commandSchema.parse(JSON.parse(body) as unknown);
    this.mutations.push({path, body});
    const existing = this.receipts.get(command.command_id);
    if (existing !== undefined && !path.endsWith('/withdraw')) return reply(existing);
    const receipt = this.apply(path, command.command_id, command.name);
    this.receipts.set(receipt.command_id, receipt);
    if (this.loseReply) throw new Error('Reply lost after commit');
    return reply(receipt, 202);
  }

  private apply(path: string, id: string, name: string | undefined): Receipt {
    if (path.endsWith('/withdraw'))
      return {
        command_id: id,
        kind: 'start',
        disposition: 'withdrawn',
        target_id: null,
        reason: null,
      };
    if (path === '/sessions') return this.session(id, name);
    if (path === '/runs') return this.start(id);
    if (this.run !== null) {
      this.run.state = 'cancelled';
      this.run.cleanup = 'confirmed';
    }
    this.workspace.admission_available = true;
    return {
      command_id: id,
      kind: 'stop',
      disposition: 'accepted',
      target_id: 'run',
      reason: 'operator_stop',
    };
  }

  private session(id: string, name: string | undefined): Receipt {
    this.workspace.sessions.items.push({
      session_id: 'new-session',
      name: name ?? 'New',
      created_at: 2,
    });
    return {
      command_id: id,
      kind: 'session',
      disposition: 'accepted',
      target_id: 'new-session',
      reason: null,
    };
  }

  private start(id: string): Receipt {
    this.run = runRecord();
    if (this.pending) {
      this.run.state = 'running';
      this.run.cleanup = 'unconfirmed';
    }
    this.workspace.admission_available = !this.pending;
    return {
      command_id: id,
      kind: 'start',
      disposition: 'accepted',
      target_id: 'run',
      reason: null,
    };
  }
}
