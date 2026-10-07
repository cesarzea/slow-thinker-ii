import {useCallback, useRef, useState} from 'react';
import type {ReactElement} from 'react';
import type {DraftModel} from '../features/editor/index.ts';
import {ActionButton, Dialog} from '../ui/index.ts';

interface Guard {
  readonly register: (model: DraftModel | null) => void;
  readonly request: (action: () => void) => void;
  readonly dialog: ReactElement | null;
}

/** Asks to save, discard or stay before leaving an editor with unsaved changes. */
export function useDraftGuard(): Guard {
  const model = useRef<DraftModel | null>(null);
  const [pending, setPending] = useState<(() => void) | null>(null);
  const register = useCallback((next: DraftModel | null) => {
    model.current = next;
  }, []);
  const request = useCallback((action: () => void) => {
    if (model.current?.dirty === true) setPending(() => action);
    else action();
  }, []);
  const close = (): void => {
    setPending(null);
  };
  const dialog =
    pending === null ? null : <GuardDialog model={model} action={pending} close={close} />;
  return {register, request, dialog};
}

interface DialogProps {
  readonly model: {readonly current: DraftModel | null};
  readonly action: () => void;
  readonly close: () => void;
}

function useGuardActions(props: DialogProps): {
  problem: string | null;
  save: () => Promise<void>;
  discard: () => void;
} {
  const [problem, setProblem] = useState<string | null>(null);
  const finish = (): void => {
    props.close();
    props.action();
  };
  const save = async (): Promise<void> => {
    const result = await props.model.current?.save();
    if (result === 'failed')
      setProblem('The graph was not saved. Its problems are shown in the editor.');
    else finish();
  };
  const discard = (): void => {
    props.model.current?.discard();
    finish();
  };
  return {problem, save, discard};
}

function GuardDialog(props: DialogProps): ReactElement {
  const {problem, save, discard} = useGuardActions(props);
  return (
    <Dialog title="Unsaved changes" onClose={props.close}>
      <p>This graph has changes that are not saved.</p>
      {problem !== null && <p role="alert">{problem}</p>}
      <div className="dialog-actions">
        <ActionButton action={save} primary>
          Save
        </ActionButton>
        <ActionButton action={discard}>Discard</ActionButton>
        <ActionButton action={props.close}>Stay</ActionButton>
      </div>
    </Dialog>
  );
}
