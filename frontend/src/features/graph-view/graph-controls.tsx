import type {ReactElement} from 'react';
import type {GraphSettings} from './graph-settings.ts';

export function GraphControls(props: GraphSettings): ReactElement {
  return (
    <fieldset className="graph-controls">
      <legend>Graph view</legend>
      <ModeButtons {...props} />
      <div className="graph-options">
        <DisplayOption
          label="Show configuration"
          checked={props.configuration}
          onChange={props.onConfiguration}
        />
        <DisplayOption
          label="Show system elements"
          checked={props.system}
          onChange={props.onSystem}
        />
      </div>
    </fieldset>
  );
}
interface OptionProps {
  readonly label: string;
  readonly checked: boolean;
  readonly onChange: (value: boolean) => void;
}
function DisplayOption({label, checked, onChange}: OptionProps): ReactElement {
  return (
    <label>
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => {
          onChange(event.target.checked);
        }}
      />
      {label}
    </label>
  );
}
function ModeButtons(props: GraphSettings): ReactElement {
  return (
    <div className="actions">
      <button
        aria-pressed={!props.execution}
        onClick={() => {
          props.onMode(false);
        }}
      >
        Structure
      </button>
      <button
        aria-pressed={props.execution}
        onClick={() => {
          props.onMode(true);
        }}
      >
        Execution
      </button>
      <button onClick={props.onOrganize}>Reorganize graph</button>
    </div>
  );
}
