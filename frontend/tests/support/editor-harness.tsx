import {render, screen, waitFor} from '@testing-library/react';
import {vi} from 'vitest';
import type {Mock} from 'vitest';
import {OperatorClient} from '../../src/api/index.ts';
import type {Diagnostic, GraphDocument} from '../../src/api/index.ts';
import {Editor} from '../../src/features/editor/index.ts';
import type {DraftModel} from '../../src/features/editor/index.ts';
import type {FakeApi} from './fake-api.ts';
import {graphServer} from './graph-server.ts';
import type {Validator} from './graph-server.ts';

export type {Validator} from './graph-server.ts';

export interface EditorHarness {
  readonly api: FakeApi;
  readonly onDraft: Mock<(model: DraftModel | null) => void>;
  readonly draft: () => DraftModel;
}

export const missingModel = (document: GraphDocument): Diagnostic[] =>
  document.nodes.flatMap((node, index) =>
    node.component.startsWith('llm-call@') && node.config['model'] === null
      ? [
          {
            severity: 'error' as const,
            code: 'service_not_selected',
            message: 'Select a model.',
            path: `/nodes/${String(index)}/config/model`,
            node_id: node.id,
          },
        ]
      : [],
  );

/** A fake operator API serving one graph, stored with one active version or not stored yet. */
export function editorApi(
  graphId: string,
  saved: GraphDocument | null,
  validator: Validator = () => [],
): FakeApi {
  return graphServer(graphId, saved, validator).api.install();
}

/** Render the editor of a graph and wait until its canvas is shown. */
export async function renderEditor(
  api: FakeApi,
  graphId: string,
  created: GraphDocument | null = null,
): Promise<EditorHarness> {
  const onDraft = vi.fn<(model: DraftModel | null) => void>();
  render(
    <div style={{width: '1200px', height: '800px'}}>
      <Editor
        client={new OperatorClient('credential')}
        graphId={graphId}
        created={created}
        onDraft={onDraft}
      />
    </div>,
  );
  await screen.findByRole('button', {name: 'Add Trigger'});
  await measured();
  await settled();
  const draft = (): DraftModel => {
    const model = onDraft.mock.calls.findLast((call) => call[0] !== null)?.[0];
    if (model === undefined || model === null) throw new Error('No draft model');
    return model;
  };
  return {api, onDraft, draft};
}

/** The header's save status: “Saving…”, “Saved”, and how far it is from the active version. */
export function toolbarStatus(): string {
  return screen.getAllByRole('status')[0]?.textContent ?? '';
}

/** Wait until the debounced validation of the current document has been applied. */
export async function settled(): Promise<void> {
  await waitFor(
    () => {
      if (screen.queryByText('Checking…') !== null) throw new Error('Still checking');
    },
    {timeout: 3000},
  );
}

/** Wait until the autosave has stored the latest edit. */
export async function saved(): Promise<void> {
  await waitFor(
    () => {
      if (!toolbarStatus().startsWith('Saved')) throw new Error('Still saving');
    },
    {timeout: 3000},
  );
}

/** Wait until React Flow has measured every node, which makes the cards visible. */
async function measured(): Promise<void> {
  await waitFor(() => {
    const hidden = [...document.querySelectorAll<HTMLElement>('.react-flow__node')].some(
      (node) => node.style.visibility === 'hidden',
    );
    if (hidden) throw new Error('Nodes are still being measured');
  });
}
