import type {ReactElement} from 'react';
import type {ConfigurationCatalog} from '../../api/index.ts';
import {ModelInventory} from './inventory.tsx';
import {limitFields} from './limits-model.ts';
import type {LimitField} from './limits-model.ts';
import {useLimits} from './use-limits.ts';
import type {LimitsModel} from './use-limits.ts';

interface Props {
  readonly credential: string;
  readonly catalog: ConfigurationCatalog | null;
  readonly refresh: () => void;
}
export function ConfigurationSettings(props: Props): ReactElement {
  return (
    <section aria-label="Workspace settings">
      <h2>Settings</h2>
      <p>
        Trusted server ceilings bound every change. Changing a cap never resets settled or reserved
        spending.
      </p>
      <ModelInventory catalog={props.catalog} />
      {props.catalog === null ? (
        <p>Load configuration discovery to edit effective settings.</p>
      ) : (
        <LimitsSettings {...props} catalog={props.catalog} />
      )}
    </section>
  );
}
function LimitsSettings(props: Props & {readonly catalog: ConfigurationCatalog}): ReactElement {
  const model = useLimits(props.credential, props.catalog, props.refresh);
  return (
    <section aria-label="Effective limits">
      <h3>Deadlines and budgets</h3>
      <p>Editing configuration revision {model.state.revision}</p>
      <fieldset disabled={model.state.pending || model.state.uncertain}>
        <legend>Effective values</legend>
        <div className="schema-fields">
          {limitFields.map((field) => (
            <LimitInput
              key={field.name}
              {...{field, model}}
              maximum={props.catalog.limits.maximum[field.name]}
            />
          ))}
        </div>
      </fieldset>
      <LimitsActions model={model} />
      {model.state.message !== null && <p role="status">{model.state.message}</p>}
      {model.state.revision !== props.catalog.configuration_revision && (
        <p>
          The discovered revision differs. Load the latest limits before a new change if needed.
        </p>
      )}
    </section>
  );
}
function LimitInput({
  field,
  model,
  maximum,
}: {
  readonly field: LimitField;
  readonly model: LimitsModel;
  readonly maximum: number | string;
}): ReactElement {
  return (
    <label>
      {field.label}
      <input
        type="text"
        inputMode={field.budget ? 'decimal' : 'numeric'}
        value={model.state.edits[field.name] ?? String(model.state.current[field.name])}
        onChange={(event) => {
          model.edit(field.name, event.target.value);
        }}
      />
      <span>Server ceiling: {maximum}</span>
    </label>
  );
}
function LimitsActions({model}: {readonly model: LimitsModel}): ReactElement {
  const disabled = model.state.pending || model.state.uncertain;
  return (
    <div className="actions">
      <button
        disabled={disabled || Object.keys(model.state.edits).length === 0}
        onClick={() => {
          void model.submit();
        }}
      >
        Apply settings
      </button>
      <button disabled={disabled} onClick={model.useLatest}>
        Use latest server limits
      </button>
      {model.state.pending && <p role="status">Saving settings…</p>}
      {model.state.uncertain && (
        <button
          onClick={() => {
            void model.replay();
          }}
        >
          Replay unchanged settings command
        </button>
      )}
    </div>
  );
}
