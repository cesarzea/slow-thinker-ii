import {errorMessage} from '../../api/index.ts';
import type {RunDetail, RunStatus} from '../../api/index.ts';

export interface RunState {
  readonly run: RunDetail | null;
  readonly error: string | null;
}

const TERMINAL: ReadonlySet<RunStatus> = new Set(['completed', 'stopped', 'failed', 'cancelled']);

export function isTerminal(status: RunStatus): boolean {
  return TERMINAL.has(status);
}

/** Polls one run every interval until it reaches a terminal status. */
export class RunTracker {
  private state: RunState = {run: null, error: null};
  private readonly listeners = new Set<() => void>();
  private controller = new AbortController();
  private timer: ReturnType<typeof setTimeout> | undefined;
  private polling = false;

  constructor(
    private readonly read: (signal: AbortSignal) => Promise<RunDetail>,
    private readonly interval = 1000,
  ) {}

  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  };

  readonly snapshot = (): RunState => this.state;

  start(): void {
    this.controller = new AbortController();
    void this.poll();
  }

  stop(): void {
    this.controller.abort();
    clearTimeout(this.timer);
  }

  refresh(): void {
    if (this.polling || this.controller.signal.aborted) return;
    clearTimeout(this.timer);
    void this.poll();
  }

  private async poll(): Promise<void> {
    const {signal} = this.controller;
    this.polling = true;
    try {
      const run = await this.read(signal);
      if (signal.aborted) return;
      this.update({run, error: null});
      if (isTerminal(run.status)) return;
    } catch (error) {
      if (signal.aborted) return;
      this.update({...this.state, error: errorMessage(error)});
    } finally {
      this.polling = false;
    }
    this.timer = setTimeout(() => {
      void this.poll();
    }, this.interval);
  }

  private update(state: RunState): void {
    this.state = state;
    for (const listener of this.listeners) listener();
  }
}
