import type {ExecutionPage, GraphDetail, OperatorClient, Run} from '../../api/index.ts';

export interface ExecutionProjection {
  readonly detail: GraphDetail | null;
  readonly execution: ExecutionPage | null;
  readonly projectionError: string | null;
}
export interface ExecutionObservation extends ExecutionProjection {
  readonly run: Run | null;
  readonly stale: boolean;
}
export const emptyProjection: ExecutionProjection = {
  detail: null,
  execution: null,
  projectionError: null,
};

export class ProjectionReader {
  private definition: GraphDetail | null = null;
  private pending: ExecutionPage | null = null;
  private visible: ExecutionPage | null = null;
  private runId = '';
  private readonly cursors = new Set<string>();

  constructor(private readonly client: OperatorClient) {}

  async read(run: Run, signal: AbortSignal): Promise<ExecutionProjection> {
    this.selectRun(run.run_id);
    this.definition ??= await this.client.definition(run.run_id, signal);
    validateDefinitionRun(this.definition, run);
    const cursor = this.pending?.next_cursor ?? undefined;
    const page = await this.client.execution(run.run_id, signal, cursor);
    if (signal.aborted) return emptyProjection;
    validatePageRun(page, run);
    this.validateFreshPage(page);
    this.pending = appendPage(cursor === undefined ? null : this.pending, page);
    this.checkCursor(page.next_cursor);
    const result = {detail: this.definition, execution: this.publish(), projectionError: null};
    if (page.next_cursor === null) this.cursors.clear();
    return result;
  }

  reset(): void {
    this.definition = null;
    this.pending = null;
    this.visible = null;
    this.cursors.clear();
  }
  private validateFreshPage(page: ExecutionPage): void {
    const visible = this.visible;
    if (
      visible !== null &&
      page.backend_generation === visible.backend_generation &&
      page.through_sequence < visible.through_sequence
    ) {
      throw new Error('La instantánea es anterior a la evidencia ya mostrada.');
    }
  }
  private publish(): ExecutionPage | null {
    if (this.pending?.next_cursor === null || this.visible?.next_cursor !== null) {
      this.visible = this.pending;
    }
    return this.visible;
  }
  private selectRun(id: string): void {
    if (this.runId === id) return;
    this.runId = id;
    this.reset();
  }
  private checkCursor(cursor: string | null): void {
    if (cursor === null) return;
    if (this.cursors.has(cursor)) throw new Error('El servidor repite una página de ejecución.');
    this.cursors.add(cursor);
  }
}
function appendPage(previous: ExecutionPage | null, page: ExecutionPage): ExecutionPage {
  if (previous === null) return page;
  if (
    previous.through_sequence !== page.through_sequence ||
    previous.backend_generation !== page.backend_generation
  ) {
    throw new Error('La página pertenece a otra instantánea.');
  }
  const activations = [...previous.activations, ...page.activations];
  const calls = [...previous.calls, ...page.calls];
  if (
    new Set(activations.map((item) => item.id)).size !== activations.length ||
    new Set(calls.map((item) => item.id)).size !== calls.length
  )
    throw new Error('La instantánea contiene identidades repetidas.');
  return {...page, activations, calls};
}

function validatePageRun(page: ExecutionPage, run: Run): void {
  if (
    page.graph_revision !== run.graph_revision ||
    page.backend_generation !== run.backend_generation
  ) {
    throw new Error('La proyección corresponde a otra revisión o servidor.');
  }
}

function validateDefinitionRun(definition: GraphDetail, run: Run): void {
  if (definition.graph_id !== run.graph_id || definition.revision !== run.graph_revision) {
    throw new Error('Definición incompatible con la ejecución.');
  }
}
