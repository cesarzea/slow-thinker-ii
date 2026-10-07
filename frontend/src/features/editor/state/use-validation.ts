import {useEffect} from 'react';
import type {Dispatch} from 'react';
import {errorMessage} from '../../../api/index.ts';
import type {OperatorClient} from '../../../api/index.ts';
import type {EditorAction, EditorState} from './editor-state.ts';

const VALIDATION_DELAY_MS = 300;

/** Validate the working copy through the API a moment after each change. */
export function useValidation(
  client: OperatorClient,
  state: EditorState,
  dispatch: Dispatch<EditorAction>,
  attempt: number,
): void {
  const {document, revision, checked} = state;
  useEffect(() => {
    if (checked === revision) return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      client.validate(document, controller.signal).then(
        (diagnostics) => {
          dispatch({type: 'checked', revision, diagnostics});
        },
        (error: unknown) => {
          if (!controller.signal.aborted)
            dispatch({type: 'check-failed', revision, message: errorMessage(error)});
        },
      );
    }, VALIDATION_DELAY_MS);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [client, document, revision, checked, dispatch, attempt]);
}
