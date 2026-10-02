import type {ReactElement} from 'react';
import {locked} from './draft.ts';
import type {EditorModel} from './types.ts';

export function EditorActions({model}: {readonly model: EditorModel}): ReactElement {
  const {state} = model;
  return (
    <>
      <ImportControl model={model} />
      <DraftButtons model={model} />
      {state.uncertain && (
        <EditorButton
          disabled={state.pending !== null}
          action={model.retry}
          label="Retry same save"
        />
      )}
      {!state.loaded && state.pending === null && (
        <EditorButton
          disabled={false}
          action={model.reload}
          label="Retry loading saved definition"
        />
      )}
    </>
  );
}

function DraftButtons({model}: {readonly model: EditorModel}): ReactElement {
  const {state} = model;
  return (
    <div className="actions">
      <EditorButton
        disabled={locked(state) || state.pending !== null}
        action={model.validate}
        label="Validate definition"
      />
      <EditorButton
        disabled={locked(state) || state.pending !== null || state.validation === null}
        action={model.save}
        label="Save definition"
      />
      <EditorButton
        disabled={
          !state.loaded ||
          state.pending === 'save' ||
          state.pending === 'import' ||
          state.pending === 'draft'
        }
        action={model.discard}
        label="Discard draft"
      />
    </div>
  );
}

function EditorButton({
  disabled,
  action,
  label,
}: {
  readonly disabled: boolean;
  readonly action: () => void | Promise<void>;
  readonly label: string;
}): ReactElement {
  return (
    <button
      disabled={disabled}
      onClick={() => {
        void action();
      }}
    >
      {label}
    </button>
  );
}

function ImportControl({model}: {readonly model: EditorModel}): ReactElement {
  return (
    <label>
      Import UTF-8 JSON file
      <input
        type="file"
        accept=".json,application/json"
        disabled={locked(model.state)}
        onChange={(event) => {
          const file = event.target.files?.[0];
          event.target.value = '';
          if (file !== undefined) void model.importFile(file);
        }}
      />
    </label>
  );
}
