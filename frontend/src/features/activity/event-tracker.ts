import {EVENT_PAGE_LIMIT, errorMessage} from '../../api/index.ts';
import type {EventPage, RunEvent} from '../../api/index.ts';

export interface EventsState {
  readonly events: readonly RunEvent[];
  readonly finished: boolean;
  readonly error: string | null;
}
type ReadPage = (after: number, signal: AbortSignal) => Promise<EventPage>;

/** Reads a run's events page by page until the log is finished, polling while it is active. */
export class EventTracker {
  private state: EventsState = {events: [], finished: false, error: null};
  private readonly listeners = new Set<() => void>();
  private controller = new AbortController();
  private timer: ReturnType<typeof setTimeout> | undefined;

  constructor(
    private readonly read: ReadPage,
    private readonly interval = 1000,
  ) {}

  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  };

  readonly snapshot = (): EventsState => this.state;

  start(): void {
    this.controller = new AbortController();
    void this.poll();
  }

  stop(): void {
    this.controller.abort();
    clearTimeout(this.timer);
  }

  private async poll(): Promise<void> {
    const {signal} = this.controller;
    const after = this.state.events.at(-1)?.seq ?? 0;
    try {
      const page = await this.read(after, signal);
      if (!signal.aborted) this.accept(page, after);
    } catch (error) {
      if (signal.aborted) return;
      this.update({...this.state, error: errorMessage(error)});
      this.schedule(this.interval);
    }
  }

  private accept(page: EventPage, after: number): void {
    const full = page.events.length >= EVENT_PAGE_LIMIT;
    const finished = page.finished && !full;
    const events = [...this.state.events, ...page.events.filter((event) => event.seq > after)];
    this.update({events, finished, error: null});
    if (!finished) this.schedule(full ? 0 : this.interval);
  }

  private schedule(delay: number): void {
    this.timer = setTimeout(() => {
      void this.poll();
    }, delay);
  }

  private update(state: EventsState): void {
    this.state = state;
    for (const listener of this.listeners) listener();
  }
}
