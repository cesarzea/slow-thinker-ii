import type {Run, Workspace, OperatorClient} from '../../api/index.ts';
import type {ExecutionCommands} from './commands.ts';
import {failureMessage} from './receipts.ts';
import {ProjectionReader, emptyProjection} from './projection.ts';
import type {ExecutionProjection} from './projection.ts';
import type {ExecutionStore} from './state.ts';

export class ExecutionPolling {
  private reading = false;
  private readonly projections: ProjectionReader;

  constructor(
    private readonly store: ExecutionStore,
    private readonly commands: ExecutionCommands,
    private readonly client: OperatorClient,
  ) {
    this.projections = new ProjectionReader(client);
  }

  async refresh(signal: AbortSignal): Promise<void> {
    if (this.reading || this.store.closed) return;
    this.reading = true;
    try {
      await this.commands.recover(signal);
      await this.readState(signal);
    } catch (error) {
      if (!signal.aborted) this.store.update({stale: true, message: failureMessage(error)});
    } finally {
      this.reading = false;
    }
  }

  private async readState(signal: AbortSignal): Promise<void> {
    const epoch = this.store.epoch;
    const state = this.store.snapshot();
    const workspace = await this.client.workspace(signal, state.workspaceCursor);
    const session = selectedSession(state.sessionId, workspace);
    const run = state.runId === '' ? null : await this.client.run(state.runId, signal);
    const projection = run === null ? emptyProjection : await this.readProjection(run, signal);
    const history =
      session === '' ? null : await this.client.history(session, signal, state.historyCursor);
    if (signal.aborted || epoch !== this.store.epoch) return;
    if (regressed(run, state.run)) return;
    this.store.update({workspace, sessionId: session, run, history, stale: false, ...projection});
  }
  private async readProjection(run: Run, signal: AbortSignal): Promise<ExecutionProjection> {
    try {
      return await this.projections.read(run, signal);
    } catch {
      this.projections.reset();
      const previous = this.store.snapshot();
      return {
        detail: previous.detail,
        execution: previous.execution,
        projectionError:
          'No se pudo actualizar el grafo. La evidencia visible puede estar desactualizada.',
      };
    }
  }
}

function regressed(run: Run | null, previous: Run | null): boolean {
  return (
    run !== null &&
    previous !== null &&
    run.backend_generation === previous.backend_generation &&
    run.last_event_sequence < previous.last_event_sequence
  );
}

function selectedSession(selected: string, workspace: Workspace): string {
  return selected === '' ? (workspace.sessions.items[0]?.session_id ?? '') : selected;
}
