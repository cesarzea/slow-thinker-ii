import type {ReactElement} from 'react';
import {ActionButton} from '../../ui/index.ts';

export function ReadStatus({
  error,
  loading,
  refresh,
}: {
  readonly error: string | null;
  readonly loading: boolean;
  readonly refresh: () => void;
}): ReactElement {
  return (
    <div className="actions">
      {error !== null && <p role="alert">{error}</p>}
      {loading && <p role="status">Loading evidence…</p>}
      <button disabled={loading} onClick={refresh}>
        Refresh evidence
      </button>
    </div>
  );
}

interface PageProps {
  readonly next: string | null;
  readonly cursor: string | undefined;
  readonly onPage: (cursor: string | undefined) => void;
}

export function TracePages({next, onPage, cursor}: PageProps): ReactElement {
  return (
    <div className="actions">
      {cursor !== undefined && (
        <ActionButton
          action={() => {
            onPage(undefined);
          }}
        >
          Back to the beginning
        </ActionButton>
      )}
      {next !== null && (
        <ActionButton
          action={() => {
            onPage(next);
          }}
        >
          Next page
        </ActionButton>
      )}
    </div>
  );
}
