export type Route =
  | {readonly kind: 'graphs'; readonly creating: boolean}
  | {readonly kind: 'editor'; readonly graphId: string}
  | {readonly kind: 'run'; readonly graphId: string; readonly runId: string}
  | {readonly kind: 'activity'; readonly graphId: string; readonly runId: string}
  | {readonly kind: 'runs'; readonly graphId: string | null}
  | {readonly kind: 'components'};

/** The section of the main navigation that a route belongs to. */
export type Section = 'graphs' | 'runs' | 'components';

export const GRAPHS: Route = {kind: 'graphs', creating: false};
const GRAPH_ID = /^[a-z][a-z0-9-]{0,63}$/u;
const RUN_ID = /^[\w.-]{1,128}$/u;
const SECTIONS: Readonly<Record<Route['kind'], Section>> = {
  graphs: 'graphs',
  editor: 'graphs',
  run: 'runs',
  activity: 'runs',
  runs: 'runs',
  components: 'components',
};

function decoded(part: string | undefined): string {
  try {
    return decodeURIComponent(part ?? '');
  } catch {
    return '';
  }
}

function runRoute(graphId: string, rest: readonly string[]): Route {
  const [run, activity, ...extra] = rest;
  const runId = decoded(run);
  if (!RUN_ID.test(runId) || extra.length > 0) return GRAPHS;
  if (activity === undefined) return {kind: 'run', graphId, runId};
  return activity === 'activity' ? {kind: 'activity', graphId, runId} : GRAPHS;
}

function graphRoute(graphId: string, rest: readonly string[]): Route {
  if (rest.length === 0) return {kind: 'editor', graphId};
  const [runs, ...runPath] = rest;
  if (runs !== 'runs') return GRAPHS;
  return runPath.length === 0 ? {kind: 'runs', graphId} : runRoute(graphId, runPath);
}

function graphsRoute(parts: readonly string[]): Route {
  const [graph, ...rest] = parts;
  if (graph === undefined || graph === '') return GRAPHS;
  if (graph === 'new' && rest.length === 0) return {kind: 'graphs', creating: true};
  const graphId = decoded(graph);
  return GRAPH_ID.test(graphId) ? graphRoute(graphId, rest) : GRAPHS;
}

/** The route of a location hash; unknown routes are the graph list. */
export function parseRoute(hash: string): Route {
  const [root, ...parts] = hash.replace(/^#?\/?/u, '').split('/');
  if (root === 'graphs') return graphsRoute(parts);
  if (parts.length > 0) return GRAPHS;
  if (root === 'runs') return {kind: 'runs', graphId: null};
  return root === 'components' ? {kind: 'components'} : GRAPHS;
}

function graphHash(graphId: string): string {
  return `#/graphs/${encodeURIComponent(graphId)}`;
}

function runsHash(graphId: string | null): string {
  return graphId === null ? '#/runs' : `${graphHash(graphId)}/runs`;
}

export function routeHash(route: Route): string {
  switch (route.kind) {
    case 'graphs':
      return route.creating ? '#/graphs/new' : '#/graphs';
    case 'editor':
      return graphHash(route.graphId);
    case 'run':
      return `${runsHash(route.graphId)}/${encodeURIComponent(route.runId)}`;
    case 'activity':
      return `${routeHash({...route, kind: 'run'})}/activity`;
    case 'runs':
      return runsHash(route.graphId);
    case 'components':
      return '#/components';
  }
}

/** The navigation section of a route: graph pages, run pages or the components page. */
export function routeSection(route: Route): Section {
  return SECTIONS[route.kind];
}

/** The graph whose editor a route shows: its editor, or one of its runs in run mode. */
function editorGraph(route: Route): string | null {
  return route.kind === 'editor' || route.kind === 'run' ? route.graphId : null;
}

/** Whether moving between two routes leaves the open editor. */
export function leavesEditor(current: Route, next: Route): boolean {
  const graph = editorGraph(current);
  return graph !== null && editorGraph(next) !== graph;
}
