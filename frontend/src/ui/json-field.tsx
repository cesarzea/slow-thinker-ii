import {useState} from 'react';
import type {ReactElement} from 'react';
import type {PatchOperation} from '../api/index.ts';

export interface SourceFieldProps {
  readonly label: string;
  readonly path: string;
  readonly raw: string | undefined;
  readonly disabled: boolean;
  readonly patch: (operations: readonly PatchOperation[]) => Promise<void>;
}

export function JsonField(props: SourceFieldProps): ReactElement {
  return <ValueField key={JSON.stringify([props.path, props.raw])} {...props} />;
}
function ValueField(props: SourceFieldProps): ReactElement {
  const [value, setValue] = useState(props.raw ?? 'null');
  const [error, setError] = useState<string | null>(null);
  const apply = (): void => {
    try {
      JSON.parse(value);
      setError(null);
      void props.patch([
        {op: props.raw === undefined ? 'add' : 'replace', path: props.path, value_json: value},
      ]);
    } catch {
      setError('Enter a valid JSON value. Numeric literals are preserved exactly.');
    }
  };
  return <FieldView {...props} value={value} setValue={setValue} error={error} apply={apply} />;
}
function FieldView(
  props: SourceFieldProps & {
    readonly value: string;
    readonly setValue: (value: string) => void;
    readonly error: string | null;
    readonly apply: () => void;
  },
): ReactElement {
  return (
    <div className="form-field">
      <label>
        {props.label}
        <textarea
          value={props.value}
          disabled={props.disabled}
          rows={4}
          onChange={(event) => {
            props.setValue(event.target.value);
          }}
        />
      </label>
      {props.error !== null && <p role="alert">{props.error}</p>}
      <button disabled={props.disabled || props.value === props.raw} onClick={props.apply}>
        Apply {props.label}
      </button>
    </div>
  );
}
