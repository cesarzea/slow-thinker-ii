import type {ReactElement, ReactNode} from 'react';

export function EvidenceLink({
  identity,
  select,
  children,
}: {
  readonly identity: string | null;
  readonly select: (id: string) => void;
  readonly children: ReactNode;
}): ReactElement | null {
  if (identity === null) return null;
  return (
    <button
      onClick={() => {
        select(identity);
      }}
    >
      {children}
    </button>
  );
}
