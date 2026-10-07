import {useId, useState} from 'react';
import type {ReactElement} from 'react';
import {ControlLabel, described} from './form-controls.tsx';
import type {ControlProps} from './form-controls.tsx';

export interface NumberControlProps extends ControlProps {
  readonly value: number | undefined;
  readonly onValue: (value: number | undefined) => void;
  readonly minimum?: number;
  readonly maximum?: number;
  readonly integer?: boolean;
  readonly placeholder?: string;
  /** Decimal places; the arrows step by the smallest of them. */
  readonly decimals?: number;
  /** Shown before and after the value, for example `$` or `tokens`. */
  readonly prefix?: string;
  readonly suffix?: string;
}

type NumberInputProps = Omit<NumberControlProps, 'label' | 'help' | 'prefix' | 'suffix'> & {
  readonly id?: string;
  /** The accessible name when no visible label names the input. */
  readonly name?: string;
};

function step(props: NumberInputProps): string {
  if (props.decimals !== undefined) return String(10 ** -props.decimals);
  return props.integer === true ? '1' : 'any';
}

/** A number input that keeps partial input while typing and reports parsed numbers. */
export function NumberInput(props: NumberInputProps): ReactElement {
  const [text, setText] = useState(props.value === undefined ? '' : String(props.value));
  const shown = Number(text) === props.value || (text === '' && props.value === undefined);
  return (
    <input
      id={props.id}
      type="number"
      aria-label={props.name}
      value={shown ? text : String(props.value ?? '')}
      min={props.minimum}
      max={props.maximum}
      step={step(props)}
      disabled={props.disabled === true}
      placeholder={props.placeholder}
      aria-describedby={props.describedBy}
      onChange={(event) => {
        setText(event.target.value);
        props.onValue(event.target.value === '' ? undefined : Number(event.target.value));
      }}
    />
  );
}

function Affix({text}: {readonly text: string | undefined}): ReactElement | null {
  return text === undefined || text === '' ? null : <span className="affix">{text}</span>;
}

/** A labelled spin button, with the declared prefix and suffix around it. */
export function NumberControl(props: NumberControlProps): ReactElement {
  const id = useId();
  const {label, help, prefix, suffix, ...input} = props;
  const description = described(id, props);
  return (
    <div className="control">
      <ControlLabel label={label} {...(help === undefined ? {} : {help})} id={id} />
      <span className="number-input">
        <Affix text={prefix} />
        <NumberInput
          {...input}
          id={id}
          {...(description === undefined ? {} : {describedBy: description})}
        />
        <Affix text={suffix} />
      </span>
    </div>
  );
}
