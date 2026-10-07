import {errorMessage} from '../../../api/index.ts';
import type {GraphDocument, OperatorClient} from '../../../api/index.ts';

/** Where the working copy is saved: the graph, once created, and the branch shown. */
export interface SaveTarget {
  readonly graphId: string;
  readonly branch: string;
  /** False for a graph created on the graphs page and not stored yet. */
  readonly exists: boolean;
}

/** The latest change stored for the branch, and the document revision it holds. */
export interface StoredChange {
  readonly change: number;
  readonly at: string;
  readonly revision: number;
}

export type SaveEvent =
  | {readonly kind: 'saving'}
  | ({readonly kind: 'stored'} & StoredChange)
  | {readonly kind: 'failed'; readonly message: string};

/** Edits are saved this long after the last one. */
const AUTOSAVE_DELAY_MS = 600;

interface Wanted {
  readonly document: GraphDocument;
  readonly revision: number;
}

/**
 * Saves the working copy as changes of its branch, one save at a time: the latest document
 * wins, a failed save is kept for a retry, and the first save of a new graph creates it.
 */
export class Autosaver {
  private wanted: Wanted | null = null;
  private timer: number | undefined;
  private running: Promise<void> = Promise.resolve();
  private target: SaveTarget;
  private last: StoredChange | null;

  constructor(
    private readonly client: OperatorClient,
    start: {readonly target: SaveTarget; readonly stored: StoredChange | null},
    private readonly report: (event: SaveEvent) => void,
  ) {
    this.target = start.target;
    this.last = start.stored;
  }

  /** The latest change stored, once every save in progress has finished. */
  get latest(): StoredChange | null {
    return this.last;
  }

  /** Save this document after the autosave delay, unless a newer one replaces it. */
  schedule(document: GraphDocument, revision: number): void {
    this.wanted = {document, revision};
    window.clearTimeout(this.timer);
    this.timer = window.setTimeout(() => {
      void this.flush();
    }, AUTOSAVE_DELAY_MS);
  }

  /** Save what is waiting now, after any save in progress; true when nothing is left. */
  async flush(): Promise<boolean> {
    window.clearTimeout(this.timer);
    this.running = this.running.then(async () => this.saveWanted());
    await this.running;
    return this.wanted === null;
  }

  private async saveWanted(): Promise<void> {
    const wanted = this.wanted;
    if (wanted === null) return;
    this.wanted = null;
    this.report({kind: 'saving'});
    try {
      const stored = {...(await this.store(wanted.document)), revision: wanted.revision};
      this.last = stored;
      this.report({kind: 'stored', ...stored});
    } catch (error) {
      this.wanted ??= wanted;
      this.report({kind: 'failed', message: errorMessage(error)});
    }
  }

  private async store(document: GraphDocument): Promise<{change: number; at: string}> {
    const {graphId, branch, exists} = this.target;
    if (exists) return await this.client.saveChange(graphId, branch, document);
    const created = await this.client.createGraph(document);
    this.target = {graphId: created.id, branch: created.branch, exists: true};
    return {change: created.change, at: new Date().toISOString()};
  }
}
