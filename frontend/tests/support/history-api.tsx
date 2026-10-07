import {render} from '@testing-library/react';
import {vi} from 'vitest';
import {OperatorClient} from '../../src/api/index.ts';
import type {GraphDocument} from '../../src/api/index.ts';
import {HistoryPanel} from '../../src/features/versions/index.ts';
import {catalogBody, copy, j1} from './contract.ts';
import {FakeApi} from './fake-api.ts';

const path = '/graphs/funny-story';
const at = (minute: number): string => `2026-10-04T10:${String(minute).padStart(2, '0')}:00.000Z`;

function document(change: (draft: GraphDocument) => void): GraphDocument {
  const draft = copy(j1);
  change(draft);
  return draft;
}

/** The documents of changes 1 to 5 of branch main. */
export const documents: Record<number, GraphDocument> = {
  1: document((draft) => {
    draft.nodes = draft.nodes.filter((node) => node.id !== 'result');
    draft.connections = draft.connections.filter((link) => link.to !== 'result.in');
  }),
  2: copy(j1),
  3: document((draft) => {
    draft.layout = {...draft.layout, story: [40, 100]};
  }),
  4: document((draft) => {
    draft.layout = {...draft.layout, story: [40, 100]};
    const proposer = draft.nodes.find((node) => node.id === 'proposer');
    if (proposer !== undefined) proposer.config['prompt'] = 'Shorter, please.';
  }),
};
documents[5] = {...copy(documents[4] ?? j1), limits: {...j1.limits, max_activations: 30}};

const branch = (name: string, latest: number, head: number | null, from: number | null) => ({
  name,
  created_at: at(0),
  from_version: from,
  from_change: null,
  latest_change: latest,
  head_version: head,
});
const versionOf = (version: number, change: number, parent: number | null) => ({
  version,
  branch: 'main',
  parent,
  change,
  name: 'Funny story',
  created_at: at(change * 5),
});
const detail = {
  id: 'funny-story',
  name: 'Funny story',
  active_version: 2,
  latest_change: 6,
  branches: [branch('main', 5, 2, null), branch('draft', 6, null, 1)],
  versions: [versionOf(1, 2, null), versionOf(2, 4, 1)],
};
const ACTIVATED: Readonly<Record<number, number>> = {2: 1, 4: 2};
/** Branch main's changes, newest first; 2 and 4 were activated as versions 1 and 2. */
const changes = [5, 4, 3, 2, 1].map((change) => ({
  change,
  branch: 'main',
  at: at(change * 5),
  name: 'Funny story',
  version: ACTIVATED[change] ?? null,
}));

function serveChanges(api: FakeApi): void {
  for (const [change, body] of Object.entries(documents)) {
    const record = {graph_id: 'funny-story', branch: 'main', at: at(1), version: null};
    api.on(`GET ${path}/changes/${change}`, {
      status: 200,
      body: {...record, change: Number(change), document: body},
    });
  }
}

/** A fake API holding the history of graph funny-story. */
export function historyApi(): FakeApi {
  const api = new FakeApi()
    .on('GET /catalog', {status: 200, body: catalogBody})
    .on(`GET ${path}`, {status: 200, body: detail})
    .on(`GET ${path}/changes`, {status: 200, body: {changes}})
    .on(`GET ${path}/versions/1`, {
      status: 200,
      body: {
        graph_id: 'funny-story',
        version: 1,
        branch: 'main',
        parent: null,
        change: 2,
        created_at: at(10),
        document: documents[2],
      },
    })
    .on(`POST ${path}/changes`, {status: 201, body: {change: 7, at: at(40)}})
    .on(`POST ${path}/versions`, {status: 201, body: {version: 3, branch: 'main', change: 7}})
    .on(`POST ${path}/branches`, {status: 201, body: {name: 'Experiment', change: 8}});
  serveChanges(api);
  return api.install();
}

/** Renders the panel on branch main with spies for every request it makes of the editor. */
export function renderPanel(): Record<
  'onRestore' | 'onBranchChange' | 'onActivated' | 'onClose' | 'renderGraph',
  ReturnType<typeof vi.fn>
> {
  const spies = {
    onRestore: vi.fn(),
    onBranchChange: vi.fn(),
    onActivated: vi.fn(),
    onClose: vi.fn(),
    renderGraph: vi.fn(() => <p>Read-only canvas</p>),
  };
  render(
    <HistoryPanel
      client={new OperatorClient('credential')}
      graphId="funny-story"
      branch="main"
      latestChange={5}
      activeVersion={2}
      {...spies}
    />,
  );
  return spies;
}
