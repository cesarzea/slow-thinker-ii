import {act, renderHook, waitFor} from '@testing-library/react';
import {expect} from 'vitest';
import {useEditor} from '../../src/features/definition-editor/use-editor.ts';
import type {EditorModel} from '../../src/features/definition-editor/types.ts';
import {EditorClientFixture, parentReference} from './editor-view.tsx';

export class EditorModelFixture extends EditorClientFixture {
  readonly hook = renderHook(() =>
    useEditor({
      credential: 'key',
      reference: parentReference,
      onSaved: this.saved,
      onDirtyChange: this.dirty,
    }),
  );

  get model(): EditorModel {
    return this.hook.result.current;
  }

  async ready(): Promise<void> {
    await waitFor(() => {
      expect(this.model.state.loaded).toBe(true);
    });
  }

  async perform(action: (model: EditorModel) => unknown): Promise<void> {
    await act(async () => {
      await Promise.resolve(action(this.model));
    });
  }

  start(action: (model: EditorModel) => Promise<unknown>): void {
    act(() => {
      void action(this.model);
    });
  }
}

export async function attemptLockedActions(model: EditorModel): Promise<void> {
  model.edit('superseding text');
  model.discard();
  await Promise.all([
    model.validate(),
    model.save(),
    model.importFile(new File(['{}'], 'ignored.json')),
    model.derive('variant', 'ignored'),
  ]);
}
