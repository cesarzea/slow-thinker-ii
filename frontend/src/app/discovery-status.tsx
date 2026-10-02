import type {ReactElement} from 'react';
import type {useDiscovery} from '../features/workspace/index.tsx';
interface Props {
  readonly discovery: ReturnType<typeof useDiscovery>;
  readonly connected: boolean;
}
export function DiscoveryStatus({discovery, connected}: Props): ReactElement | null {
  if (!connected)
    return (
      <p className="notice">
        Viewer mode. Connect operator access to configure experiments, resources, runs and settings.
      </p>
    );
  return (
    <div className="discovery-status">
      <button disabled={discovery.loading} onClick={discovery.refresh}>
        Refresh configuration
      </button>
      {discovery.loading && <p role="status">Loading trusted configuration…</p>}
      {discovery.error !== null && <p role="alert">{discovery.error}</p>}
    </div>
  );
}
