import type {ReactElement} from 'react';
import type {ExecutionStore} from './state.ts';

interface Props {
  readonly kind: 'workspace' | 'history';
  readonly current: string | undefined;
  readonly next: string | null;
  readonly store: ExecutionStore;
}

export function PageControls({kind, current, next, store}: Props): ReactElement {
  const label = kind === 'workspace' ? 'sesiones' : 'ejecuciones';
  return (
    <div className="actions">
      {current !== undefined && (
        <button
          onClick={() => {
            store.page(kind, undefined);
          }}
        >
          Primeras {label}
        </button>
      )}
      {next !== null && (
        <button
          onClick={() => {
            store.page(kind, next);
          }}
        >
          Más {label}
        </button>
      )}
    </div>
  );
}
