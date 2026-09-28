import type {ReactElement, ReactNode} from 'react';

interface Props {
  readonly children: ReactNode;
  readonly action: () => void | Promise<void>;
  readonly disabled?: boolean;
}

export function ActionButton({children, action, disabled = false}: Props): ReactElement {
  return (
    <button
      disabled={disabled}
      onClick={() => {
        void action();
      }}
    >
      {children}
    </button>
  );
}
