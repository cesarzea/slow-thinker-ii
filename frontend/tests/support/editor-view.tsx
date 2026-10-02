import {vi, expect} from 'vitest';
import {fireEvent, render, waitFor} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import type {ReactElement} from 'react';
import {z} from 'zod';
import {DefinitionClient} from '../../src/api/index.ts';
import type {GraphReference} from '../../src/api/index.ts';
import {DefinitionEditor} from '../../src/features/definition-editor/index.tsx';
import {singleDetail} from './projection-data.ts';

export const parentReference = {graph_id: 'single-agent', revision: 'example-2'};
export const personalReference = {graph_id: 'single-agent', revision: 'personal-1'};
export const numericSource = JSON.stringify(singleDetail.definition).replace(
  '"parameters":{}',
  '"parameters":{"temperature":1.0,"seed":9007199254740993}',
);

function identity(source: string): GraphReference {
  const value: unknown = JSON.parse(source);
  return z.object({graph_id: z.string(), revision: z.string()}).parse(value);
}

export function draftText(target = personalReference, parent = parentReference): string {
  const source = numericSource
    .replace('"graph_id":"single-agent"', `"graph_id":${JSON.stringify(target.graph_id)}`)
    .replace('"revision":"example-2"', `"revision":${JSON.stringify(target.revision)}`);
  return `{"derived_from":${JSON.stringify(parent)},${source.slice(1)}`;
}

export class EditorClientFixture {
  readonly saved = vi.fn<(reference: GraphReference) => void>();
  readonly dirty = vi.fn<(dirty: boolean) => void>();
  readonly source = vi.spyOn(DefinitionClient.prototype, 'source').mockResolvedValue(numericSource);
  readonly draft = vi.spyOn(DefinitionClient.prototype, 'draft').mockResolvedValue(draftText());
  readonly validate = vi
    .spyOn(DefinitionClient.prototype, 'validate')
    .mockImplementation((source) =>
      Promise.resolve({...identity(source), validation_scope: 'definition'}),
    );
  readonly save = vi
    .spyOn(DefinitionClient.prototype, 'save')
    .mockImplementation((source) => Promise.resolve({...identity(source), created: true}));
}

export class EditorFixture extends EditorClientFixture {
  readonly view = render(this.element(parentReference, 'key'));

  async ready(): Promise<void> {
    await waitFor(() => {
      expect(this.text.value).toBe(numericSource);
    });
  }

  get text(): HTMLTextAreaElement {
    return screen.getByLabelText<HTMLTextAreaElement>(/Definition JSON/);
  }

  change(source: string): void {
    fireEvent.change(this.text, {target: {value: source}});
  }

  select(reference: GraphReference, credential = 'key'): void {
    this.view.rerender(this.element(reference, credential));
  }

  element(reference: GraphReference, credential: string): ReactElement {
    return (
      <DefinitionEditor
        credential={credential}
        reference={reference}
        onSaved={this.saved}
        onDirtyChange={this.dirty}
      />
    );
  }
}

export async function press(name: string): Promise<void> {
  await userEvent.click(screen.getByRole('button', {name}));
}

export function disabled(name: string): boolean {
  const button = screen.getByRole<HTMLButtonElement>('button', {name});
  return button.disabled || button.closest('fieldset')?.disabled === true;
}

export function importFile(bytes: Uint8Array, name = 'experiment.json'): File {
  const file = new File([bytes.slice().buffer], name, {type: 'application/json'});
  Object.defineProperty(file, 'arrayBuffer', {value: () => Promise.resolve(bytes.slice().buffer)});
  return file;
}
