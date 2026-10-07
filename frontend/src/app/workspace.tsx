import {useMemo} from 'react';
import type {ReactElement} from 'react';
import {OperatorClient} from '../api/index.ts';
import {useDraftGuard} from './draft-guard.tsx';
import {Pages} from './pages.tsx';
import {routeSection} from './routes.ts';
import {Shell} from './shell.tsx';
import {useRoute} from './use-route.ts';

interface WorkspaceProps {
  /** `null` on a server without operator authentication. */
  readonly credential: string | null;
  /** `null` hides Disconnect. */
  readonly onDisconnect: (() => void) | null;
}

/** An action that first passes the unsaved-changes guard, or `null` without an action. */
function guarded(
  action: (() => void) | null,
  request: (action: () => void) => void,
): (() => void) | null {
  return action === null
    ? null
    : () => {
        request(action);
      };
}

/** The connected product: shell, pages, the run dialog and the unsaved-changes guard. */
export function Workspace(props: WorkspaceProps): ReactElement {
  const client = useMemo(() => new OperatorClient(props.credential), [props.credential]);
  const guard = useDraftGuard();
  const {route, navigate} = useRoute(guard.request);
  const pages = {client, route, navigate};
  const disconnect = guarded(props.onDisconnect, guard.request);
  return (
    <Shell client={client} section={routeSection(route)} onDisconnect={disconnect}>
      <Pages {...pages} onDraft={guard.register} />
      {guard.dialog}
    </Shell>
  );
}
