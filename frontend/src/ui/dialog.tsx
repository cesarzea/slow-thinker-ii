import {createContext, useEffect, useId, useRef} from 'react';
import type {ReactElement, ReactNode, RefObject} from 'react';
import {IconButton} from './button.tsx';
import {dialogKey, focusable} from './dialog-focus.ts';

export const DialogContext = createContext(false);

export interface DialogProps {
  readonly title: string;
  readonly children: ReactNode;
  readonly onClose: () => void;
  readonly subtitle?: string;
  /** Shown before the title, for example a component's tile. */
  readonly icon?: ReactNode;
  readonly initialFocusRef?: RefObject<HTMLElement | null>;
  readonly closeDisabled?: boolean;
  readonly wide?: boolean;
  /**
   * A fixed size and place: anchored near the top and centred horizontally, whatever its
   * content, so that switching what it shows never moves or resizes it.
   */
  readonly fixed?: boolean;
}

function panelClass(props: DialogProps): string {
  const wide = props.wide === true ? ' dialog-wide' : '';
  const fixed = props.fixed === true ? ' dialog-fixed' : '';
  return `dialog${wide}${fixed}`;
}

/** A modal dialog named by its title, with focus kept inside until it closes. */
export function Dialog(props: DialogProps): ReactElement {
  const title = useId();
  const panel = useRef<HTMLDivElement>(null);
  useDialogFocus(panel, props.initialFocusRef);
  return (
    <DialogContext value={true}>
      <div className={props.fixed === true ? 'dialog-backdrop anchored' : 'dialog-backdrop'}>
        <div
          className={panelClass(props)}
          ref={panel}
          role="dialog"
          aria-modal="true"
          aria-labelledby={title}
          tabIndex={-1}
          onKeyDown={(event) => {
            dialogKey(event, panel.current, () => {
              if (props.closeDisabled !== true) props.onClose();
            });
          }}
        >
          <DialogHeading {...props} id={title} />
          {props.children}
        </div>
      </div>
    </DialogContext>
  );
}

function useDialogFocus(
  panel: RefObject<HTMLElement | null>,
  initialFocus: DialogProps['initialFocusRef'],
): void {
  useEffect(() => {
    const previous = document.activeElement;
    const target = initialFocus?.current ?? focusable(panel.current)[0] ?? panel.current;
    target?.focus();
    return () => {
      if (previous instanceof HTMLElement && previous.isConnected) previous.focus();
    };
  }, [panel, initialFocus]);
}

function DialogHeading(props: DialogProps & {readonly id: string}): ReactElement {
  return (
    <div className="dialog-heading">
      {props.icon}
      <div className="dialog-titles">
        <h2 id={props.id}>{props.title}</h2>
        {props.subtitle !== undefined && <p className="dialog-subtitle">{props.subtitle}</p>}
      </div>
      <IconButton
        icon="close"
        label={`Close ${props.title}`}
        disabled={props.closeDisabled === true}
        onClick={props.onClose}
      />
    </div>
  );
}
