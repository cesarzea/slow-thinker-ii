import type {ReactElement, ReactNode} from 'react';

export interface ActionButtonProps {
  readonly children: ReactNode;
  readonly action: () => unknown;
  readonly disabled?: boolean;
  readonly primary?: boolean;
  readonly label?: string;
  readonly describedBy?: string;
  readonly className?: string;
}

/** A button whose action may be asynchronous. */
export function ActionButton(props: ActionButtonProps): ReactElement {
  return (
    <button
      type="button"
      className={props.primary === true ? 'primary' : props.className}
      disabled={props.disabled === true}
      aria-label={props.label}
      aria-describedby={props.describedBy}
      onClick={() => {
        void props.action();
      }}
    >
      {props.children}
    </button>
  );
}

export interface PanelProps {
  readonly title: string;
  readonly children: ReactNode;
  readonly className?: string;
}

/** A titled region. */
export function Panel(props: PanelProps): ReactElement {
  return (
    <section className={props.className ?? 'panel'} aria-label={props.title}>
      <h2>{props.title}</h2>
      {props.children}
    </section>
  );
}
