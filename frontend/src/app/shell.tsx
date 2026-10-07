import {useEffect, useState} from 'react';
import type {ReactElement, ReactNode} from 'react';
import type {OperatorClient, Usage} from '../api/index.ts';
import {ActionButton, moneyLabel} from '../ui/index.ts';
import {GRAPHS, routeHash} from './routes.ts';
import type {Section} from './routes.ts';
import {spentLabel} from './spending.ts';

const USAGE_INTERVAL_MS = 30_000;
const SECTIONS: readonly (readonly [Section, string, string])[] = [
  ['graphs', 'Graphs', routeHash(GRAPHS)],
  ['runs', 'Runs', routeHash({kind: 'runs', graphId: null})],
  ['components', 'Components', routeHash({kind: 'components'})],
];

/** The day's and month's spending, read now and every 30 seconds. */
function useUsage(client: OperatorClient): Usage | null | undefined {
  const [usage, setUsage] = useState<Usage | null | undefined>(undefined);
  useEffect(() => {
    const controller = new AbortController();
    const read = (): void => {
      client.usage(controller.signal).then(setUsage, () => {
        setUsage(null);
      });
    };
    read();
    const timer = window.setInterval(read, USAGE_INTERVAL_MS);
    return () => {
      controller.abort();
      window.clearInterval(timer);
    };
  }, [client]);
  return usage;
}

function Spent(props: {readonly label: string; readonly scope: Usage['day']}): ReactElement {
  return (
    <span>
      {`${props.label} `}
      <b>{spentLabel(props.scope.used_usd)}</b>
      {` of ${moneyLabel(props.scope.limit_usd)}`}
    </span>
  );
}

function UsageText({usage}: {readonly usage: Usage | null | undefined}): ReactElement {
  if (usage === undefined) return <p className="usage" />;
  if (usage === null) return <p className="usage">Spending unavailable</p>;
  return (
    <p className="usage">
      <Spent label="Today" scope={usage.day} />
      <Spent label="This month" scope={usage.month} />
    </p>
  );
}

function MainNavigation({section}: {readonly section: Section}): ReactElement {
  return (
    <nav className="main-navigation" aria-label="Main">
      {SECTIONS.map(([id, label, href]) => (
        <a key={id} href={href} aria-current={id === section ? 'page' : undefined}>
          {label}
        </a>
      ))}
    </nav>
  );
}

/** The product shell: name, navigation, spending against the budgets, Disconnect. */
export function Shell(props: {
  readonly client: OperatorClient;
  readonly section: Section;
  /** `null` without operator authentication: there is nothing to disconnect. */
  readonly onDisconnect: (() => void) | null;
  readonly children: ReactNode;
}): ReactElement {
  const usage = useUsage(props.client);
  return (
    <div className="app-shell">
      <header className="shell-header">
        <span className="brand">
          <b aria-hidden="true">ST</b>
          Slow Thinker II
        </span>
        <MainNavigation section={props.section} />
        <UsageText usage={usage} />
        {props.onDisconnect !== null && (
          <ActionButton action={props.onDisconnect}>Disconnect</ActionButton>
        )}
      </header>
      <main className="shell-main">{props.children}</main>
    </div>
  );
}
