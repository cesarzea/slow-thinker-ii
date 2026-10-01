import {useEffect, useReducer} from 'react';

import type {InspectionSelection} from './types.ts';

type Evidence = 'call' | 'payload' | 'activation';
interface Selection {
  readonly call: string | undefined;
  readonly payload: string | undefined;
  readonly activation: string | undefined;
  readonly focused: Evidence | undefined;
  readonly revision: number;
}
const initial: Selection = {
  call: undefined,
  payload: undefined,
  activation: undefined,
  focused: undefined,
  revision: 0,
};

function select(previous: Selection, action: {kind: Evidence; id: string}): Selection {
  const next = {...previous, focused: action.kind, revision: previous.revision + 1};
  if (action.kind === 'activation') {
    return {...next, activation: action.id, call: undefined, payload: undefined};
  }
  if (action.kind === 'call') return {...next, call: action.id, payload: undefined};
  return {...next, payload: action.id};
}

export function useSelection(external?: InspectionSelection): Selection & {
  readonly onCall: (id: string) => void;
  readonly onPayload: (id: string) => void;
  readonly onActivation: (id: string) => void;
} {
  const [state, dispatch] = useReducer(select, initial);
  useEffect(() => {
    if (external !== undefined) dispatch(external);
  }, [external]);
  return {
    ...state,
    onCall: (id) => {
      dispatch({kind: 'call', id});
    },
    onPayload: (id) => {
      dispatch({kind: 'payload', id});
    },
    onActivation: (id) => {
      dispatch({kind: 'activation', id});
    },
  };
}
