import type {GraphReference, GraphSummary} from '../api/index.ts';
import {findSaved, readCatalog} from './catalog-requests.ts';
import {initialCatalog, mergePage, referenceKey, savedSelection} from './catalog-state.ts';
import type {CatalogPage, CatalogState} from './catalog-state.ts';

export class CatalogModel {
  private state = initialCatalog();
  private readonly listeners = new Set<() => void>();
  private active: AbortController | null = null;
  private searching = false;
  private readonly cursors = new Set<string>();
  constructor(private readonly credential: string | undefined) {}

  readonly snapshot = (): CatalogState => this.state;
  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  };

  readonly select = (key: string): void => {
    const canceledSearch = this.searching;
    if (this.searching) {
      this.dispose();
      this.searching = false;
    }
    const graph =
      this.state.graphs.find((item) => referenceKey(item) === key) ??
      (this.state.graph !== null && referenceKey(this.state.graph) === key
        ? this.state.graph
        : undefined);
    if (graph !== undefined)
      this.publish({
        ...this.state,
        graph,
        selectionBlocked: false,
        loading: canceledSearch ? false : this.state.loading,
      });
  };

  readonly refresh = async (): Promise<void> => {
    const controller = this.begin(false);
    this.cursors.clear();
    await this.page(controller, undefined, false);
  };

  readonly loadMore = async (): Promise<void> => {
    const cursor = this.state.nextCursor;
    if (cursor === null || this.state.loading) return;
    const controller = this.begin(false);
    await this.page(controller, cursor, true);
  };

  readonly recoverSaved = async (reference: GraphReference): Promise<void> => {
    const controller = this.begin(true);
    this.cursors.clear();
    this.publish({
      ...this.state,
      confirmedSaved: reference,
      needsSavedSelection: true,
      selectionBlocked: true,
    });
    try {
      const graph = await findSaved(
        reference,
        controller.signal,
        (cursor) => readCatalog(this.credential, controller.signal, cursor),
        (page, append) => {
          this.accept(page, append);
        },
      );
      this.foundSaved(controller, graph);
    } catch {
      this.failed(
        controller,
        'The saved definition is confirmed, but its library refresh failed. Retry to select it.',
      );
    }
  };

  readonly dispose = (): void => {
    this.active?.abort();
  };

  private begin(searching: boolean): AbortController {
    this.dispose();
    const controller = new AbortController();
    this.active = controller;
    this.searching = searching;
    this.publish({...this.state, loading: true, error: null});
    return controller;
  }

  private foundSaved(controller: AbortController, graph: GraphSummary | null): void {
    if (!this.current(controller)) return;
    this.searching = false;
    this.publish(savedSelection(this.state, graph));
  }

  private async page(
    controller: AbortController,
    cursor: string | undefined,
    append: boolean,
  ): Promise<void> {
    try {
      const page = await readCatalog(this.credential, controller.signal, cursor);
      if (!this.current(controller)) return;
      this.accept(page, append);
      this.publish({...this.state, loading: false});
    } catch {
      this.failed(
        controller,
        'Could not load the experiment library. Refresh to start a new listing.',
      );
    }
  }

  private accept(page: CatalogPage, append: boolean): void {
    if (page.next_cursor !== null && this.cursors.has(page.next_cursor))
      throw new Error('Repeated library cursor.');
    const graphs = mergePage(append ? this.state.graphs : [], page);
    if (page.next_cursor !== null) this.cursors.add(page.next_cursor);
    this.publish({
      ...this.state,
      graphs,
      nextCursor: page.next_cursor,
      graph: this.state.graph ?? graphs[0] ?? null,
    });
  }

  private current(controller: AbortController): boolean {
    return this.active === controller && !controller.signal.aborted;
  }

  private failed(controller: AbortController, error: string): void {
    if (!this.current(controller)) return;
    this.searching = false;
    this.publish({...this.state, error, loading: false});
  }

  private publish(state: CatalogState): void {
    this.state = state;
    for (const listener of this.listeners) listener();
  }
}
