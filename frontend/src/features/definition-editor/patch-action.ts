import type {DefinitionClient, PatchOperation} from '../../api/index.ts';
import {changeSource, locked, MAX_SOURCE_BYTES, sourceSize, rejected} from './draft.ts';
import type {DraftState, Requests, UpdateDraft} from './types.ts';

export function patchAction(
  state: DraftState,
  client: DefinitionClient,
  requests: Requests,
  update: UpdateDraft,
): (operations: readonly PatchOperation[]) => Promise<void> {
  return async (operations) => {
    if (locked(state) || state.pending !== null) return;
    const source = state.source;
    const controller = requests.begin();
    update((draft) => ({...draft, pending: 'patch', validation: null, message: null, issues: []}));
    try {
      const patched = await client.patch(source, operations, controller.signal);
      if (controller.signal.aborted) return;
      if (sourceSize(patched) > MAX_SOURCE_BYTES)
        throw new Error('Patch exceeds the editor bound.');
      update((draft) => (draft.source === source ? changeSource(draft, patched) : draft));
    } catch (error) {
      if (!controller.signal.aborted)
        update((draft) =>
          rejected(
            draft,
            error,
            'Could not apply configuration changes. The previous source is preserved.',
          ),
        );
    }
  };
}
