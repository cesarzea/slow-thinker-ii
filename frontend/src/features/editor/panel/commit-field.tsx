import {useId, useState} from 'react';
import type {KeyboardEvent, ReactElement} from 'react';

export interface CommitFieldProps {
  readonly label: string;
  readonly value: string;
  readonly type: 'text' | 'number';
  /** The problem with the text, or null when it can be committed. */
  readonly check: (text: string) => string | null;
  readonly onCommit: (text: string) => void;
  /** The label above the field rather than beside it. */
  readonly wide?: boolean;
}

function useCommit(props: CommitFieldProps): {
  text: string;
  setText: (text: string) => void;
  problem: string | null;
  commit: () => void;
  key: (event: KeyboardEvent<HTMLInputElement>) => void;
} {
  const [text, setText] = useState(props.value);
  const [problem, setProblem] = useState<string | null>(null);
  const commit = (): void => {
    const found = props.check(text);
    setProblem(found);
    if (found === null && text.trim() !== props.value) props.onCommit(text.trim());
  };
  const key = (event: KeyboardEvent<HTMLInputElement>): void => {
    if (event.key === 'Enter') commit();
    if (event.key !== 'Escape') return;
    setText(props.value);
    setProblem(null);
  };
  return {text, setText, problem, commit, key};
}

/**
 * A field that commits its text on Enter or when it loses focus, when the text is valid;
 * Escape restores the committed value. Problems show under the field.
 */
export function CommitField(props: CommitFieldProps): ReactElement {
  const id = useId();
  const {text, setText, problem, commit, key} = useCommit(props);
  return (
    <div className={props.wide === true ? 'commit-field wide' : 'commit-field'}>
      <label htmlFor={id}>{props.label}</label>
      <input
        id={id}
        type={props.type}
        value={text}
        aria-invalid={problem !== null}
        aria-describedby={problem === null ? undefined : `${id}-problem`}
        onChange={(event) => {
          setText(event.target.value);
        }}
        onBlur={commit}
        onKeyDown={key}
      />
      {problem !== null && (
        <p id={`${id}-problem`} className="field-problem">
          {problem}
        </p>
      )}
    </div>
  );
}
