import {Transport} from './transport.ts';
import {
  activationSchema,
  branchCreatedSchema,
  branchListSchema,
  changeListSchema,
  changeRecordSchema,
  changeSavedSchema,
} from './schemas/changes.ts';
import type {
  Activation,
  BranchOrigin,
  ChangeQuery,
  ChangeRecord,
  ChangeSummary,
  CreatedBranch,
  SavedChange,
} from './schemas/changes.ts';
import {
  createdSchema,
  graphDetailSchema,
  graphListSchema,
  graphVersionSchema,
  validationSchema,
} from './schemas/graph.ts';
import type {
  Branch,
  CreatedGraph,
  Diagnostic,
  GraphDetail,
  GraphDocument,
  GraphSummary,
  GraphVersion,
} from './schemas/graph.ts';

const segment = encodeURIComponent;
const graphPath = (id: string, rest = ''): string => `/graphs/${segment(id)}${rest}`;

/** The graphs part of the operator API: graphs, branches, working-copy changes, versions. */
export class GraphClient {
  protected readonly transport: Transport;

  constructor(credential: string | null) {
    this.transport = new Transport(credential);
  }

  async validate(document: GraphDocument, signal?: AbortSignal): Promise<Diagnostic[]> {
    const options = {body: {document}, signal};
    return (await this.transport.read('/graphs/validate', validationSchema, 200, options))
      .diagnostics;
  }

  /** The graphs, most recently changed first. */
  async graphs(signal?: AbortSignal): Promise<GraphSummary[]> {
    return (await this.transport.read('/graphs', graphListSchema, 200, {signal})).graphs;
  }

  /** Stores a draft document as change 1 of branch `main`. */
  async createGraph(document: GraphDocument, signal?: AbortSignal): Promise<CreatedGraph> {
    return await this.transport.read('/graphs', createdSchema, 201, {body: {document}, signal});
  }

  async graph(id: string, signal?: AbortSignal): Promise<GraphDetail> {
    return await this.transport.read(graphPath(id), graphDetailSchema, 200, {signal});
  }

  /** The branches, oldest first. */
  async branches(id: string, signal?: AbortSignal): Promise<Branch[]> {
    const path = graphPath(id, '/branches');
    return (await this.transport.read(path, branchListSchema, 200, {signal})).branches;
  }

  async createBranch(
    id: string,
    name: string,
    from: BranchOrigin,
    signal?: AbortSignal,
  ): Promise<CreatedBranch> {
    const options = {body: {name, from}, signal};
    return await this.transport.read(graphPath(id, '/branches'), branchCreatedSchema, 201, options);
  }

  /** Saves a draft as the branch's next change; an unchanged document keeps the latest one. */
  async saveChange(
    id: string,
    branch: string,
    document: GraphDocument,
    signal?: AbortSignal,
  ): Promise<SavedChange> {
    const options = {body: {branch, document}, signal};
    return await this.transport.read(
      graphPath(id, '/changes'),
      changeSavedSchema,
      [200, 201],
      options,
    );
  }

  /** Changes newest first, of one branch or of every branch. */
  async changes(
    id: string,
    query: ChangeQuery = {},
    signal?: AbortSignal,
  ): Promise<ChangeSummary[]> {
    const search = new URLSearchParams();
    if (query.branch !== undefined) search.set('branch', query.branch);
    if (query.before !== undefined) search.set('before', String(query.before));
    if (query.limit !== undefined) search.set('limit', String(query.limit));
    const suffix = search.size > 0 ? `?${search.toString()}` : '';
    const path = graphPath(id, `/changes${suffix}`);
    return (await this.transport.read(path, changeListSchema, 200, {signal})).changes;
  }

  async change(id: string, change: number, signal?: AbortSignal): Promise<ChangeRecord> {
    const path = graphPath(id, `/changes/${String(change)}`);
    return await this.transport.read(path, changeRecordSchema, 200, {signal});
  }

  /** Activates a change as the next version on its branch. */
  async activate(id: string, change: number, signal?: AbortSignal): Promise<Activation> {
    const options = {body: {change}, signal};
    return await this.transport.read(graphPath(id, '/versions'), activationSchema, 201, options);
  }

  async version(id: string, version: number, signal?: AbortSignal): Promise<GraphVersion> {
    const path = graphPath(id, `/versions/${String(version)}`);
    return await this.transport.read(path, graphVersionSchema, 200, {signal});
  }
}
