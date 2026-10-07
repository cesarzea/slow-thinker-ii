import {useContext, useId, useRef, useState} from 'react';
import type {ReactElement, ReactNode, RefObject} from 'react';
import {Dialog, DialogContext} from './dialog.tsx';
import {descriptionIds, FieldHelp} from './field-help.tsx';

export interface ExpandableTextAreaProps {
  readonly label: string;
  readonly value: string;
  readonly onChange: (value: string) => void;
  readonly disabled?: boolean;
  readonly rows?: number;
  readonly placeholder?: string;
  readonly describedBy?: string;
  /** Shown under the label and read as the text area's description. */
  readonly help?: string;
}

/** A multi-line text field that can grow inline in dialogs, or open in a dialog elsewhere. */
export function ExpandableTextArea(props: ExpandableTextAreaProps): ReactElement {
  const inDialog = useContext(DialogContext);
  return inDialog ? <InlineTextArea {...props} /> : <ModalTextArea {...props} />;
}

function InlineTextArea(props: ExpandableTextAreaProps): ReactElement {
  const [expanded, expand] = useState(false);
  const focus = useRef<HTMLTextAreaElement>(null);
  return (
    <div className="expandable-text-area">
      <TextArea {...props} rows={expanded ? 18 : (props.rows ?? 5)} focus={focus}>
        <button
          type="button"
          className="expand-text"
          aria-label={`${expanded ? 'Collapse' : 'Expand'} ${props.label}`}
          aria-expanded={expanded}
          disabled={props.disabled}
          onClick={() => {
            expand(!expanded);
            focus.current?.focus();
          }}
        >
          {expanded ? '↙' : '↗'}
        </button>
      </TextArea>
    </div>
  );
}

function ModalTextArea(props: ExpandableTextAreaProps): ReactElement {
  const [expanded, expand] = useState(false);
  const focus = useRef<HTMLTextAreaElement>(null);
  const close = (): void => {
    expand(false);
  };
  return (
    <div className="expandable-text-area">
      <TextArea {...props}>
        <button
          type="button"
          className="expand-text"
          aria-label={`Expand ${props.label}`}
          disabled={props.disabled}
          onClick={() => {
            expand(true);
          }}
        >
          ↗
        </button>
      </TextArea>
      {expanded && (
        <Dialog title={props.label} initialFocusRef={focus} onClose={close}>
          <TextArea {...props} rows={18} focus={focus} />
        </Dialog>
      )}
    </div>
  );
}

type TextAreaProps = ExpandableTextAreaProps & {
  readonly focus?: RefObject<HTMLTextAreaElement | null>;
  readonly children?: ReactNode;
};

/** Label, help and the text area, with the expand button kept in the text area's corner. */
function TextArea({focus, children, ...props}: TextAreaProps): ReactElement {
  const id = useId();
  return (
    <>
      <label className="field-label" htmlFor={id}>
        {props.label}
      </label>
      <FieldHelp id={`${id}-help`} text={props.help} />
      <div className="text-area-box">
        <textarea
          id={id}
          ref={focus}
          value={props.value}
          rows={props.rows ?? 5}
          disabled={props.disabled}
          placeholder={props.placeholder}
          aria-describedby={descriptionIds(`${id}-help`, props.help, props.describedBy)}
          onChange={(event) => {
            props.onChange(event.target.value);
          }}
        />
        {children}
      </div>
    </>
  );
}
