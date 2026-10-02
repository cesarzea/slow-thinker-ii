import {expect, vi} from 'vitest';
import {fireEvent, render, waitFor} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import {z} from 'zod';
import {DefinitionClient} from '../../src/api/index.ts';
import type {GraphReference, LibraryPage} from '../../src/api/index.ts';
import {CatalogPanel} from '../../src/app/catalog-panel.tsx';
import {EditorClientFixture, draftText, numericSource, parentReference} from './editor-view.tsx';
import {libraryItem, libraryPage} from './catalog-data.ts';
import {OperatorServer} from './operator-server.ts';
import {singleDetail} from './projection-data.ts';

function sourceFor(reference: GraphReference): string {
  return reference.revision === parentReference.revision ? numericSource : draftText(reference);
}

export class CatalogFixture extends EditorClientFixture {
  readonly operator = new OperatorServer();
  readonly list = vi
    .spyOn(DefinitionClient.prototype, 'list')
    .mockResolvedValue(libraryPage([libraryItem()]));
  readonly detail = vi
    .spyOn(DefinitionClient.prototype, 'detail')
    .mockImplementation((reference) => {
      const definition: unknown = JSON.parse(sourceFor(reference));
      const parsed = z.record(z.string(), z.json()).parse(definition);
      return Promise.resolve({...singleDetail, ...reference, definition: parsed});
    });

  constructor(page: LibraryPage = libraryPage([libraryItem()])) {
    super();
    this.list.mockResolvedValue(page);
    this.source.mockImplementation((reference) => Promise.resolve(sourceFor(reference)));
    vi.stubGlobal('fetch', this.operator.fetch);
    render(<CatalogPanel credential="key" generation={0} />);
  }

  async ready(): Promise<void> {
    await waitFor(() => {
      expect(this.text.value).toBe(numericSource);
    });
    await screen.findByLabelText(/Task or problem/);
  }

  get text(): HTMLTextAreaElement {
    return screen.getByLabelText<HTMLTextAreaElement>(/Definition JSON/);
  }

  change(source: string): void {
    fireEvent.change(this.text, {target: {value: source}});
  }
}
