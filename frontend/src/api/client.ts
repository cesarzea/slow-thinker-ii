import {GraphClient} from './graph-client.ts';
import {Transport} from './transport.ts';
import {accessSchema} from './schemas/access.ts';
import type {Access} from './schemas/access.ts';
import {catalogSchema} from './schemas/catalog.ts';
import type {Catalog} from './schemas/catalog.ts';
import type {GraphDocument} from './schemas/graph.ts';
import {
  runDetailSchema,
  runListSchema,
  startedSchema,
  stoppedSchema,
  usageSchema,
} from './schemas/runs.ts';
import type {RunDetail, RunStatus, RunSummary, Usage} from './schemas/runs.ts';
import {eventPageSchema} from './schemas/events.ts';
import type {EventPage} from './schemas/events.ts';
import type {JsonValue} from './schemas/json.ts';

export const EVENT_PAGE_LIMIT = 500;
const EVENT_PAGE_BYTES = 67_108_864;

const segment = encodeURIComponent;

/**
 * Validated access to the operator API, version 2: the graph methods of `GraphClient`,
 * the catalog, runs and usage. A `null` credential sends no Authorization header, for a
 * server without operator authentication.
 */
/** What a run executes: an activated version, or a change of the working copy. */
export type RunSource = {readonly version: number} | {readonly change: number};

export class OperatorClient extends GraphClient {
  /** Whether the server needs the operator token; this request never sends one. */
  async access(signal?: AbortSignal): Promise<Access> {
    return await new Transport(null).read('/access', accessSchema, 200, {signal});
  }

  async catalog(signal?: AbortSignal): Promise<Catalog> {
    return await this.transport.read('/catalog', catalogSchema, 200, {signal});
  }

  async startRun(
    graphId: string,
    source: RunSource,
    input: JsonValue,
    signal?: AbortSignal,
  ): Promise<string> {
    const body = {graph_id: graphId, ...source, input};
    return (await this.transport.read('/runs', startedSchema, 202, {body, signal})).run_id;
  }

  /** The document a run executed: its version's, or its change's when never activated. */
  async runDocument(run: RunSummary, signal?: AbortSignal): Promise<GraphDocument> {
    const {graph_id: graphId, version, change} = run;
    const source =
      version === null
        ? await this.change(graphId, change, signal)
        : await this.version(graphId, version, signal);
    return source.document;
  }

  async runs(graphId?: string, signal?: AbortSignal): Promise<RunSummary[]> {
    const query = new URLSearchParams({limit: '100'});
    if (graphId !== undefined) query.set('graph_id', graphId);
    const path = `/runs?${query.toString()}`;
    return (await this.transport.read(path, runListSchema, 200, {signal})).runs;
  }

  async run(runId: string, signal?: AbortSignal): Promise<RunDetail> {
    return await this.transport.read(`/runs/${segment(runId)}`, runDetailSchema, 200, {signal});
  }

  async events(runId: string, after: number, signal?: AbortSignal): Promise<EventPage> {
    const query = new URLSearchParams({after: String(after), limit: String(EVENT_PAGE_LIMIT)});
    const path = `/runs/${segment(runId)}/events?${query.toString()}`;
    const options = {signal, maxBytes: EVENT_PAGE_BYTES};
    return await this.transport.read(path, eventPageSchema, 200, options);
  }

  async stopRun(runId: string, signal?: AbortSignal): Promise<RunStatus> {
    const path = `/runs/${segment(runId)}/stop`;
    return (await this.transport.read(path, stoppedSchema, 202, {body: {}, signal})).status;
  }

  async usage(signal?: AbortSignal): Promise<Usage> {
    return await this.transport.read('/usage', usageSchema, 200, {signal});
  }
}
