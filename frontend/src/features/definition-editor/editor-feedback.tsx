import type {ReactElement} from 'react';
import type {DraftState} from './types.ts';

export function EditorFeedback({state}: {readonly state: DraftState}): ReactElement {
  return (
    <>
      {state.pending !== null && <p role="status">{pendingLabel(state.pending)}</p>}
      {state.message !== null && <p role="status">{state.message}</p>}
      {state.issues.length > 0 && (
        <ul aria-label="Definition validation issues">
          {state.issues.map((issue, index) => (
            <li key={JSON.stringify([issue.pointer, index])}>
              <code>{issue.pointer || '/'}</code>: {issue.message}
            </li>
          ))}
        </ul>
      )}
      {state.validation !== null && (
        <p role="status">
          Definition validation passed for {state.validation.graph_id} · {state.validation.revision}
          . Run inputs, policies, budgets and availability are checked again before execution.
        </p>
      )}
      {!state.uncertain && state.validation === null && (
        <p>Validate the current text before saving. Saving creates an immutable definition.</p>
      )}
    </>
  );
}

function pendingLabel(pending: NonNullable<DraftState['pending']>): string {
  const labels = {
    load: 'Loading saved definition…',
    validate: 'Validating definition…',
    save: 'Saving frozen definition…',
    import: 'Reading UTF-8 JSON file…',
    draft: 'Creating revision draft…',
    patch: 'Applying configuration changes…',
  };
  return labels[pending];
}
