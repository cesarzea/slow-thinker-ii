import {useState} from 'react';

interface Selection {
  readonly call: string | undefined;
  readonly payload: string | undefined;
  readonly activation: string | undefined;
}

export function useSelection(): Selection & {
  readonly onCall: (id: string) => void;
  readonly onPayload: (id: string) => void;
  readonly onActivation: (id: string) => void;
} {
  const [state, setState] = useState<Selection>({
    call: undefined,
    payload: undefined,
    activation: undefined,
  });
  return {
    ...state,
    onCall: (call) => {
      setState((previous) => ({...previous, call, payload: undefined}));
    },
    onPayload: (payload) => {
      setState((previous) => ({...previous, payload}));
    },
    onActivation: (activation) => {
      setState({activation, call: undefined, payload: undefined});
    },
  };
}
