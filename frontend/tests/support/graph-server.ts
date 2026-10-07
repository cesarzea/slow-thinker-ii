import type {Diagnostic, GraphDocument} from '../../src/api/index.ts';
import {FakeApi, failure} from './fake-api.ts';
import type {ApiCall, Reply} from './fake-api.ts';
import {catalogBody} from './contract.ts';

const AT = '2026-10-04T10:42:00.000Z';

export type Validator = (document: GraphDocument) => Diagnostic[];

/** One graph on branch `main`: its changes, versions and the active one. */
export interface GraphState {
  changes: GraphDocument[];
  /** Version n holds change versions[n - 1]. */
  versions: number[];
}

function detail(id: string, state: GraphState): Record<string, unknown> {
  const latest = state.changes.length;
  const active = state.versions.length === 0 ? null : state.versions.length;
  return {
    id,
    name: state.changes.at(-1)?.name ?? id,
    active_version: active,
    latest_change: latest,
    branches: [
      {
        name: 'main',
        created_at: AT,
        from_version: null,
        from_change: null,
        latest_change: latest,
        head_version: active,
      },
    ],
    versions: state.versions.map((change, index) => ({
      version: index + 1,
      branch: 'main',
      parent: index === 0 ? null : index,
      change,
      name: state.changes[change - 1]?.name ?? id,
      created_at: AT,
    })),
  };
}

function versionOf(state: GraphState, change: number): number | null {
  const index = state.versions.indexOf(change);
  return index < 0 ? null : index + 1;
}

function changeRecord(id: string, state: GraphState, call: ApiCall): Reply {
  const change = Number(call.path.split('/').at(-1));
  const document = state.changes[change - 1];
  if (document === undefined) return failure(404, 'change_not_found', 'No change.');
  const version = versionOf(state, change);
  return {status: 200, body: {graph_id: id, change, branch: 'main', at: AT, document, version}};
}

function changeList(state: GraphState): Reply {
  const changes = state.changes
    .map((document, index) => ({
      change: index + 1,
      branch: 'main',
      at: AT,
      name: document.name,
      version: versionOf(state, index + 1),
    }))
    .reverse();
  return {status: 200, body: {changes}};
}

function saveChange(state: GraphState, call: ApiCall): Reply {
  const {document} = call.body as {document: GraphDocument};
  const same = JSON.stringify(state.changes.at(-1)) === JSON.stringify(document);
  if (!same) state.changes.push(document);
  return {status: same ? 200 : 201, body: {change: state.changes.length, at: AT}};
}

function activate(state: GraphState, call: ApiCall): Reply {
  const {change} = call.body as {change: number};
  state.versions.push(change);
  return {status: 201, body: {version: state.versions.length, branch: 'main', change}};
}

function versionRecord(id: string, state: GraphState, version: number): Reply {
  const change = state.versions[version - 1];
  const document = change === undefined ? undefined : state.changes[change - 1];
  if (change === undefined || document === undefined)
    return failure(404, 'version_not_found', 'No version.');
  const parent = version === 1 ? null : version - 1;
  return {
    status: 200,
    body: {graph_id: id, version, branch: 'main', parent, change, created_at: AT, document},
  };
}

function graphRoutes(api: FakeApi, graphId: string, state: GraphState): void {
  const base = `/graphs/${graphId}`;
  const exists = (answer: () => Reply) => (): Reply =>
    state.changes.length === 0 ? failure(404, 'graph_not_found', 'No graph.') : answer();
  api
    .on(
      `GET ${base}`,
      exists(() => ({status: 200, body: detail(graphId, state)})),
    )
    .on(
      `GET ${base}/changes`,
      exists(() => changeList(state)),
    )
    .on(`POST ${base}/changes`, (call) => saveChange(state, call))
    .on(`POST ${base}/versions`, (call) => activate(state, call));
  for (let change = 1; change <= 50; change += 1)
    api.on(`GET ${base}/changes/${String(change)}`, (call) => changeRecord(graphId, state, call));
  for (let version = 1; version <= 10; version += 1)
    api.on(`GET ${base}/versions/${String(version)}`, () => versionRecord(graphId, state, version));
}

/**
 * A fake operator API serving one graph: stored with one change and one active version, or
 * not stored yet. Saves, creation and activation update it.
 */
export function graphServer(
  graphId: string,
  saved: GraphDocument | null,
  validator: Validator = () => [],
): {api: FakeApi; state: GraphState} {
  const state: GraphState = {
    changes: saved === null ? [] : [saved],
    versions: saved === null ? [] : [1],
  };
  const api = new FakeApi()
    .on('GET /catalog', {status: 200, body: catalogBody})
    .on('POST /graphs/validate', (call) => ({
      status: 200,
      body: {diagnostics: validator((call.body as {document: GraphDocument}).document)},
    }))
    .on('POST /graphs', (call) => {
      state.changes.push((call.body as {document: GraphDocument}).document);
      return {status: 201, body: {id: graphId, branch: 'main', change: 1}};
    });
  graphRoutes(api, graphId, state);
  return {api, state};
}
