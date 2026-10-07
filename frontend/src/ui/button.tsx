import type {ReactElement, ReactNode} from 'react';
import type {ComponentIcon} from '../api/index.ts';
import {Icon} from './icons.tsx';
import type {IconName} from './icons.tsx';

/** `default` is the outlined button; `accent` the soft accent one; `ghost` has no border. */
type ButtonVariant = 'default' | 'primary' | 'accent' | 'ghost' | 'danger';
interface Look {
  readonly variant?: ButtonVariant;
  readonly size?: 'md' | 'sm';
  readonly icon?: IconName;
}
export interface ButtonProps extends Look {
  readonly children?: ReactNode;
  readonly onClick: () => void;
  /** The accessible name, when it differs from the text. */
  readonly label?: string;
  /** A tooltip, for example why the button is disabled. */
  readonly title?: string;
  readonly disabled?: boolean;
  readonly describedBy?: string;
  readonly pressed?: boolean;
  readonly expanded?: boolean;
  readonly controls?: string;
}

function lookClass(look: Look): string {
  const size = look.size === 'sm' ? ' btn-sm' : '';
  return `btn btn-${look.variant ?? 'default'}${size}`;
}

/** A button of the design system, with an optional leading icon. */
export function Button(props: ButtonProps): ReactElement {
  return (
    <button
      type="button"
      className={lookClass(props)}
      disabled={props.disabled === true}
      aria-label={props.label}
      title={props.title}
      aria-describedby={props.describedBy}
      aria-pressed={props.pressed}
      aria-expanded={props.expanded}
      aria-controls={props.controls}
      onClick={props.onClick}
    >
      {props.icon !== undefined && <Icon name={props.icon} />}
      {props.children}
    </button>
  );
}

/** A square icon button; its name is also its tooltip. */
export function IconButton(props: {
  readonly icon: IconName;
  readonly label: string;
  readonly onClick: () => void;
  readonly disabled?: boolean;
  readonly size?: 'md' | 'sm';
  readonly tone?: 'muted' | 'danger';
}): ReactElement {
  const size = props.size === 'sm' ? ' icon-button-sm' : '';
  const tone = props.tone === 'danger' ? ' icon-button-danger' : '';
  return (
    <button
      type="button"
      className={`icon-button${size}${tone}`}
      aria-label={props.label}
      title={props.label}
      disabled={props.disabled === true}
      onClick={props.onClick}
    >
      <Icon name={props.icon} size={props.size === 'sm' ? 14 : 16} />
    </button>
  );
}

/** A link that looks like a button. */
export function ButtonLink(
  props: Look & {readonly href: string; readonly children: ReactNode; readonly title?: string},
): ReactElement {
  return (
    <a className={lookClass(props)} href={props.href} title={props.title}>
      {props.icon !== undefined && <Icon name={props.icon} />}
      {props.children}
    </a>
  );
}

const KINDS: Readonly<Record<ComponentIcon, readonly [IconName, string]>> = {
  trigger: ['trigger', 'trigger'],
  agent: ['llm', 'llm'],
  router: ['router', 'router'],
  output: ['output', 'output'],
  memory: ['memory', 'memory'],
  component: ['component', 'neutral'],
};

/** The coloured tile of a component kind, from its declared icon. */
export function KindTile(props: {
  readonly icon: ComponentIcon;
  readonly size?: 'md' | 'sm';
}): ReactElement {
  const [name, tone] = KINDS[props.icon];
  const small = props.size === 'sm';
  return (
    <span className={`tile tile-${tone}${small ? ' tile-sm' : ''}`} aria-hidden="true">
      <Icon name={name} size={small ? 13 : 16} />
    </span>
  );
}
