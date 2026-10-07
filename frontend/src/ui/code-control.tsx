import {useId} from 'react';
import type {ReactElement, UIEvent} from 'react';
import {descriptionIds, FieldHelp} from './field-help.tsx';

export interface CodeControlProps {
  readonly label: string;
  readonly value: string;
  readonly onChange: (value: string) => void;
  readonly disabled?: boolean;
  readonly describedBy?: string;
  readonly help?: string;
  readonly placeholder?: string;
  readonly language?: string;
}

/** Keep the line numbers beside the lines they number while the code scrolls. */
function followScroll(event: UIEvent<HTMLTextAreaElement>): void {
  const gutter = event.currentTarget.previousElementSibling;
  if (gutter instanceof HTMLElement) gutter.scrollTop = event.currentTarget.scrollTop;
}

function CodeGutter({value}: {readonly value: string}): ReactElement {
  const lines = Array.from({length: value.split('\n').length}, (_, index) => index + 1);
  return (
    <pre className="code-gutter" aria-hidden="true">
      {lines.join('\n')}
    </pre>
  );
}

/** A monospaced editor with line numbers; lines do not wrap, so numbers stay aligned. */
export function CodeControl(props: CodeControlProps): ReactElement {
  const id = useId();
  return (
    <div className="control code-control">
      <label htmlFor={id}>{props.label}</label>
      <FieldHelp id={`${id}-help`} text={props.help} />
      <div className="code-editor">
        <CodeGutter value={props.value} />
        <textarea
          id={id}
          className="code"
          spellCheck={false}
          wrap="off"
          rows={16}
          value={props.value}
          disabled={props.disabled === true}
          placeholder={props.placeholder}
          aria-describedby={descriptionIds(`${id}-help`, props.help, props.describedBy)}
          data-language={props.language}
          onScroll={followScroll}
          onChange={(event) => {
            props.onChange(event.target.value);
          }}
        />
      </div>
    </div>
  );
}
