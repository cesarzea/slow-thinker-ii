import {useState} from 'react';
import type {ReactElement, ReactNode} from 'react';
import {Dialog} from './dialog.tsx';
import type {DialogProps} from './dialog.tsx';

export interface ConfigurationDialogProps {
  readonly title: string;
  readonly subtitle?: string;
  readonly description?: string;
  readonly error?: string | null;
  readonly wide?: boolean;
  /** A fixed size and place; see `Dialog`. */
  readonly fixed?: boolean;
  /** Further actions shown at the start of the footer, before Cancel and Apply. */
  readonly actions?: ReactNode;
  /** Shown before the title, for example a component's tile. */
  readonly icon?: ReactNode;
  /** A short note in the footer, before Cancel and Apply. */
  readonly note?: string;
  readonly onApply: () => void | Promise<void>;
  readonly onCancel: () => void;
  readonly children: ReactNode;
}

function useApply(onApply: ConfigurationDialogProps['onApply']): {
  applying: boolean;
  failure: string | null;
  apply: () => Promise<void>;
} {
  const [applying, setApplying] = useState(false);
  const [failure, setFailure] = useState<string | null>(null);
  const apply = async (): Promise<void> => {
    setApplying(true);
    setFailure(null);
    try {
      await onApply();
    } catch {
      setFailure('Could not apply the changes. Review the fields and try again.');
    } finally {
      setApplying(false);
    }
  };
  return {applying, failure, apply};
}

/** A dialog whose changes take effect only when Apply succeeds; Cancel discards them. */
export function ConfigurationDialog(props: ConfigurationDialogProps): ReactElement {
  const {applying, failure, apply} = useApply(props.onApply);
  const error = props.error ?? failure;
  return (
    <Dialog {...dialogProps(props)} closeDisabled={applying}>
      {props.description !== undefined && <p className="dialog-description">{props.description}</p>}
      <fieldset className="dialog-fields" disabled={applying} aria-busy={applying}>
        {props.children}
      </fieldset>
      {error !== null && <p role="alert">{error}</p>}
      <DialogActions {...props} pending={applying} onApply={apply} />
    </Dialog>
  );
}

function dialogProps(props: ConfigurationDialogProps): Omit<DialogProps, 'children'> {
  const {title, subtitle, wide, fixed, icon} = props;
  return {
    title,
    onClose: props.onCancel,
    ...(subtitle === undefined ? {} : {subtitle}),
    ...(wide === undefined ? {} : {wide}),
    ...(fixed === undefined ? {} : {fixed}),
    ...(icon === undefined ? {} : {icon}),
  };
}

function DialogActions(props: {
  readonly pending: boolean;
  readonly actions?: ReactNode;
  readonly note?: string;
  readonly onApply: () => Promise<void>;
  readonly onCancel: () => void;
}): ReactElement {
  return (
    <div className="dialog-actions">
      <div className="dialog-actions-start">{props.actions}</div>
      {props.note !== undefined && <span className="dialog-note">{props.note}</span>}
      <button type="button" disabled={props.pending} onClick={props.onCancel}>
        Cancel
      </button>
      <button
        type="button"
        className="primary"
        disabled={props.pending}
        onClick={() => {
          void props.onApply();
        }}
      >
        Apply
      </button>
    </div>
  );
}
